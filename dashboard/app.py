# dashboard/app.py  (FINAL + Live Sensor Mode + 5s Auto Update + Top Nav + Sidebar Nav)

import streamlit as st
import requests
import random

from authentication import signup, login
from streamlit_autorefresh import st_autorefresh

# Optional theme
try:
    from ui_theme import inject_theme, topbar, hero, banner
    THEME_OK = True
except Exception:
    THEME_OK = False


st.set_page_config(
    page_title="WaveSense",
    layout="wide",
    page_icon="🌊",
)

if THEME_OK:
    inject_theme()

# -------------------------
# SESSION DEFAULTS
# -------------------------
if "authed" not in st.session_state:
    st.session_state.authed = False

if "user" not in st.session_state:
    st.session_state.user = None


# -------------------------
# HEADER
# -------------------------
if THEME_OK:
    topbar(st.session_state.user.get("name") if st.session_state.authed and st.session_state.user else None)
    hero("🌊 WaveSense", "Safety • Hotspots • Tracking • Detection (ML + FastAPI)")
else:
    st.title("🌊 Sense")


# -------------------------
# LOGIN / SIGNUP
# -------------------------
if not st.session_state.authed:

    st.subheader("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")

        if st.button("Login", width="stretch"):
            ok, msg, user = login(phone, password)
            if ok:
                st.session_state.authed = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        st.caption("Password rule: 6–128 characters")
        name = st.text_input("Full Name")
        phone2 = st.text_input("Phone Number", key="phone2")
        password2 = st.text_input("Create Password", type="password", key="pw2")

        if st.button("Create Account", width="stretch"):
            ok, msg = signup(name, phone2, password2)
            if ok:
                st.success(msg)
                st.info("Now login using Phone + Password.")
            else:
                st.error(msg)

    st.stop()


# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.markdown("## 🌊 WaveSense")
st.sidebar.caption("Ocean Monitoring Command Center")

API_BASE = st.sidebar.text_input("API URL", value=st.session_state.get("API_BASE", "https://wave-sense.onrender.com"))
st.session_state["API_BASE"] = API_BASE

st.sidebar.write("Start API:")
st.sidebar.code("uvicorn src.api:app --reload")


def api_is_alive():
    try:
        r = requests.get(f"{API_BASE}/", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


alive = api_is_alive()

if alive:
    st.sidebar.success("✅ API Connected")
else:
    st.sidebar.error("❌ API Not Running")


# Navigation
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
st.sidebar.page_link("pages/home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/weather.py", label="Weather", icon="🌦️")
st.sidebar.page_link("pages/hotspot.py", label="Hotspot", icon="🎯")
st.sidebar.page_link("pages/fish.py", label="Fish Detection", icon="🐟")
st.sidebar.page_link("pages/tracking.py", label="Boat Tracking", icon="📍")

st.sidebar.markdown("---")
user_name = st.session_state.user.get("name", "User")
st.sidebar.info(f"Logged in as **{user_name}**")

if st.sidebar.button("Logout"):
    st.session_state.authed = False
    st.session_state.user = None
    st.rerun()


# -------------------------
# TOP NAV (Always visible)
# -------------------------
st.markdown("### 🧭 Navigation")
c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 1, 1])

with c1:
    st.page_link("pages/home.py", label="Home", icon="🏠")
with c2:
    st.page_link("pages/weather.py", label="Weather", icon="🌦️")
with c3:
    st.page_link("pages/hotspot.py", label="Hotspot", icon="🎯")
with c4:
    st.page_link("pages/fish.py", label="Fish", icon="🐟")
with c5:
    st.page_link("pages/tracking.py", label="Tracking", icon="📍")
with c6:
    if st.button("🚪 Logout", width="stretch"):
        st.session_state.authed = False
        st.session_state.user = None
        st.rerun()


