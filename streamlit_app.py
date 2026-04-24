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

st.set_page_config(page_title="PAICHI PURPLE GOLD v5.2", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM CSS (Black Glass Sidebar & Animations) ---
st.markdown("""
    <style>
    /* Main Background */
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

    /* Black Glass Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* Balance Banner */
    .balance-banner {
        background: rgba(255, 215, 0, 0.1);
        padding: 20px; border-radius: 20px; border: 1px solid #FFD700;
        text-align: center; margin-bottom: 25px;
    }
    h1, h2, h3, p, label, .stMarkdown { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ENGINES & HELPERS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# Animations
lottie_panther = load_lottieurl("https://lottie.host/81f9537d-9447-4974-98c4-e86749963721/nQ8Yw2rS6r.json")
lottie_cash = load_lottieurl("https://lottie.host/869e5d4e-b5f7-4184-8840-062639097723/P6v68xT1N3.json") # Money flying animation

def get_exchange_rate():
    try:
        data = yf.Ticker("AEDINR=X").history(period="1d")
        return data['Close'].iloc[-1]
    except: return 22.75

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

# --- 4. APP MAIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_panther: st_lottie(lottie_panther, height=250, key="panther")
        st.markdown("<h2 style='text-align:center;'>PAICHI VAULT</h2>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("UNLOCK"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    # Sidebar Setup
    with st.sidebar:
        st.markdown("### 🏦 FINANCE HUB")
        rate = get_exchange_rate()
        st.metric(label="AED to INR", value=f"₹{rate:.2f}")
        st.divider()
        page = st.radio("SELECT PAGE", ["💰 Add Entry", "📊 Advisor", "🏠 Dashboard", "🔍 History"])
        st.divider()
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    balance = get_total_balance()
    st.markdown(f"""<div class="balance-banner">
        <p style="margin:0; font-size:16px; color:#E0B0FF;">Total Vault Balance</p>
        <h1 style="margin:0; font-size:42px; color:#FFD700;">₹{balance:,.2f}</h1>
    </div>""", unsafe_allow_html=True)

    if page == "💰 Add Entry":
        st.title("🎙️ Smart Voice Entry")
        
        # Cash Animation at top of page
        if lottie_cash:
            st_lottie(lottie_cash, height=150, key="cash_rain")
            
        v_raw = speech_to_text(language='ml', key='v_v5.2')
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description (എന്തിനു വേണ്ടി?)")
            am_str = st.text_input("Amount (എത്ര രൂപ?)")
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE TO VAULT"):
                try:
                    am = float(am_str)
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
                    
                    st.toast(f'Processing ₹{am}...', icon='💸')
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    st.toast('Transaction Confirmed!', icon='✅')
                    st.snow() # പണം പറക്കുന്ന പോലെ മഞ്ഞ് വീഴുന്ന ഇഫക്ട്
                    
                    threading.Thread(target=send_wa, args=(f"💰 *Entry Saved*\nUser: {st.session_state.user}\nAmt: ₹{am}\nBal: ₹{balance + (c-d):,.2f}",)).start()
                except: st.error("Amount കൃത്യമായി നൽകുക")

    elif page == "📊 Advisor":
        st.title("Trading Advisor 🚀")
        st.info("Market data is live.")

    elif page == "🏠 Dashboard":
        st.title("Analytics 📊")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            fig = px.pie(df[df['Debit']>0], values='Debit', names='Item', hole=0.5)
            st.plotly_chart(fig, use_container_width=True)
        except: st.write("Loading data...")

    elif page == "🔍 History":
        st.title("History 📜")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("No entries found.")
