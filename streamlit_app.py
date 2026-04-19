import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI ULTIMATE v8.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 YOUR EXACT COLOR THEME ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521);
        color: #fff;
    }
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.85) !important;
        backdrop-filter: blur(10px);
    }
    .stButton>button {
        background-color: #FFD700;
        color: #000;
        border-radius: 10px;
        font-weight: bold;
    }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 25px;
        border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center;
        margin-bottom: 25px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 MARKET DATA ENGINE ---
def get_market_data():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = {}
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="1d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            if name == "Crude Fut": last_p = round(last_p * 83.5 * 1.15, 0)
            else: last_p = round(last_p, 0)
            results[name] = last_p
        return results
    except: return None

# --- 4. APP LOGIC ---
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
    
    # 🔒 Shabana Restriction (Add Entry Only)
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        st.sidebar.title(f"👤 {curr_user.capitalize()}")
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History", "🤝 Debt Tracker"])

    # --- PAGES ---
    if page == "💰 Add Entry":
        st.title("Quick Add Transaction")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Details", value=v if v else "")
            # എക്സ്ട്രാ പൂജ്യങ്ങൾ ഒഴിവാക്കി
            am = st.number_input("Amount", min_value=0, step=1, value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {it}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    })
                    st.success("സേവ് ചെയ്തു! ✅")

    elif page == "📊 Advisor" and curr_user != "shabana":
        st.title("Live Trading Advisor")
        markets = get_market_data()
        if markets:
            for name, price in markets.items():
                st.markdown(f"""
                <div class="purple-box">
                    <h3>{name}</h3>
                    <h1 style="color:#FFD700;">₹{price:,.0f}</h1>
                </div>
                """, unsafe_allow_html=True)

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Financial Overview")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            st.markdown(f"""
            <div class="purple-box">
                <p>Net Balance</p>
                <h1 style="color:#FFD700;">₹{total_in - total_out:,.0f}</h1>
            </div>
            """, unsafe_allow_html=True)
        except: st.error("Data error!")

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("Loading...")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
