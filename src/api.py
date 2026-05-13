from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import deque

from hotspot_rule import hotspot_zone

BASE = Path(__file__).resolve().parents[1]
MODELS = BASE / "models"

fish_model = joblib.load(MODELS / "fish_presence_model.pkl")
weather_model = joblib.load(MODELS / "weather_alert_model.pkl")

WEATHER_FEATURES = list(weather_model.feature_names_in_)

app = FastAPI(title="Smart Marine API")


# =========================
# LIVE BOAT LOCATION STORAGE
# =========================
boat_location = {
    "lat": 0.0,
    "lon": 0.0,
    "updated_at": None
}

boat_history = deque(maxlen=100)


# =========================
# SOS / ALERT STORAGE
# =========================
boat_sos = {
    "active": False,
    "lat": 0.0,
    "lon": 0.0,
    "reason": None,
    "created_at": None,
    "boat_id": "BOAT_1"
}


# =========================
# SENSOR TELEMETRY STORAGE
# =========================
sensor_latest = {
    "TEMP": None,
    "WDSP": None,
    "DEWP": None,
    "SLP": None,
    "STP": None,
    "VISIB": None,
    "MXSPD": None,
    "MAX": None,
    "MIN": None,
    "SNDP": None,
    "SST": None,
    "lat": None,
    "lon": None,
    "updated_at": None,
    "boat_id": "BOAT_1"
}


# ---------- Inputs ----------
class FishInput(BaseModel):
    features: list[float]


class WeatherInput(BaseModel):
    TEMP: float
    DEWP: float | None = None
    SLP: float | None = None
    STP: float | None = None
    VISIB: float | None = None
    WDSP: float = 0.0
    MXSPD: float | None = None
    MAX: float | None = None
    MIN: float | None = None
    SNDP: float | None = None


class MarineInput(BaseModel):
    TEMP: float
    DEWP: float | None = None
    SLP: float | None = None
    STP: float | None = None
    VISIB: float | None = None
    WDSP: float = 0.0
    MXSPD: float | None = None
    MAX: float | None = None
    MIN: float | None = None
    SNDP: float | None = None

    SST: float = 26.0
    lat: float = 0.0
    lon: float = 0.0


class GPSInput(BaseModel):
    lat: float
    lon: float
    boat_id: str | None = "BOAT_1"


class SOSInput(BaseModel):
    lat: float
    lon: float
    reason: str | None = "SOS"
    boat_id: str | None = "BOAT_1"


class SensorInput(BaseModel):
    TEMP: float | None = None
    WDSP: float | None = None
    DEWP: float | None = None
    SLP: float | None = None
    STP: float | None = None
    VISIB: float | None = None
    MXSPD: float | None = None
    MAX: float | None = None
    MIN: float | None = None
    SNDP: float | None = None
    SST: float | None = None
    lat: float | None = None
    lon: float | None = None
    boat_id: str | None = "BOAT_1"


# ---------- Helpers ----------
def make_weather_df(payload_dict: dict) -> pd.DataFrame:
    df = pd.DataFrame([payload_dict]).fillna(0)
    df = df.reindex(columns=WEATHER_FEATURES, fill_value=0)
    return df


# ---------- Routes ----------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Smart Marine API running",
        "weather_features_expected": WEATHER_FEATURES,
        "live_tracking": {
            "post_location": "/boat/location",
            "get_location": "/boat/location",
            "get_history": "/boat/location/history"
        },
        "sos": {
            "trigger": "/boat/sos",
            "status": "/boat/sos",
            "clear": "/boat/sos/clear"
        },
        "sensors": {
            "post_sensors": "/sensors",
            "get_latest": "/sensors/latest"
        }
    }


