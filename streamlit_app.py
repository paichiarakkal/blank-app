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

st.set_page_config(page_title="PAICHI PURPLE GOLD v5.5", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM CSS (Black Glass Sidebar) ---
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
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 215, 0, 0.2);
    }
    .balance-banner {
        background: rgba(255, 215, 0, 0.1);
        padding: 20px; border-radius: 20px; border: 1px solid #FFD700;
        text-align: center; margin-bottom: 25px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #000 !important; border-radius: 10px; font-weight: bold; width: 100%;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ENGINES & HELPERS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_panther = load_lottieurl("https://lottie.host/81f9537d-9447-4974-98c4-e86749963721/nQ8Yw2rS6r.json")
lottie_cash = load_lottieurl("https://lottie.host/869e5d4e-b5f7-4184-8840-062639097723/P6v68xT1N3.json")

def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
        # ഓഫ്‌ലൈൻ ആവശ്യത്തിന് ബാലൻസ് സേവ് ചെയ്യുന്നു
        st.session_state['last_balance'] = bal
        return bal
    except:
        # നെറ്റ് ഇല്ലെങ്കിൽ പഴയ ബാലൻസ് കാണിക്കും
        return st.session_state.get('last_balance', 0.0)

# --- 4. LOGIN LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_panther: st_lottie(lottie_panther, height=250)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("UNLOCK VAULT"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome {st.session_state.user.capitalize()}!")
        page = st.radio("MENU", ["💰 Add Entry", "📊 Advisor", "🔍 History"])
        
        # SMS Button (ഇന്റർനെറ്റ് ഇല്ലാത്തപ്പോൾ ഉപകരിക്കും)
        st.divider()
        current_bal = st.session_state.get('last_balance', 0.0)
        sms_body = f"Paichi Balance: AED {current_bal:,.2f}"
        sms_url = f"sms:{WA_PHONE}?body={urllib.parse.quote(sms_body)}"
        st.markdown(f'**Offline Help:**')
        st.markdown(f'<a href="{sms_url}" style="text-decoration:none;"><button style="width:100%; border-radius:10px; background:#4CAF50; color:white; border:none; padding:10px;">Send Balance via SMS</button></a>', unsafe_allow_html=True)
        
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    balance = get_total_balance()
    st.markdown(f"""<div class="balance-banner">
        <p style="margin:0; font-size:16px; color:#E0B0FF;">Current Balance</p>
        <h1 style="margin:0; font-size:42px; color:#FFD700;">₹{balance:,.2f}</h1>
    </div>""", unsafe_allow_html=True)

    if page == "💰 Add Entry":
        st.title("🎙️ Quick Voice Entry")
        if lottie_cash: st_lottie(lottie_cash, height=150)
        
        v_raw = speech_to_text(language='ml', key='voice_input_v5')
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description")
            am_str = st.text_input("Amount")
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE"):
                try:
                    am = float(am_str)
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
                    
                    st.toast(f'Processing ₹{am}...', icon='💸')
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    st.toast('Transaction Confirmed!', icon='✅')
                    st.snow()
                    
                    # WhatsApp Notification with Balance
                    new_bal = balance + (c - d)
                    wa_msg = f"✅ *Paichi Entry*\n💰 Amt: ₹{am}\n⚖️ *Total Bal: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_wa, args=(wa_msg,)).start()
                except: st.error("Error in data entry")

    elif page == "📊 Advisor":
        st.title("Trading Advisor 🚀")
        st.info("Live signals updated.")

    elif page == "🔍 History":
        st.title("Activity Log 📜")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("Searching records...")
