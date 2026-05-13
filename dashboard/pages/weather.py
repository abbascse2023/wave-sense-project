import streamlit as st
import requests
from ui_theme import inject_theme, topbar, hero, banner
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Weather • Smart Marine", layout="wide")
inject_theme()

if not st.session_state.get("authed"):
    st.error("Please login first.")
    st.switch_page("app.py")

topbar(st.session_state.get("user", {}).get("name"))
hero("Weather Safety Prediction", "Predict safe/unsafe weather with a risk meter and emergency guidance.")
st.session_state.last_module = "Weather"

API_BASE = st.sidebar.text_input("API Base URL", value=st.session_state.get("API_BASE", "http://127.0.0.1:8000"))
st.session_state["API_BASE"] = API_BASE

def get_latest_sensors():
    try:
        r = requests.get(f"{API_BASE}/sensors/latest", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

def pick(s: dict, key: str, default: float) -> float:
    v = s.get(key, None)
    if v is None:
        return float(default)
    try:
        return float(v)
    except Exception:
        return float(default)

def push_alert(kind: str, msg: str):
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    st.session_state.alerts.insert(0, {"kind": kind, "msg": msg})
    st.session_state.alerts = st.session_state.alerts[:7]

# ---- Live mode + refresh ----
live_mode = st.toggle("📡 Live Sensor Mode (Auto update every 5 seconds)", value=True)
auto_predict = st.toggle("⚡ Auto Predict every refresh (Live Mode)", value=False, disabled=not live_mode)

if live_mode:
    st.caption("🔄 Live mode ON: reading /sensors/latest every 5 seconds")
    st_autorefresh(interval=5000, key="weather_refresh")

s = get_latest_sensors() if live_mode else {}

# ---- Inputs ----
st.markdown("### 📥 Inputs")
c1, c2, c3, c4 = st.columns(4)

if live_mode:
    TEMP = pick(s, "TEMP", 30.0); c1.number_input("TEMP", value=TEMP, disabled=True)
    WDSP = pick(s, "WDSP", 12.0); c2.number_input("WDSP (Wind)", value=WDSP, disabled=True)
    DEWP = pick(s, "DEWP", 24.0); c3.number_input("DEWP", value=DEWP, disabled=True)
    VISIB = pick(s, "VISIB", 10.0); c4.number_input("VISIB", value=VISIB, disabled=True)
else:
    TEMP = c1.number_input("TEMP", value=30.0)
    WDSP = c2.number_input("WDSP (Wind)", value=12.0)
    DEWP = c3.number_input("DEWP", value=24.0)
    VISIB = c4.number_input("VISIB", value=10.0)

c1, c2, c3, c4 = st.columns(4)
if live_mode:
    SLP = pick(s, "SLP", 1012.0); c1.number_input("SLP", value=SLP, disabled=True)
    STP = pick(s, "STP", 1010.0); c2.number_input("STP", value=STP, disabled=True)
    MXSPD = pick(s, "MXSPD", 20.0); c3.number_input("MXSPD", value=MXSPD, disabled=True)
    SNDP = pick(s, "SNDP", 0.0); c4.number_input("SNDP", value=SNDP, disabled=True)
else:
    SLP = c1.number_input("SLP", value=1012.0)
    STP = c2.number_input("STP", value=1010.0)
    MXSPD = c3.number_input("MXSPD", value=20.0)
    SNDP = c4.number_input("SNDP", value=0.0)

c1, c2 = st.columns(2)
if live_mode:
    MAX = pick(s, "MAX", 33.0); c1.number_input("MAX", value=MAX, disabled=True)
    MIN = pick(s, "MIN", 25.0); c2.number_input("MIN", value=MIN, disabled=True)
else:
    MAX = c1.number_input("MAX", value=33.0)
    MIN = c2.number_input("MIN", value=25.0)

if live_mode:
    updated_at = s.get("updated_at")
    if updated_at:
        st.info(f"📡 Latest sensor update: {updated_at}")
    else:
        st.warning("No sensor data received yet. Send data to POST /sensors")

payload = {
    "TEMP": TEMP, "WDSP": WDSP, "DEWP": DEWP, "SLP": SLP, "STP": STP,
    "VISIB": VISIB, "MXSPD": MXSPD, "MAX": MAX, "MIN": MIN, "SNDP": SNDP
}

def run_prediction():
    try:
        r = requests.post(f"{API_BASE}/predict/weather", json=payload, timeout=10)
        r.raise_for_status()
        out = r.json()

        alert = int(out.get("weather_alert", 0))
        conf = float(out.get("confidence", 0.0))

        risk = int((conf * 100) if alert == 1 else ((1 - conf) * 45))
        risk = max(0, min(100, risk))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Status", "UNSAFE 🚨" if alert else "SAFE ✅")
        m2.metric("Confidence", f"{conf:.2f}")
        m3.metric("Risk Score", f"{risk}/100")
        m4.metric("Wind (WDSP)", f"{WDSP:.1f}")
        st.progress(risk / 100)

        if alert == 0:
            st.session_state.last_risk = "SAFE ✅"
            banner("safe", "✅ SAFE WEATHER",
                   "Conditions look stable. Continue fishing but monitor updates regularly.")
            push_alert("safe", f"Weather SAFE • confidence {conf:.2f}")
            st.info("Recommendation: keep life jackets ready • check again in 30 minutes.")
        else:
            st.session_state.last_risk = "DANGER 🚨"
            banner("danger", "🚨 DANGER: UNSAFE WEATHER",
                   "<b>Go to shore immediately.</b> Reduce speed, avoid deep route, and stay together.")
            push_alert("danger", f"UNSAFE WEATHER • confidence {conf:.2f} • risk {risk}/100")
            st.warning("Emergency checklist", icon="🚨")
            st.markdown(
                "- Share GPS with shore team\n"
                "- Inform nearby boats/coast guard\n"
                "- Avoid high waves and deep routes\n"
                "- Keep phone/radio charged\n"
            )

        with st.expander("Raw API output"):
            st.json(out)

    except Exception as e:
        st.error(f"API error: {e}")

st.markdown("---")
if st.button("Predict Weather Safety", type="primary", width="stretch"):
    run_prediction()

# Auto predict (live mode)
if live_mode and auto_predict:
    run_prediction()

st.page_link("pages/home.py", label="← Back to Home", icon="🏠")
