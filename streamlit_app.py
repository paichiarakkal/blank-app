import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. WHATSAPP ---
def send_wa(item, amount):
    api_key = "7463030" 
    phone = "971551347989"
    msg = f"📝 Item: {item}\n💰 Amount: {amount}"
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(msg)}&apikey={api_key}"
    try: requests.get(url, timeout=10)
    except: pass

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700 !important; color: #000 !important; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📊 Advisor", "🔍 History"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    if page == "💰 Add Entry":
        st.title("Add New Entry")
        v_raw = speech_to_text(language='ml', key='v_v1')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_raw if v_raw else "")
            am = st.number_input("Amount", min_value=0.0)
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Chicken", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    send_wa(it, am)
                    st.success("Saved! ✅")
                    st.rerun()

    elif page == "🏠 Dashboard":
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            bal = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum() - pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            st.markdown(f'<div class="balance-banner"><h1>Available Balance</h1><h1 style="color:#FFD700;">₹{bal:,.2f}</h1></div>', unsafe_allow_html=True)
        except: st.write("Loading...")

    elif page == "🔍 History":
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Error")

    elif page == "📊 Advisor":
        st.title("Trading Advisor")
        st.write("Live signals ready.")
