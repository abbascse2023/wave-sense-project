import streamlit as st
import requests
from ui_theme import inject_theme, topbar, hero, banner
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Home • Wave Sense", layout="wide")
inject_theme()

if not st.session_state.get("authed"):
    st.error("Please login first.")
    st.switch_page("app.py")

topbar(st.session_state.get("user", {}).get("name"))
hero("Command Center", "Live monitoring + predictive alerts for fishermen (software prototype).")

# ---- Alert log (session-based) ----
if "alerts" not in st.session_state:
    st.session_state.alerts = []  # list of dicts: {"type": "...", "msg": "..."}

def push_alert(kind: str, msg: str):
    st.session_state.alerts.insert(0, {"kind": kind, "msg": msg})
    st.session_state.alerts = st.session_state.alerts[:7]

# ---- Check API status (optional) ----
API_BASE = st.sidebar.text_input("API Base URL", value="http://127.0.0.1:8000")

api_ok = False
try:
    r = requests.get(f"{API_BASE}/", timeout=2)
    api_ok = (r.status_code == 200)
except Exception:
    api_ok = False

# ---- KPI Cards ----
k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(
        f"""
        <div class="kpi">
          <div class="kpi-title">System Status</div>
          <div class="kpi-value">{'ONLINE ✅' if api_ok else 'OFFLINE ❌'}</div>
          <div class="kpi-sub">{'FastAPI connected' if api_ok else 'Start uvicorn src.api:app --reload'}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    last = st.session_state.get("last_module", "—")
    st.markdown(
        f"""
        <div class="kpi">
          <div class="kpi-title">Last Used Module</div>
          <div class="kpi-value">{last}</div>
          <div class="kpi-sub">Helps show usage in demo</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    last_risk = st.session_state.get("last_risk", "—")
    st.markdown(
        f"""
        <div class="kpi">
          <div class="kpi-title">Last Risk Level</div>
          <div class="kpi-value">{last_risk}</div>
          <div class="kpi-sub">Updated when you run predictions</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

left, right = st.columns([1.2, 0.8], vertical_alignment="top")

with left:
    st.markdown("### 🧩 Modules")
    colA, colB = st.columns(2)

    with colA:
        st.markdown("""<div class="card"><h3>🌦️ Weather Safety</h3><p>Unsafe weather detection + emergency action.</p></div>""", unsafe_allow_html=True)
        if st.button("Open Weather →", width="stretch"):
            st.session_state.last_module = "Weather"
            st.switch_page("pages/weather.py")

        st.markdown("""<div class="card"><h3>🎯 Hotspot Zone</h3><p>SST-based fishing potential zones.</p></div>""", unsafe_allow_html=True)
        if st.button("Open Hotspot →", width="stretch"):
            st.session_state.last_module = "Hotspot"
            st.switch_page("pages/hotspot.py")

    with colB:
        st.markdown("""<div class="card"><h3>🐟 Fish/Object Detection</h3><p>Sonar demo prediction + confidence.</p></div>""", unsafe_allow_html=True)
        if st.button("Open Fish Detection →", width="stretch"):
            st.session_state.last_module = "Fish Detection"
            st.switch_page("pages/fish.py")

        st.markdown("""<div class="card"><h3>🗺️ Boat Tracking</h3><p>GPS tracking + emergency share.</p></div>""", unsafe_allow_html=True)
        if st.button("Open Tracking →", width="stretch"):
            st.session_state.last_module = "Tracking"
            st.switch_page("pages/tracking.py")

with right:
    st.markdown("### 🚨 Recent Alerts")
    if not st.session_state.alerts:
        banner("warn", "No alerts yet", "Run weather prediction to generate safety alerts.")
    else:
        for a in st.session_state.alerts:
            lvl = "danger" if a["kind"] == "danger" else ("warn" if a["kind"] == "warn" else "safe")
            banner(lvl, a["kind"].upper(), a["msg"])

    st.divider()
    if st.button("Clear Alerts", width="stretch"):
        st.session_state.alerts = []
        st.rerun()

st.divider()
if st.button("Logout", width="stretch"):
    st.session_state.authed = False
    st.session_state.user = None
    st.switch_page("app.py")
