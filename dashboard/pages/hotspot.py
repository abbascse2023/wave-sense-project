import streamlit as st
import requests
from ui_theme import inject_theme, topbar, hero, banner
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Wave Sense", layout="wide")
inject_theme()

if not st.session_state.get("authed"):
    st.error("Please login first.")
    st.switch_page("app.py")

topbar(st.session_state.get("user", {}).get("name"))
hero("Fishing Hotspot Zone", "SST-based hotspot indicator with zone meter and recommendations.")
st.session_state.last_module = "Hotspot"

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

live_mode = st.toggle("📡 Live Sensor Mode (Auto update every 5 seconds)", value=True)

if live_mode:
    st.caption("🔄 Live mode ON: reading /sensors/latest every 5 seconds")
    st_autorefresh(interval=5000, key="hotspot_refresh")

s = get_latest_sensors() if live_mode else {}

st.markdown('<span class="pill">Rule: SST < 24 = LOW • 24–28 = MEDIUM • > 28 = HIGH</span>', unsafe_allow_html=True)

left, right = st.columns([1.05, 0.95], vertical_alignment="top")

with left:
    st.markdown("### 🌡️ Sea Surface Temperature Input")

    if live_mode:
        sst_val = pick(s, "SST", 26.0)
        st.slider("Sea Surface Temperature (SST)", 10.0, 40.0, float(sst_val), 0.1, disabled=True)
        sst = float(sst_val)
        updated_at = s.get("updated_at")
        if updated_at:
            st.info(f"📡 Latest sensor update: {updated_at}")
        else:
            st.warning("No sensor data received yet. Send data to POST /sensors")
    else:
        sst = st.slider("Sea Surface Temperature (SST)", 10.0, 40.0, 26.0, 0.1)

    meter = int((sst - 10.0) / 30.0 * 100)
    meter = max(0, min(100, meter))
    st.markdown("### 📊 Zone Meter")
    st.progress(meter / 100)

    if st.button("Analyze Hotspot", type="primary", width="stretch"):
        if sst < 24:
            st.session_state.last_risk = "LOW 🟡"
            banner("warn", "🔻 LOW Potential Zone",
                   "SST is below the optimal range. Consider moving to a warmer nearby region.")
            push_alert("warn", f"Hotspot LOW • SST {sst:.1f}°C")
            st.markdown("**Suggested action:** Try another location/time • Use weather safety check before moving.")
        elif 24 <= sst <= 28:
            st.session_state.last_risk = "MEDIUM ✅"
            banner("safe", "✅ MEDIUM Potential Zone",
                   "Good SST range. Suitable for fishing if weather is safe.")
            push_alert("safe", f"Hotspot MEDIUM • SST {sst:.1f}°C")
            st.markdown("**Suggested action:** Start fishing here • Monitor weather every 30 minutes.")
        else:
            st.session_state.last_risk = "HIGH 🔥"
            banner("safe", "🔥 HIGH Potential Zone",
                   "High SST range. Strong fishing potential if conditions remain stable.")
            push_alert("safe", f"Hotspot HIGH • SST {sst:.1f}°C")
            st.markdown("**Suggested action:** Prioritize this zone • Combine with sonar scan + weather check.")

with right:
    st.markdown("### 🧭 Decision Support")
    banner("warn", "Best Practice",
           "Always combine <b>Weather Safety</b> + <b>Hotspot</b> before deciding the fishing route.")
    st.markdown(
        "- If weather is UNSAFE → ignore hotspot and return to shore.\n"
        "- If weather is SAFE → use hotspot to choose route.\n"
        "- Use fish detection scan near medium/high SST zones.\n"
    )

st.page_link("pages/home.py", label="← Back to Home", icon="🏠")
