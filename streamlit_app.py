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

st.set_page_config(page_title="PAICHI ULTIMATE v12.1", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #1A0521); color: #fff; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 15px; border: 2px solid #FFD700;
        text-align: center; margin-bottom: 15px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. FUNCTIONS ---
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return None

def get_market_signals():
    results = []
    for name, sym in {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}.items():
        try:
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            lp = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            delta = df['Close'].diff()
            rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean()).iloc[-1]))
            atr = (df['High'] - df['Low']).rolling(10).mean().iloc[-1]
            st_buy = lp > (((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr))
            
            if lp > pivot and rsi > 55 and st_buy: sig, col = "🚀 BUY", "#00FF00"
            elif lp < pivot and rsi < 45 and not st_buy: sig, col = "📉 SELL", "#FF3131"
            else: sig, col = "⚖️ WAIT", "#FFFF00"
            
            if name == "Crude Fut": lp = lp * 83.5 * 1.15
            results.append({"name": name, "price": lp, "sig": sig, "rsi": rsi, "col": col})
        except: continue
    return results

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    curr_user = st.session_state.user
    df = load_data()
    
    if curr_user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if page == "📊 Advisor":
        st.title("Smart Advisor")
        signals = get_market_signals()
        for s in signals:
            st.markdown(f'<div class="purple-box" style="border-color:{s["col"]} !important;"><h3>{s["name"]}</h3><h1 style="color:{s["col"]} !important;">{s["sig"]}</h1><h2>₹{s["price"]:,.0f}</h2><p>RSI: {s["rsi"]:.1f}</p></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Add Transaction")
        v = speech_to_text(language='ml', key='v')
        with st.form("entry_form"):
            it = st.text_input("Details", value=v if v else "")
            am = st.number_input("Amount", min_value=1, value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE TO SHEET"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                    st.success("Saved! ✅"); st.rerun()

    elif page == "🏠 Dashboard":
        if df is not None:
            bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
            st.markdown(f'<div class="purple-box"><h1>Balance: ₹{bal:,.0f}</h1></div>', unsafe_allow_html=True)

    elif page == "🔍 History":
        if df is not None: st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
