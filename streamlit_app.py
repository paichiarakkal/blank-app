import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re
import urllib.parse
import threading
from streamlit_lottie import st_lottie

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v5.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 ANIMATED PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #1A0521, #4B0082, #2D0844, #000000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #fff;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .purple-box {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 25px; border-radius: 20px; 
        border: 1px solid rgba(255, 215, 0, 0.3);
        text-align: center; margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .purple-box:hover { transform: translateY(-5px); border-color: #FFD700; }
    .balance-banner {
        background: rgba(255, 215, 0, 0.1);
        padding: 20px; border-radius: 20px; border: 1px solid #FFD700;
        text-align: center; margin-bottom: 30px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(255, 215, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: black !important; border-radius: 12px; font-weight: bold; border: none;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER ENGINES ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_loading = load_lottieurl("https://lottie.host/8593444a-f31d-4886-993d-4c3e800d3d5f/q8o4xV3V3v.json")

def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
    except: return 0.0

def process_voice(text):
    if not text: return "Others", None, ""
    raw_text = text.lower()
    nums = re.findall(r'\d+', raw_text)
    amount = float(nums[0]) if nums else None
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "hotel"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട"]): category = "Shop"
    return category, amount, clean_desc

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_loading: st_lottie(lottie_loading, height=200)
        st.markdown("<h2 style='text-align: center;'>🔐 PAICHI LOGIN</h2>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("ENTER VAULT"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    balance = get_total_balance()
    
    st.markdown(f"""<div class="balance-banner">
        <p style="margin:0; font-size:18px; color:#E0B0FF;">Available Balance</p>
        <h1 style="margin:0; font-size:45px; color:#FFD700;">₹{balance:,.2f}</h1>
    </div>""", unsafe_allow_html=True)

    page = st.sidebar.radio("MENU", ["💰 Add Entry", "📊 Advisor", "🏠 Dashboard", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Voice Assistant 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_input')
        v_cat, v_amt, v_desc = process_voice(v_raw)

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am = st.text_input("Amount", value=str(v_amt) if v_amt else "")
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Rent", "Others"], index=4)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE DATA"):
                try:
                    val = float(am)
                    d, c = (val, 0) if ty == "Debit" else (0, val)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    st.balloons()
                    st.success("Success! ✅")
                    threading.Thread(target=send_wa, args=(f"✅ *New Entry*\n💰 ₹{val}\n📝 {it}",)).start()
                except: st.error("Enter valid amount")

    elif page == "📊 Advisor":
        st.title("Trading Signals 🚀")
        # Add your Advisor Logic here (From previous version)
        st.write("Market signals loading...")

    elif page == "🏠 Dashboard":
        st.title("Statistics 📈")
        st.write("Visual analytics and pie charts...")

    elif page == "🔍 History":
        st.title("History 📜")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Wait for data...")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