@app.post("/sensors")
def update_sensors(inp: SensorInput):
    now = datetime.utcnow().isoformat() + "Z"
    data = inp.model_dump()

    for k in sensor_latest.keys():
        if k in data and data[k] is not None:
            sensor_latest[k] = data[k]

    sensor_latest["updated_at"] = now
    sensor_latest["boat_id"] = inp.boat_id or "BOAT_1"

    if sensor_latest.get("lat") is not None and sensor_latest.get("lon") is not None:
        boat_location["lat"] = float(sensor_latest["lat"])
        boat_location["lon"] = float(sensor_latest["lon"])
        boat_location["updated_at"] = now

        boat_history.append({
            "lat": boat_location["lat"],
            "lon": boat_location["lon"],
            "updated_at": now,
            "boat_id": sensor_latest["boat_id"]
        })

    return {"status": "updated", "sensor_latest": sensor_latest}


@app.get("/sensors/latest")
def get_latest_sensors():
    return sensor_latest


@app.post("/boat/location")
def update_boat_location(inp: GPSInput):
    now = datetime.utcnow().isoformat() + "Z"
    boat_location["lat"] = float(inp.lat)
    boat_location["lon"] = float(inp.lon)
    boat_location["updated_at"] = now

    boat_history.append({
        "lat": boat_location["lat"],
        "lon": boat_location["lon"],
        "updated_at": now,
        "boat_id": inp.boat_id or "BOAT_1"
    })

    return {"status": "updated", "boat_location": boat_location}


@app.get("/boat/location")
def get_boat_location():
    return boat_location


@app.get("/boat/location/history")
def get_boat_history(limit: int = 30):
    limit = max(1, min(int(limit), 100))
    data = list(boat_history)[-limit:]
    return {"count": len(data), "history": data}


@app.post("/boat/sos")
def trigger_sos(inp: SOSInput):
    now = datetime.utcnow().isoformat() + "Z"
    boat_sos["active"] = True
    boat_sos["lat"] = float(inp.lat)
    boat_sos["lon"] = float(inp.lon)
    boat_sos["reason"] = inp.reason or "SOS"
    boat_sos["created_at"] = now
    boat_sos["boat_id"] = inp.boat_id or "BOAT_1"
    return {"status": "sos_triggered", "sos": boat_sos}


@app.get("/boat/sos")
def get_sos():
    return boat_sos


@app.post("/boat/sos/clear")
def clear_sos():
    boat_sos["active"] = False
    boat_sos["reason"] = None
    boat_sos["created_at"] = None
    return {"status": "cleared", "sos": boat_sos}


@app.post("/predict/fish")
def predict_fish(inp: FishInput):
    if len(inp.features) != 60:
        return {"error": "Expected 60 sonar features"}

    X = pd.DataFrame([inp.features])
    pred = fish_model.predict(X)[0]
    proba = float(fish_model.predict_proba(X).max())
    return {"prediction": str(pred), "confidence": proba}


@app.post("/predict/weather")
def predict_weather(inp: WeatherInput):
    wdf = make_weather_df(inp.model_dump())
    pred = int(weather_model.predict(wdf)[0])
    proba = float(weather_model.predict_proba(wdf).max())
    return {"weather_alert": pred, "confidence": proba}


@app.post("/predict/all")
def predict_all(inp: MarineInput):
    data = inp.model_dump()

    wdf = make_weather_df(data)
    w_pred = int(weather_model.predict(wdf)[0])
    w_conf = float(weather_model.predict_proba(wdf).max())

    zone = hotspot_zone(float(data.get("SST", 26.0)))
    gps = {"lat": float(data.get("lat", 0.0)), "lon": float(data.get("lon", 0.0))}

    if w_pred == 1 and not (gps["lat"] == 0.0 and gps["lon"] == 0.0):
        now = datetime.utcnow().isoformat() + "Z"
        boat_sos["active"] = True
        boat_sos["lat"] = gps["lat"]
        boat_sos["lon"] = gps["lon"]
        boat_sos["reason"] = "AUTO: Unsafe weather predicted"
        boat_sos["created_at"] = now
        boat_sos["boat_id"] = "BOAT_1"

    return {
        "gps": gps,
        "weather_alert": w_pred,
        "weather_confidence": w_conf,
        "hotspot_zone": zone,
        "sos": boat_sos
    }