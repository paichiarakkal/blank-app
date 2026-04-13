import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. ലിങ്കുകളും ലോഗിൻ വിവരങ്ങളും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v26.8", layout="wide")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Home"

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം & മോഡേൺ സൈഡ്ബാർ
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    
    /* സൈഡ്ബാർ ഡിസൈൻ */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        min-width: 320px !important;
    }

    /* 3x3 ഗ്രിഡ് ബട്ടൺ സ്റ്റൈൽ */
    div.stButton > button {
        border-radius: 20px !important;
        width: 80px !important;
        height: 80px !important;
        border: 2px solid #FFD700 !important;
        background-color: #1e293b !important;
        color: #FFD700 !important;
        font-size: 30px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        transition: 0.3s all ease;
    }

    div.stButton > button:hover {
        background-color: #FFD700 !important;
        color: #000 !important;
        transform: translateY(-5px);
    }

    /* ബട്ടൺ ലേബൽ */
    .btn-text {
        color: #FFD700;
        font-size: 11px;
        font-weight: bold;
        text-align: center;
        margin-top: 8px;
        margin-bottom: 20px;
    }

    /* മുകളിൽ കാണുന്ന ബാക്കി തുക ബോക്സ് */
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if not st.session_state.auth:
    # ലോഗിൻ പേജ് കോഡ് ഇവിടെ വരും...
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            st.rerun()
else:
    # --- 📱 SIDEBAR 3x3 NAVIGATION ---
    st.sidebar.markdown("<h1 style='text-align: center; color: #FFD700;'>PAICHI</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    menu = [
        ("🏠", "🏠 Home"), ("💰", "💰 Add"), ("📊", "📊 Reports"),
        ("🤝", "🤝 Debt"), ("📄", "📄 Sheet"), ("📈", "📈 Charts"),
        ("🌙", "🌙 Peace"), ("⚙️", "⚙️ Setup"), ("🚪", "Logout")
    ]

    # 3x3 ഗ്രിഡ് ലോജിക്
    for i in range(0, len(menu), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(menu):
                icon, name = menu[idx]
                with cols[j]:
                    if st.button(icon, key=f"nav_{idx}"):
                        if name == "Logout":
                            st.session_state.auth = False
                            st.rerun()
                        else:
                            st.session_state.page = name
                            st.rerun()
                    st.markdown(f"<p class='btn-text'>{name.split()[-1]}</p>", unsafe_allow_html=True)

    # --- CONTENT AREA ---
    page = st.session_state.page
    st.title(page)
    
    # ബാക്കി പേജുകളുടെ കണ്ടന്റ് ഇവിടെ വരും... (Home, Add Entry etc.)
    if page == "🏠 Home":
        st.info("നിങ്ങൾ ഇപ്പോൾ ഹോം പേജിലാണ്. താഴെ വിവരങ്ങൾ കാണാം.")
