import streamlit as st
import requests
import random
from ui_theme import inject_theme, topbar, hero, banner
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Fish Detection • Wave Sense", layout="wide")
inject_theme()

if not st.session_state.get("authed"):
    st.error("Please login first.")
    st.switch_page("app.py")

topbar(st.session_state.get("user", {}).get("name"))
hero("Fish/Object Detection (Sonar Demo)", "Run a sonar scan → object presence + confidence + scan history.")
st.session_state.last_module = "Fish Detection"

API_BASE = st.sidebar.text_input("API Base URL", value=st.session_state.get("API_BASE", "http://127.0.0.1:8000"))
st.session_state["API_BASE"] = API_BASE

# Optional auto-refresh (for UI only)
live_refresh = st.toggle("🔄 Auto refresh (5s)", value=False)
if live_refresh:
    st_autorefresh(interval=5000, key="fish_refresh")

def push_alert(kind: str, msg: str):
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    st.session_state.alerts.insert(0, {"kind": kind, "msg": msg})
    st.session_state.alerts = st.session_state.alerts[:7]

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

st.markdown('<span class="pill">Endpoint: <b>/predict/fish</b></span>', unsafe_allow_html=True)

left, right = st.columns([1.15, 0.85], vertical_alignment="top")

with left:
    st.markdown("### 🎛️ Scan Controls (Demo)")
    c1, c2 = st.columns(2)
    noise = c1.slider("Signal Variation", 0.0, 1.0, 0.35, 0.05)
    strength = c2.slider("Scan Strength", 0.0, 1.0, 0.60, 0.05)

    if st.button("Run Sonar Scan", type="primary", width="stretch"):
        features = [max(0.0, min(1.0, random.random() * (1 + noise) * strength)) for _ in range(60)]
        payload = {"features": features}

        try:
            r = requests.post(f"{API_BASE}/predict/fish", json=payload, timeout=10)
            r.raise_for_status()
            out = r.json()

            pred = out.get("prediction", "R")
            conf = float(out.get("confidence", 0.0))

            interest = int(conf * 100) if pred == "M" else int((1 - conf) * 60)
            interest = max(0, min(100, interest))

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Result", "Object Detected" if pred == "M" else "No Object")
            m2.metric("Class", pred)
            m3.metric("Confidence", f"{conf:.2f}")
            m4.metric("Interest", f"{interest}/100")

            st.progress(interest / 100)

            if pred == "M":
                st.session_state.last_risk = "TARGET ✅"
                banner("safe", "🐟 Object Detected",
                       "Possible underwater object detected (proxy fish). Consider scanning nearby points.")
                push_alert("safe", f"Fish/Object detected • conf {conf:.2f}")
            else:
                st.session_state.last_risk = "NO TARGET 🟡"
                banner("warn", "🪨 No Object Detected",
                       "Mostly rock/no target detected. Try another nearby area or hotspot zone.")
                push_alert("warn", f"No target • conf {conf:.2f}")

            st.session_state.scan_history.insert(0, {
                "result": "Detected" if pred == "M" else "No target",
                "class": pred,
                "confidence": round(conf, 2),
                "interest": interest
            })
            st.session_state.scan_history = st.session_state.scan_history[:10]

            with st.expander("Raw API output"):
                st.json(out)

        except Exception as e:
            st.error(f"API error: {e}")

with right:
    st.markdown("### 🧾 Scan History")
    if not st.session_state.scan_history:
        banner("warn", "No scans yet", "Run a sonar scan to store scan results here.")
    else:
        for item in st.session_state.scan_history:
            lvl = "safe" if item["class"] == "M" else "warn"
            banner(lvl,
                   f"{item['result']} • {item['confidence']}",
                   f"Class: <b>{item['class']}</b> • Interest: <b>{item['interest']}/100</b>")

    st.divider()
    if st.button("Clear Scan History", width="stretch"):
        st.session_state.scan_history = []
        st.rerun()

st.page_link("pages/home.py", label="← Back to Home", icon="🏠")
