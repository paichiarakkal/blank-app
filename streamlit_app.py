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

st.set_page_config(page_title="PAICHI NAVY", layout="wide", initial_sidebar_state="expanded")

# --- 🔵 NAVY BLUE & GOLD UI ---
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് - കറുപ്പിന് പകരം നേവി ബ്ലൂ */
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    
    /* സൈഡ്‌ബാർ - ഡാർക്ക് ബ്ലൂ */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 2px solid #ffd700;
    }
    
    /* സൈഡ്‌ബാറിലെ ഓരോ സെക്ഷനും */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        background-color: #1e293b !important;
    }

    /* റൗണ്ട് ഐക്കൺ ബട്ടണുകൾ - നല്ല വ്യക്തതയുള്ള കളർ */
    .stSidebar .stButton > button {
        background-color: #334155 !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
        border-radius: 50% !important; 
        height: 75px !important;
        width: 75px !important;
        margin: 10px auto !important;
        display: flex !important;
        align-items: center;
        justify-content: center;
        font-size: 24px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .stSidebar .stButton > button:active {
        transform: scale(0.9);
        background-color: #ffd700 !important;
        color: #000000 !important;
    }

    /* ലേബൽ കളർ - വെള്ള */
    .side-label {
        text-align: center;
        font-size: 11px;
        color: #ffffff !important;
        font-weight: bold;
        margin-bottom: 20px;
        text-transform: uppercase;
    }

    .main-card {
        background-color: #1e293b;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #ffd700;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def nav(p):
    st.session_state.page = p

# --- SIDEBAR ICON DRAWER ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>PAICHI</h2>", unsafe_allow_html=True)
    st.write("---")
    
    st.button("🏠", on_click=nav, args=("🏠 HOME",))
    st.markdown("<p class='side-label'>Home</p>", unsafe_allow_html=True)

    st.button("💰", on_click=nav, args=("ADD",))
    st.markdown("<p class='side-label'>Add Entry</p>", unsafe_allow_html=True)

    st.button("📊", on_click=nav, args=("DATA",))
    st.markdown("<p class='side-label'>Reports</p>", unsafe_allow_html=True)

    st.button("🌙", on_click=nav, args=("PEACE",))
    st.markdown("<p class='side-label'>Peace</p>", unsafe_allow_html=True)

    st.button("🔄", on_click=st.rerun)
    st.markdown("<p class='side-label'>Refresh</p>", unsafe_allow_html=True)

# --- MAIN CONTENT ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center; color: #ffd700;'>DASHBOARD</h1>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="main-card">
            <p style="color: #cbd5e1; font-size: 14px; margin:0;">TOTAL EXPENDITURE</p>
            <h1 style="color: #fff; font-size: 55px; margin:10px 0;">₹ {total:,.2f}</h1>
            <div style="width: 60px; height: 4px; background: #ffd700; margin: 0 auto;"></div>
        </div>
    ''', unsafe_allow_html=True)

elif st.session_state.page == "ADD":
    st.markdown("<h2 style='color: #ffd700;'>📥 Add Transaction</h2>", unsafe_allow_html=True)
    
    v_text = ""
    if speech_to_text:
        v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    
    with st.form("entry_form"):
        item = st.text_input("Item Name", value=v_text if v_text else "")
        amt = st.number_input("Amount (₹)", min_value=0)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                st.success("സേവ് ചെയ്തു! ✅")

else:
    st.title(st.session_state.page)
    st.info("ഈ പേജ് റെഡിയാണ്! 🟢")

st.markdown("<br><p style='text-align: center; color: #475569;'>PAICHI NAVY v45.0</p>", unsafe_allow_html=True)
