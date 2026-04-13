import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. Settings
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"
MY_NUMBER = "918714752210"

# സൈഡ്‌ബാർ തിരികെ കൊണ്ടുവന്നു
st.set_page_config(page_title="PAICHI SIDE-OS", layout="wide", initial_sidebar_state="expanded")

# --- 🌗 SIDEBAR ICON UI DESIGN ---
st.markdown("""
    <style>
    .stApp { background: #000000; color: #ffffff; }
    
    /* സൈഡ്‌ബാർ സ്റ്റൈൽ */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #ffd700;
        min-width: 150px !important;
    }

    /* സൈഡ്‌ബാറിലെ റൗണ്ട് ബട്ടണുകൾ */
    .stSidebar .stButton > button {
        background: #1a1a1a !important;
        color: #ffd700 !important;
        border: 2px solid #333 !important;
        border-radius: 50% !important; /* റൗണ്ട് ആക്കി */
        height: 80px !important;
        width: 80px !important;
        margin: 10px auto !important;
        display: flex !important;
        font-size: 25px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    
    .stSidebar .stButton > button:active {
        transform: scale(0.9);
        border-color: #ffd700 !important;
    }

    /* സൈഡ്‌ബാറിലെ ലേബൽ */
    .side-label {
        text-align: center;
        font-size: 10px;
        color: #888;
        font-weight: bold;
        margin-bottom: 15px;
        text-transform: uppercase;
    }

    .main-card {
        background: #0d0d0d;
        padding: 30px;
        border-radius: 25px;
        border: 1px solid #ffd700;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAV LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def nav(p):
    st.session_state.page = p

# --- 🏰 SIDEBAR DRAWER (Round Icons) ---
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #ffd700;'>MENU</h3>", unsafe_allow_html=True)
    st.write("---")
    
    # ഓരോ ഐക്കണും അതിനു താഴെ പേരും
    st.button("🏠", on_click=nav, args=("🏠 HOME",))
    st.markdown("<p class='side-label'>HOME</p>", unsafe_allow_html=True)

    st.button("💰", on_click=nav, args=("ADD",))
    st.markdown("<p class='side-label'>ADD ENTRY</p>", unsafe_allow_html=True)

    st.button("📊", on_click=nav, args=("DATA",))
    st.markdown("<p class='side-label'>REPORTS</p>", unsafe_allow_html=True)

    st.button("🌙", on_click=nav, args=("PEACE",))
    st.markdown("<p class='side-label'>PEACE</p>", unsafe_allow_html=True)

    st.button("🔄", on_click=st.rerun)
    st.markdown("<p class='side-label'>REFRESH</p>", unsafe_allow_html=True)

# --- 🏠 MAIN CONTENT AREA ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h1 style='color: #ffd700;'>PAICHI AI</h1>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="main-card">
            <p style="color: #555; font-size: 14px; margin:0;">CURRENT BALANCE / SPENT</p>
            <h1 style="color: #fff; font-size: 50px; margin:10px 0;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)
    st.info("സൈഡ്‌ബാറിലെ ഐക്കണുകൾ ഉപയോഗിച്ച് പേജുകൾ മാറ്റാം.")

elif st.session_state.page == "ADD":
    st.header("📥 Add Transaction")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    with st.form("entry"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("Data Saved!")

elif st.session_state.page == "DATA":
    st.header("📊 Financial Data")
    try:
        df = pd.read_csv(CSV_URL)
        st.dataframe(df, use_container_width=True)
    except: st.error("No Data found.")

elif st.session_state.page == "PEACE":
    st.header("🌙 Peace Mode")
    st.write("Morning greetings and more...")

st.markdown("<br><p style='text-align: center; color: #222;'>PAICHI OS v44.0 | Side-Icon Edition</p>", unsafe_allow_html=True)
