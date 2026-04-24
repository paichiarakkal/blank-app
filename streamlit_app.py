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

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# WhatsApp Config
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI v4.4", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. SMART ENGINES ---

def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except: return 0.0

def process_voice(text):
    if not text: return "Others", None, ""
    raw_text = text.lower()
    nums = re.findall(r'\d+', raw_text)
    amount = float(nums[0]) if nums else None
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    category = "Others"
    if any(x in raw_text for x in ["food", "tea", "ചായ"]): category = "Food"
    elif any(x in raw_text for x in ["rent", "വാടക"]): category = "Rent"
    return category, amount, clean_desc

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    balance = get_total_balance()
    st.markdown(f"""<div class="balance-banner">
        <span style="font-size:18px; color:#E0B0FF;">Total Balance</span><br>
        <span style="font-size:32px; color:#FFD700;">₹{balance:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    page = st.sidebar.radio("Menu", ["💰 Add Entry", "🏠 Dashboard", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Add Transaction 🎙️")
        v_raw = speech_to_text(language='ml', key='v44')
        v_cat, v_amt, v_desc = process_voice(v_raw)

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=v_desc if v_desc else "")
            am = st.number_input("Amount", min_value=0.0, value=v_amt if v_amt else 0.0)
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE & NOTIFY"):
                if am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    new_bal = balance + (c - d)
                    full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
                    
                    # Save to Google Sheets
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    # Send WhatsApp Notification
                    wa_msg = f"✅ *Paichi Entry*\n📂 {cat}\n📝 {it}\n💰 ₹{am}\n⚖️ *Bal: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_wa, args=(wa_msg,)).start()
                    
                    st.success(f"Saved! New Balance: ₹{new_bal:,.2f}"); st.rerun()

    elif page == "🔍 History":
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("No history.")
