import streamlit as st
import pandas as pd
import requests

from streamlit_autorefresh import st_autorefresh
from ui_theme import inject_theme, topbar, hero, banner

st.set_page_config(page_title="Boat Tracking • Wave Sense", layout="wide")
inject_theme()

if not st.session_state.get("authed"):
    st.error("Please login first.")
    st.switch_page("app.py")

topbar(st.session_state.get("user", {}).get("name"))
hero("Boat Tracking", "Live GPS monitoring with SOS sharing and safety boundary (geofence) alerts.")
st.session_state.last_module = "Tracking"

API_BASE = st.sidebar.text_input(
    "API Base URL",
    value=st.session_state.get("API_BASE", "http://127.0.0.1:8000"),
)
st.session_state["API_BASE"] = API_BASE

def api_get(path: str):
    return requests.get(f"{API_BASE}{path}", timeout=5)

def api_post(path: str, payload: dict):
    return requests.post(f"{API_BASE}{path}", json=payload, timeout=8)

def get_latest_gps():
    try:
        r = api_get("/sensors/latest")
        if r.status_code == 200:
            s = r.json() or {}
            lat = s.get("lat", None)
            lon = s.get("lon", None)
            if lat is not None and lon is not None:
                return float(lat), float(lon), f"LIVE • sensors/latest • updated_at: {s.get('updated_at','unknown')}"
    except Exception:
        pass

    try:
        r = api_get("/boat/location")
        if r.status_code == 200:
            loc = r.json() or {}
            lat = loc.get("lat", None)
            lon = loc.get("lon", None)
            if lat is not None and lon is not None:
                lat_f = float(lat)
                lon_f = float(lon)
                if lat_f == 0.0 and lon_f == 0.0:
                    return None, None, "LIVE • boat/location • (0,0) not set yet"
                return lat_f, lon_f, f"LIVE • boat/location • updated_at: {loc.get('updated_at','unknown')}"
    except Exception:
        pass

    return None, None, "LIVE • No GPS available"

st.sidebar.markdown("### Mode")
mode = st.sidebar.radio("Tracking Mode", ["LIVE (API)", "SIMULATION (DEMO)"], index=0)

st.sidebar.markdown("### Auto Refresh")
refresh_sec = st.sidebar.slider("Refresh (seconds)", 1, 15, 5)

st_autorefresh(interval=refresh_sec * 1000, key="tracking_refresh")

st.sidebar.markdown("### Safety Boundary (Geofence)")
SAFE_LAT_MIN = st.sidebar.number_input("Safe Lat Min", value=10.80)
SAFE_LAT_MAX = st.sidebar.number_input("Safe Lat Max", value=11.30)
SAFE_LON_MIN = st.sidebar.number_input("Safe Lon Min", value=77.70)
SAFE_LON_MAX = st.sidebar.number_input("Safe Lon Max", value=78.40)

DEMO_ROUTE = [
    {"lat": 11.0000, "lon": 78.0000},
    {"lat": 11.0010, "lon": 78.0012},
    {"lat": 11.0020, "lon": 78.0025},
    {"lat": 11.0030, "lon": 78.0040},
    {"lat": 11.0040, "lon": 78.0052},
    {"lat": 11.0050, "lon": 78.0068},
    {"lat": 11.0060, "lon": 78.0085},
    {"lat": 11.0072, "lon": 78.0100},
]

if "demo_idx" not in st.session_state:
    st.session_state.demo_idx = 0

if "track_points" not in st.session_state:
    st.session_state.track_points = [{"lat": 11.0000, "lon": 78.0000}]

last = st.session_state.track_points[-1]
new_point = {"lat": float(last["lat"]), "lon": float(last["lon"])}
source_label = ""

if mode == "LIVE (API)":
    lat, lon, label = get_latest_gps()
    source_label = label

    if lat is not None and lon is not None:
        new_point = {"lat": float(lat), "lon": float(lon)}
    else:
        banner("warn", "No Live GPS Yet", "Send GPS using POST /sensors or POST /boat/location. Showing last point.")
else:
    st.session_state.demo_idx = (st.session_state.demo_idx + 1) % len(DEMO_ROUTE)
    p = DEMO_ROUTE[st.session_state.demo_idx]
    new_point = {"lat": float(p["lat"]), "lon": float(p["lon"])}
    source_label = f"SIMULATION (DEMO ROUTE) • point {st.session_state.demo_idx + 1}/{len(DEMO_ROUTE)}"

st.session_state.track_points.append(new_point)
st.session_state.track_points = st.session_state.track_points[-50:]
df = pd.DataFrame(st.session_state.track_points)

inside = (SAFE_LAT_MIN <= new_point["lat"] <= SAFE_LAT_MAX) and (SAFE_LON_MIN <= new_point["lon"] <= SAFE_LON_MAX)

left, right = st.columns([1.25, 0.75], vertical_alignment="top")

with left:
    st.markdown("### 🗺️ Live Map")
    st.caption(source_label)
    st.map(df)

    st.markdown("### 📈 Trail Data")
    st.dataframe(df.tail(12), width="stretch")

with right:
    st.markdown("### 📍 Current Location")
    st.metric("Latitude", f"{new_point['lat']:.5f}")
    st.metric("Longitude", f"{new_point['lon']:.5f}")

    st.divider()

    if inside:
        banner("safe", "✅ Within Safe Boundary", "Boat is inside the defined safety boundary.")
    else:
        banner("danger", "⚠️ Outside Safe Boundary", "Boat moved outside the safe boundary.")

    st.divider()

    st.markdown("### 🚨 SOS / Share GPS")
    gps_text = f"LAT {new_point['lat']:.5f}, LON {new_point['lon']:.5f}"
    banner("warn", "Share this GPS to Shore Team", f"<b>{gps_text}</b>")

    sos = None
    try:
        r = api_get("/boat/sos")
        if r.status_code == 200:
            sos = r.json()
    except Exception:
        sos = None

    if sos and sos.get("active"):
        banner(
            "danger",
            "🚨 SOS ACTIVE",
            f"Last SOS: <b>LAT {float(sos.get('lat', 0)):.5f}, LON {float(sos.get('lon', 0)):.5f}</b><br/>"
            f"Reason: <b>{sos.get('reason')}</b><br/>"
            f"Time: <b>{sos.get('created_at')}</b>",
        )
        if st.button("✅ Clear SOS", width="stretch"):
            try:
                api_post("/boat/sos/clear", {})
                st.success("SOS cleared.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to clear SOS: {e}")

    if st.button("🚨 Trigger SOS Now", type="primary", width="stretch"):
        try:
            payload = {"lat": new_point["lat"], "lon": new_point["lon"], "reason": "Manual SOS from dashboard"}
            api_post("/boat/sos", payload)
            st.success("SOS triggered and sent to API.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to trigger SOS: {e}")

st.caption("LIVE mode uses API GPS. SIMULATION mode uses a predefined demo route (works without hardware).")
st.page_link("pages/home.py", label="← Back to Home", icon="🏠")