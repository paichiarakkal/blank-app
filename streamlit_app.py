import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# വോയിസ് റെക്കോർഡർ എറർ ഒഴിവാക്കാൻ
try:
    from streamlit_mic_recorder import speech_to_text
except ImportError:
    speech_to_text = None

# Settings
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI SIDE-GRID", layout="wide", initial_sidebar_state="expanded")

# --- 🛠️ SIDEBAR 3x3 GRID CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; }
    
    /* സൈഡ്‌ബാർ വീതി കൂട്ടുന്നു */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        min-width: 320px !important;
        max-width: 320px !important;
        border-right: 2px solid #ffd700;
    }

    /* സൈഡ്‌ബാറിനുള്ളിൽ 3 കോളങ്ങൾ നിർബന്ധമാക്കുന്നു */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div {
        width: 33% !important;
        min-width: 33% !important;
    }

    /* സൈഡ്‌ബാറിലെ റൗണ്ട് ബട്ടണുകൾ */
    .stSidebar .stButton > button {
        background-color: #334155 !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
        border-radius: 50% !important; 
        height: 70px !important;
        width: 70px !important;
        margin: 5px auto !important;
        display: flex !important;
        align-items: center;
        justify-content: center;
        font-size: 20px !important;
    }
    
    .side-label {
        text-align: center;
        font-size: 10px;
        color: #ffffff;
        font-weight: bold;
        margin-bottom: 15px;
        text-transform: uppercase;
    }

    .main-card {
        background-color: #1e293b;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #ffd700;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def nav(p):
    st.session_state.page = p

# --- 📱 SIDEBAR 3x3 GRID ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>PAICHI MENU</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # വരി 1
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        st.button("🏠", key="h", on_click=nav, args=("🏠 HOME",))
        st.markdown("<p class='side-label'>Home</p>", unsafe_allow_html=True)
    with r1c2:
        st.button("💰", key="a", on_click=nav, args=("ADD",))
        st.markdown("<p class='side-label'>Add</p>", unsafe_allow_html=True)
    with r1c3:
        st.button("📊", key="d", on_click=nav, args=("DATA",))
        st.markdown("<p class='side-label'>Data</p>", unsafe_allow_html=True)

    # വരി 2
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        st.button("🔴", key="db", on_click=nav, args=("DEBTS",))
        st.markdown("<p class='side-label'>Debts</p>", unsafe_allow_html=True)
    with r2c2:
        st.button("📝", key="t", on_click=nav, args=("TASKS",))
        st.markdown("<p class='side-label'>Tasks</p>", unsafe_allow_html=True)
    with r2c3:
        st.button("🌙", key="p", on_click=nav, args=("PEACE",))
        st.markdown("<p class='side-label'>Peace</p>", unsafe_allow_html=True)

    # വരി 3
    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        st.button("⚙️", key="s", on_click=nav, args=("SET",))
        st.markdown("<p class='side-label'>Set</p>", unsafe_allow_html=True)
    with r3c2:
        st.button("🔄", key="r", on_click=st.rerun)
        st.markdown("<p class='side-label'>Sync</p>", unsafe_allow_html=True)
    with r3c3:
        st.button("📞", key="so", on_click=nav, args=("PEACE",))
        st.markdown("<p class='side-label'>SOS</p>", unsafe_allow_html=True)

# --- MAIN CONTENT ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center; color: #ffd700;'>DASHBOARD</h1>", unsafe_allow_html=True)
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        total = pd.to_numeric(df.iloc[:, -1], errors='coerce').sum()
    except: total = 0

    st.markdown(f'''
        <div class="main-card">
            <p style="color: #cbd5e1; margin:0;">TOTAL SPENT</p>
            <h1 style="color: #fff; font-size: 50px;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)

elif st.session_state.page == "ADD":
    st.header("Add Entry")
    # ... entry form logic ...

st.markdown("<p style='text-align: center; color: #475569; margin-top: 50px;'>PAICHI v46.0</p>", unsafe_allow_html=True)
