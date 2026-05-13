import streamlit as st
from datetime import datetime

def inject_theme():
    st.markdown(
        """
        <style>
        /* ========= Global Background (Ocean Command Center) ========= */
        .stApp {
            background:
              radial-gradient(1200px 800px at 12% 8%, rgba(56,189,248,0.18), transparent 60%),
              radial-gradient(900px 700px at 90% 12%, rgba(168,85,247,0.14), transparent 60%),
              radial-gradient(900px 700px at 25% 95%, rgba(34,197,94,0.10), transparent 55%),
              linear-gradient(180deg, #060b16 0%, #0b1220 60%, #070b14 100%);
            color: #e5e7eb;
        }

        /* Hide Streamlit defaults */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ========= Typography ========= */
        .h1 { font-size: 2.05rem; font-weight: 900; margin: 0; }
        .sub { color: #9ca3af; margin-top: 6px; margin-bottom: 0; }

        /* ========= Topbar ========= */
        .topbar {
            display:flex; align-items:center; justify-content:space-between;
            padding: 12px 14px; border-radius: 18px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 14px;
            backdrop-filter: blur(8px);
        }
        .brand { display:flex; gap:10px; align-items:center; font-weight: 900; }
        .brand-badge{
            width: 36px; height:36px; border-radius: 14px;
            display:flex; align-items:center; justify-content:center;
            background: rgba(56,189,248,0.14);
            border: 1px solid rgba(56,189,248,0.25);
        }
        .pill {
            display:inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 0.86rem;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.06);
        }

        /* ========= Hero ========= */
        .hero {
            padding: 16px 16px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 14px;
        }

        /* ========= KPI cards ========= */
        .kpi-grid { display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
        .kpi {
            border-radius: 18px;
            padding: 14px 14px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
        }
        .kpi-title { color:#9ca3af; font-size: 0.86rem; margin-bottom: 4px; }
        .kpi-value { font-size: 1.35rem; font-weight: 900; }
        .kpi-sub { color:#9ca3af; font-size: 0.86rem; margin-top: 4px; }

        /* ========= Module cards ========= */
        .grid { display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
        .card {
            border-radius: 20px;
            padding: 16px 16px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            transition: transform .12s ease, border-color .12s ease, background .12s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.22);
            background: rgba(255,255,255,0.08);
        }
        .card h3{ margin:0 0 6px 0; font-size: 1.05rem; }
        .card p{ margin:0; color:#9ca3af; font-size: 0.92rem; }

        /* ========= Alert banners ========= */
        .banner {
            border-radius: 16px;
            padding: 14px 16px;
            border: 1px solid rgba(255,255,255,0.10);
            margin: 10px 0 16px 0;
        }
        .safe { background: rgba(16,185,129,0.12); }
        .warn { background: rgba(245,158,11,0.12); }
        .danger { background: rgba(239,68,68,0.14); }
        .banner-title { font-weight: 900; margin-bottom: 4px; }
        .banner-text { color: #e5e7eb; }

        /* Buttons more premium */
        div.stButton > button {
            border-radius: 14px !important;
            padding: 0.62rem 1rem !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            background: rgba(255,255,255,0.08) !important;
        }
        div.stButton > button:hover{
            border-color: rgba(255,255,255,0.28) !important;
            background: rgba(255,255,255,0.10) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def topbar(user_name: str | None = None):
    user_text = f"👤 {user_name}" if user_name else "🔐 Not logged in"
    now = datetime.now().strftime("%d %b %Y • %I:%M %p")
    st.markdown(
        f"""
        <div class="topbar">
          <div class="brand">
            <div class="brand-badge">🌊</div>
            <div>
              <div style="font-size:1.05rem;font-weight:900;">Wave sense</div>
              <div style="color:#9ca3af;font-size:.86rem;margin-top:-2px;">Ocean Monitoring Command Center</div>
            </div>
          </div>
          <div style="display:flex;gap:10px;align-items:center;">
            <span class="pill">🕒 {now}</span>
            <span class="pill">{user_text}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero">
          <div class="h1">{title}</div>
          <p class="sub">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def banner(level: str, title: str, text_html: str):
    st.markdown(
        f"""
        <div class="banner {level}">
          <div class="banner-title">{title}</div>
          <div class="banner-text">{text_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