# -------------------------
# LIVE SENSOR MODE + AUTO UPDATE
# -------------------------
st.markdown("---")
st.subheader("⚡ Quick Prediction")

live_mode = st.toggle("📡 Live Sensor Mode (Auto update every 5 seconds)", value=True, disabled=not alive)

# Auto refresh ONLY when live mode is enabled
if live_mode:
    st.caption("🔄 Live mode ON: reading /sensors/latest every 5 seconds")
    st_autorefresh(interval=5000, key="global_live_refresh")


def get_latest_sensors():
    try:
        r = requests.get(f"{API_BASE}/sensors/latest", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


s = get_latest_sensors() if (alive and live_mode) else {}

# Helper to safely choose sensor value or default
def pick(key: str, default: float) -> float:
    val = s.get(key, None)
    if val is None:
        return float(default)
    try:
        return float(val)
    except Exception:
        return float(default)


# -------------------------
# INPUTS
# -------------------------
col1, col2, col3 = st.columns(3)

if live_mode:
    # LIVE values from API
    with col1:
        lat = pick("lat", 11.021234)
        lon = pick("lon", 78.123456)
        st.number_input("Latitude", value=lat, format="%.6f", disabled=True)
        st.number_input("Longitude", value=lon, format="%.6f", disabled=True)

    with col2:
        TEMP = pick("TEMP", 30.0)
        WDSP = pick("WDSP", 12.0)
        VISIB = pick("VISIB", 8.0)
        st.number_input("Temperature (TEMP)", value=TEMP, disabled=True)
        st.number_input("Wind Speed (WDSP)", value=WDSP, disabled=True)
        st.number_input("Visibility (VISIB)", value=VISIB, disabled=True)

    with col3:
        SST = pick("SST", 27.1)
        SLP = pick("SLP", 1010.0)
        STP = pick("STP", 1005.0)
        st.number_input("Sea Surface Temp (SST)", value=SST, disabled=True)
        st.number_input("Sea Pressure (SLP)", value=SLP, disabled=True)
        st.number_input("Station Pressure (STP)", value=STP, disabled=True)

    col4, col5, col6, col7 = st.columns(4)
    with col4:
        DEWP = pick("DEWP", 20.0)
        st.number_input("Dew Point (DEWP)", value=DEWP, disabled=True)
    with col5:
        MXSPD = pick("MXSPD", 18.0)
        st.number_input("Max Wind (MXSPD)", value=MXSPD, disabled=True)
    with col6:
        MAXT = pick("MAX", 32.0)
        st.number_input("MAX Temp (MAX)", value=MAXT, disabled=True)
    with col7:
        MINT = pick("MIN", 24.0)
        st.number_input("MIN Temp (MIN)", value=MINT, disabled=True)

    updated_at = s.get("updated_at", None)
    if updated_at:
        st.info(f"📡 Latest sensor update: {updated_at}")
    else:
        st.warning("No sensor data received yet. Send data to POST /sensors")

else:
    # MANUAL inputs
    with col1:
        lat = st.number_input("Latitude", value=11.021234, format="%.6f")
        lon = st.number_input("Longitude", value=78.123456, format="%.6f")

    with col2:
        TEMP = st.number_input("Temperature (TEMP)", value=30.0)
        WDSP = st.number_input("Wind Speed (WDSP)", value=12.0)
        VISIB = st.number_input("Visibility (VISIB)", value=8.0)

    with col3:
        SST = st.number_input("Sea Surface Temp (SST)", value=27.1)
        SLP = st.number_input("Sea Pressure (SLP)", value=1010.0)
        STP = st.number_input("Station Pressure (STP)", value=1005.0)

    col4, col5, col6, col7 = st.columns(4)
    with col4:
        DEWP = st.number_input("Dew Point (DEWP)", value=20.0)
    with col5:
        MXSPD = st.number_input("Max Wind (MXSPD)", value=18.0)
    with col6:
        MAXT = st.number_input("MAX Temp (MAX)", value=32.0)
    with col7:
        MINT = st.number_input("MIN Temp (MIN)", value=24.0)


payload = {
    "TEMP": TEMP,
    "WDSP": WDSP,
    "DEWP": DEWP,
    "SLP": SLP,
    "STP": STP,
    "VISIB": VISIB,
    "MXSPD": MXSPD,
    "MAX": MAXT,
    "MIN": MINT,
    "SNDP": 0,
    "SST": SST,
    "lat": lat,
    "lon": lon
}


# -------------------------
# MAP + RESULTS
# -------------------------
left, right = st.columns(2)

with left:
    st.subheader("📍 Boat Location")
    st.map([{"lat": lat, "lon": lon}])
    st.write({"lat": lat, "lon": lon})

with right:
    st.subheader("🌦 Weather & 🔥 Hotspot")

    # In live mode you can auto-predict too (optional), but to keep API load low we keep button
    if st.button("▶ Predict (All)", width="stretch", disabled=not alive):
        try:
            r = requests.post(f"{API_BASE}/predict/all", json=payload, timeout=10)

            if r.status_code != 200:
                st.error(f"API Error {r.status_code}")
                st.code(r.text)
            else:
                res = r.json()
                alert = res.get("weather_alert", 0)
                conf = res.get("weather_confidence", None)
                zone = res.get("hotspot_zone", "UNKNOWN")

                if alert == 1:
                    if THEME_OK:
                        banner("danger", "🚨 DANGER: UNSAFE WEATHER",
                               "<b>Go to shore immediately.</b> Avoid deep routes and reduce speed.")
                    else:
                        st.error("🚨 UNSAFE WEATHER - GO TO SHORE")
                else:
                    if THEME_OK:
                        banner("safe", "✅ SAFE WEATHER",
                               f"Confidence: <b>{conf:.2f}</b>" if conf is not None else "Conditions stable.")
                    else:
                        st.success("✅ SAFE WEATHER")

                if THEME_OK:
                    banner("warn", "🔥 Hotspot Zone", f"Predicted Zone: <b>{zone}</b>")
                else:
                    st.info(f"🔥 Hotspot Zone: {zone}")

                # Show SOS if active (from API response)
                sos = res.get("sos", None)
                if sos and sos.get("active"):
                    banner("danger", "🚨 SOS ACTIVE",
                           f"LAT <b>{sos.get('lat')}</b>, LON <b>{sos.get('lon')}</b><br/>"
                           f"Reason: <b>{sos.get('reason')}</b><br/>"
                           f"Time: <b>{sos.get('created_at')}</b>")

                with st.expander("Raw output"):
                    st.json(res)

        except Exception as e:
            st.error("API call failed")
            st.write(str(e))


# -------------------------
# FISH DEMO
# -------------------------
st.markdown("---")
st.subheader("🐟 Fish Detection Demo")

if st.button("Run Sonar Scan", width="stretch", disabled=not alive):
    demo_features = [random.uniform(-1, 1) for _ in range(60)]
    try:
        r = requests.post(f"{API_BASE}/predict/fish", json={"features": demo_features}, timeout=10)
        if r.status_code != 200:
            st.error(f"API Error {r.status_code}")
            st.code(r.text)
        else:
            out = r.json()
            pred = out.get("prediction", "R")
            conf = out.get("confidence", 0.0)

            if THEME_OK:
                if pred == "M":
                    banner("safe", "🐟 Object Detected", f"Class: <b>{pred}</b> • Confidence: <b>{conf:.2f}</b>")
                else:
                    banner("warn", "🪨 No Object Detected", f"Class: <b>{pred}</b> • Confidence: <b>{conf:.2f}</b>")
            else:
                st.json(out)

            with st.expander("Raw fish output"):
                st.json(out)
    except Exception as e:
        st.error("API call failed")
        st.write(str(e))