import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import io

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal123", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI SMOKY GLASS v4.8", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN (Smoky Glass Sidebar) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521);
        color: #fff;
    }
    
    /* 🌫️ SMOKY GLASS SIDEBAR (Transparent Black) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.4) !important; /* Karuppu niram pakshe transparent anu */
        backdrop-filter: blur(15px); /* Pinnilulla karyangal kanikkaan blur nalkunnu */
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar content transparency */
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    .stButton>button {
        background-color: #FFD700;
        color: #000;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 25px;
        border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 TRIPLE INDICATOR ENGINE ---
def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            atr = (df['High'] - df['Low']).rolling(window=10).mean().iloc[-1]
            lower_band = ((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr)
            st_buy = last_p > lower_band
            
            if last_p > pivot and rsi > 55 and st_buy: signal, color = "🚀 BUY", "#00FF00"
            elif last_p < pivot and rsi < 45 and not st_buy: signal, color = "📉 SELL", "#FF3131"
            else: signal, color = "⚖️ WAIT", "#FFFF00"
            
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": rsi, "color": color})
        return results
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    st.sidebar.title(f"👤 {curr_user.capitalize()}")
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor" and curr_user != "shabana":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f"""
                <div class="purple-box" style="border-color: {m['color']} !important;">
                    <h2 style="color:#E0B0FF !important; font-size:35px; margin-bottom:5px;">{m["name"]}</h2>
                    <h1 style="color:{m["color"]} !important; font-size:65px; margin:10px 0px;">{m["signal"]}</h1>
                    <h1 style="color:#FFD700 !important; font-size:60px; margin-bottom:10px;">₹{m["price"]:,.0f}</h1>
                    <p style="color:#ffffff !important; font-size:25px;">RSI: {m["rsi"]:.1f}</p>
                </div>
                """, unsafe_allow_html=True)

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Financial Status")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            balance = total_in - total_out
            st.markdown(f"""
            <div class="purple-box" style="border-color: #FFD700 !important;">
                <p style="color:#E0B0FF !important; font-size:20px;">Net Balance
