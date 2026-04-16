import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import numpy as np
import random
import os
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & AUTH ---
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"}
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
TRADE_FILE = 'trade_journal.csv'

st.set_page_config(page_title="PAICHI AI PRO MCX", layout="wide")

# --- 2. 🎨 AI TRADER THEME ---
st.markdown("""
<style>
    .stApp { background: #0a0e14; color: #ffffff; }
    [data-testid="stSidebar"] { background: #000000 !important; border-right: 2px solid #FFD700; }
    .ai-card { background: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; box-shadow: 0 4px 20px rgba(0,0,0,0.8); }
    .price-box { font-size: 55px; font-weight: bold; color: #FFD700; margin: 10px 0; }
    .mcx-label { color: #00FF00; font-size: 18px; font-weight: bold; background: rgba(0,255,0,0.1); padding: 5px 10px; border-radius: 5px; }
    .signal-badge { padding: 15px; border-radius: 10px; font-size: 30px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    li { font-size: 18px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=60000, key="paichi_refresh")

# --- 3. 🤖 MCX AI ENGINE ---
def get_ai_analysis(ticker):
    try:
        # അന്താരാഷ്ട്ര ക്രൂഡ് ഓയിൽ ഡാറ്റ എടുക്കുന്നു
        data = yf.Ticker(ticker).history(period='5d', interval='15m')
        if data.empty: return None
        
        curr_usd = data['Close'].iloc[-1]
        
        # MCX FUTURE CONVERSION (Upstox-ലെ ഏകദേശ വില വരാൻ 97.1 കൊണ്ട് ഗുണിക്കുന്നു)
        final_price = curr_usd * 97.1 if ticker == "CL=F" else curr_usd
        
        # Indicators
        ema = data['Close'].ewm(span=20).mean().iloc[-1]
        
        # RSI Calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))

        # Signal Logic
        score = 0
        details = []
        if data['Close'].iloc[-1] > ema: 
            details.append("🟢 Trend: Price Above 20 EMA (Bullish)")
            score += 1
        else: 
            details.append("🔴 Trend: Price Below 20 EMA (Bearish)")
            score -= 1
        
        if rsi > 55: 
            details.append("⚡ Strength: Bullish Momentum")
            score += 1
        elif rsi < 45: 
            details.append("❄️ Strength: Bearish Pressure")
            score -= 1

        advice = "NEUTRAL ⏳"
        color = "#808080"
        if score >= 2: advice, color = "STRONG BUY 🔥", "#00FF00"
        elif score == 1: advice, color = "BUY ✅", "#4CAF50"
        elif score <= -2: advice, color = "STRONG SELL 🚫", "#FF0000"
        elif score == -1: advice, color = "SELL ❌", "#F44336"

        return {"price": final_price, "rsi": rsi, "advice": advice, "color": color, "details": details}
    except: return None

# --- 4. APP INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI AI TRADER LOGIN")
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u.lower() in USERS and USERS[u.lower()]["pw"] == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            st.rerun()
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        page = st.radio("Menu", ["📊 AI Advisor", "💰 Add Expense", "🔍 View History"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    if page == "📊 AI Advisor":
        st.title("Live Pro Advisor")
        asset = st.selectbox("Market Asset", ["MCX CRUDE OIL", "NIFTY 50 Spot"])
        ticker = "CL=F" if asset == "MCX CRUDE OIL" else "^NSEI"
        
        res = get_ai_analysis(ticker)
        if res:
            label = "ORIGINAL MCX FUTURE (LIVE)" if ticker == "CL=F" else "NIFTY SPOT"
            
            st.markdown(f"""
            <div class="ai-card">
                <div class="signal-badge" style="background: {res['color']}; color: white;">{res['advice']}</div>
                <span class="mcx-label">{label}</span>
                <div class="price-box">₹ {res['price']:,.2f}</div>
                <p style="font-size: 20px;"><b>RSI Level:</b> {res['rsi']:.2f}</p>
                <hr style="border-color: #333;">
                <h4 style="color: #FFD700;">Market Analysis Logic:</h4>
                <ul style="list-style-type: none; padding-left: 0;">{"".join([f"<li>{d}</li>" for d in res['details']])}</ul>
            </div>
            """, unsafe_allow_html=True)
            
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
            st.info(f"Main Balance: ₹{bal:,.2f}")
        except: pass

    elif page == "💰 Add Expense":
        st.title("Quick Expense Tracker")
        v = speech_to_text(language='ml', key='ml_voice_new')
        with st.form("expense_form"):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SUBMIT"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Entry Saved Successfully!")

    elif page == "🔍 View History":
        st.title("Transaction History")
        try:
            dfh = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(dfh.iloc[::-1], use_container_width=True)
        except: st.error("Database connection failed.")

st.markdown("<p style='text-align:center; color: #555; margin-top: 50px;'>PAICHI AI HUB v3.0 | Real-Time MCX Pricing</p>", unsafe_allow_html=True)
