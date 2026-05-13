#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPSPlus.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* apiUrl = "http://YOUR_LAPTOP_IP:8000/sensors";

#define ONE_WIRE_BUS 4
#define TRIG_PIN 5
#define ECHO_PIN 18
#define LED_PIN 2
#define BUZZER_PIN 15

#define GPS_RX 16
#define GPS_TX 17

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);
Adafruit_BMP280 bmp;
TinyGPSPlus gps;

unsigned long lastSend = 0;
const unsigned long interval = 5000;

void connectWiFi() {
  Serial.print("Connecting WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());
}

float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return -1;
  return duration * 0.0343 / 2.0;
}

void updateGPS() {
  while (Serial2.available() > 0) {
    gps.encode(Serial2.read());
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  ds18b20.begin();
  Wire.begin(21, 22);

  if (!bmp.begin(0x76)) {
    bmp.begin(0x77);
  }

  Serial2.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);

  connectWiFi();
}

void loop() {
  updateGPS();

  if (millis() - lastSend >= interval) {
    lastSend = millis();

    ds18b20.requestTemperatures();
    float tempC = ds18b20.getTempCByIndex(0);

    float pressureHpa = -1;
    if (bmp.begin(0x76) || bmp.begin(0x77)) {
      pressureHpa = bmp.readPressure() / 100.0F;
    }

    float distanceCm = readDistanceCM();

    double lat = gps.location.isValid() ? gps.location.lat() : 0.0;
    double lon = gps.location.isValid() ? gps.location.lng() : 0.0;

    bool danger = false;
    if (tempC > 35.0) danger = true;
    if (pressureHpa > 0 && pressureHpa < 1000.0) danger = true;
    if (distanceCm > 0 && distanceCm < 20.0) danger = true;

    digitalWrite(LED_PIN, danger ? HIGH : LOW);
    digitalWrite(BUZZER_PIN, danger ? HIGH : LOW);

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(apiUrl);
      http.addHeader("Content-Type", "application/json");

      StaticJsonDocument<512> doc;
      doc["TEMP"] = tempC;
      doc["WDSP"] = 3.0;
      doc["DEWP"] = tempC - 2;
      doc["SLP"] = pressureHpa;
      doc["STP"] = pressureHpa;
      doc["VISIB"] = 8.0;
      doc["MXSPD"] = 5.0;
      doc["MAX"] = tempC + 1;
      doc["MIN"] = tempC - 1;
      doc["SNDP"] = 0.0;
      doc["SST"] = tempC;
      doc["lat"] = lat;
      doc["lon"] = lon;
      doc["boat_id"] = "BOAT_1";

      String payload;
      serializeJson(doc, payload);

      Serial.println("Sending:");
      Serial.println(payload);

      int responseCode = http.POST(payload);
      Serial.print("Response code: ");
      Serial.println(responseCode);

      if (responseCode > 0) {
        String response = http.getString();
        Serial.println(response);
      }

      http.end();
    } else {
      connectWiFi();
    }
  }
}