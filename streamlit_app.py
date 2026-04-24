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
import time

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v5.1", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM CSS ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #000000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #000 !important; border-radius: 10px; font-weight: bold; width: 100%;
        border: none; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #FFD700; }
    .balance-banner {
        background: rgba(255, 215, 0, 0.1);
        padding: 20px; border-radius: 20px; border: 1px solid #FFD700;
        text-align: center; margin-bottom: 25px;
    }
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ENGINES & HELPERS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_panther = load_lottieurl("https://lottie.host/81f9537d-9447-4974-98c4-e86749963721/nQ8Yw2rS6r.json")

def get_exchange_rate():
    try:
        data = yf.Ticker("AEDINR=X").history(period="1d")
        return data['Close'].iloc[-1]
    except: return 22.70 # Default

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

# --- 4. AUTH & MAIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_panther: st_lottie(lottie_panther, height=250, key="panther")
        st.markdown("<h2 style='text-align:center;'>PAICHI VAULT LOGIN</h2>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("UNLOCK"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    # Sidebar Info
    rate = get_exchange_rate()
    st.sidebar.markdown(f"### 🇦🇪 AED to INR: ₹{rate:.2f}")
    st.sidebar.divider()
    
    curr_user = st.session_state.user
    balance = get_total_balance()
    
    st.markdown(f"""<div class="balance-banner">
        <p style="margin:0; font-size:16px; color:#E0B0FF;">Total Vault Balance</p>
        <h1 style="margin:0; font-size:42px; color:#FFD700;">₹{balance:,.2f}</h1>
    </div>""", unsafe_allow_html=True)

    page = st.sidebar.radio("Navigation", ["💰 Add Entry", "📊 Advisor", "🏠 Dashboard", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("🎙️ Quick Entry")
        v_raw = speech_to_text(language='ml', key='v_v5.1')
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description")
            am_str = st.text_input("Amount")
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("CONFIRM TRANSACTION"):
                try:
                    am = float(am_str)
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    
                    # Push Notification (Toast)
                    st.toast(f'Processing ₹{am} Transaction...', icon='⏳')
                    
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    time.sleep(1)
                    st.toast(f'Successfully Saved to Vault!', icon='✅')
                    st.balloons()
                    
                    threading.Thread(target=send_wa, args=(f"💰 *Transaction Alert*\nAmt: ₹{am}\nRef: {it}\nBal: ₹{balance + (c-d):,.2f}",)).start()
                except: st.error("Amount തെറ്റാണ്!")

    elif page == "📊 Advisor":
        st.title("Trading Advisor 🚀")
        # Previous Trading Engine Logic...
        st.info("Market Data refreshing in 60s")

    elif page == "🏠 Dashboard":
        st.title("Analytics 📊")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            df['Category'] = df['Item'].apply(lambda x: str(x).split(':')[0] if ':' in str(x) else 'Other')
            fig = px.pie(df[df['Debit']>0], values='Debit', names='Category', hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
        except: st.write("Data loading errors...")

    elif page == "🔍 History":
        st.title("Recent Activity 📜")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("History empty.")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
