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

st.set_page_config(page_title="PAICHI AI PRO", layout="wide")

# --- 2. 🎨 AI DARK THEME ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a, #1e293b); color: #ffffff; }
    [data-testid="stSidebar"] { background: #000000 !important; border-right: 2px solid #FFD700; }
    .stButton>button { background: #FFD700 !important; color: #000 !important; font-weight: bold; border-radius: 10px; }
    .info-box { background: rgba(255, 215, 0, 0.1); padding: 10px; border-radius: 10px; border: 1px solid #FFD700; color: #FFD700; text-align: center; margin-bottom: 8px; }
    .ai-card { background: #1e293b; padding: 20px; border-radius: 15px; border: 2px solid #FFD700; margin-bottom: 20px; }
    .balance-box { background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #FFD700; font-size: 22px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="paichi_refresh")

# --- 3. 🤖 AI ENGINE (ALL INDICATORS) ---
def get_advanced_ai_advice(ticker):
    try:
        data = yf.Ticker(ticker).history(period='5d', interval='15m')
        if data.empty: return None

        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))

        # EMA 20 & VWAP
        current_price = data['Close'].iloc[-1]
        ema_20 = data['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        data['tp'] = (data['High'] + data['Low'] + data['Close']) / 3
        vwap = (data['tp'] * data['Volume']).sum() / data['Volume'].sum()

        # MACD
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = (exp1 - exp2).iloc[-1]
        signal = (exp1 - exp2).ewm(span=9, adjust=False).mean().iloc[-1]

        # Scoring Logic
        score = 0
        details = []
        if rsi > 70: details.append("⚠️ Overbought (RSI > 70)"); score -= 1
        elif rsi < 30: details.append("✅ Oversold (RSI < 30)"); score += 1
        
        if current_price > ema_20: details.append("📈 Bullish: Above 20 EMA"); score += 1
        else: details.append("📉 Bearish: Below 20 EMA"); score -= 1

        if current_price > vwap: details.append("💎 Price above VWAP (Strong)"); score += 1
        
        if macd > signal: details.append("🚀 MACD Bullish Crossover"); score += 1

        advice = "⏳ NEUTRAL"
        if score >= 2: advice = "🔥 STRONG BUY"
        elif score == 1: advice = "✅ BUY"
        elif score <= -2: advice = "🚫 STRONG SELL"
        elif score == -1: advice = "❌ SELL"

        return {"price": current_price, "rsi": rsi, "advice": advice, "details": details}
    except: return None

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI AI HUB LOGIN")
    u = st.text_input("Username").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u in USERS and USERS[u]["pw"] == p:
            st.session_state.auth, st.session_state.user, st.session_state.role = True, u.capitalize(), USERS[u]["role"]
            st.rerun()
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        if st.session_state.role == "admin":
            st.write("📊 **Quick Market**")
            for t in ["AEDINR=X", "CL=F", "^NSEI"]:
                p = yf.Ticker(t).history(period='1d')['Close'].iloc[-1]
                st.markdown(f'<div class="info-box">{t}: {p:,.2f}</div>', unsafe_allow_html=True)
        
        menu = ["🏠 AI Dashboard", "💰 Add Entry", "📈 Trade Journal", "🔍 Search"] if st.session_state.role == "admin" else ["💰 Add Entry"]
        page = st.radio("Menu", menu)
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- 🏠 AI DASHBOARD ---
    if page == "🏠 AI Dashboard":
        st.title("🤖 AI Pro Advisor")
        asset = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "CL=F", "AEDINR=X"])
        res = get_advanced_ai_advice(asset)
        
        if res:
            st.markdown(f"""
            <div class="ai-card">
                <h1 style="color: #FFD700;">{res['advice']}</h1>
                <h3>Price: {res['price']:,.2f} | RSI: {res['rsi']:.2f}</h3>
                <ul>{"".join([f"<li>{d}</li>" for d in res['details']])}</ul>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
            col1.markdown(f'<div class="balance-box">Family Bal: ₹{bal:,.0f}</div>', unsafe_allow_html=True)
        except: st.error("Sync Error")
        
        if os.path.exists(TRADE_FILE):
            tdf = pd.read_csv(TRADE_FILE)
            col2.markdown(f'<div class="balance-box">Trade P&L: ₹{tdf["P&L"].sum():,.0f}</div>', unsafe_allow_html=True)

    # --- 💰 ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("Transaction Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")

    # --- 📈 TRADE JOURNAL ---
    elif page == "📈 Trade Journal":
        st.title("Trading Log")
        with st.form("trade"):
            idx = st.selectbox("Asset", ["NIFTY", "BANKNIFTY", "CRUDE"])
            e, ex, q = st.number_input("Entry"), st.number_input("Exit"), st.number_input("Qty", step=1)
            if st.form_submit_button("LOG"):
                pnl = (ex - e) * q
                pd.DataFrame([[datetime.now().strftime("%d-%m %H:%M"), idx, e, ex, q, pnl]], columns=['Date','Asset','Entry','Exit','Qty','P&L']).to_csv(TRADE_FILE, mode='a', header=not os.path.exists(TRADE_FILE), index=False)
                st.success(f"P&L: ₹{pnl}")

    # --- 🔍 SEARCH ---
    elif page == "🔍 Search":
        st.title("History")
        search = st.text_input("Search...")
        try:
            dfs = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(dfs[dfs['Item'].str.contains(search, case=False, na=False)].iloc[::-1] if search else dfs.iloc[::-1], use_container_width=True)
        except: st.error("Error")

st.markdown("<p style='text-align:center;'>Created by Faisal Arakkal</p>", unsafe_allow_html=True)
# --- AI ENGINE UPDATE (MCX & IMPROVED SIGNALS) ---
def get_advanced_ai_advice(ticker):
    try:
        data = yf.Ticker(ticker).history(period='5d', interval='15m')
        if data.empty: return None

        # RSI Calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))

        # Price, EMA, VWAP
        current_price = data['Close'].iloc[-1]
        ema_20 = data['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        data['tp'] = (data['High'] + data['Low'] + data['Close']) / 3
        vwap = (data['tp'] * data['Volume']).sum() / data['Volume'].sum()

        # MACD
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = (exp1 - exp2).iloc[-1]
        signal = (exp1 - exp2).ewm(span=9, adjust=False).mean().iloc[-1]

        # Final Scoring & Signal Details
        score = 0
        details = []
        
        # 1. Trend Analysis
        if current_price > ema_20: details.append("📈 Price above 20 EMA"); score += 1
        else: details.append("📉 Price below 20 EMA"); score -= 1

        # 2. Volume Analysis
        if current_price > vwap: details.append("💎 Strong Volume (Above VWAP)"); score += 1
        else: details.append("⚠️ Weak Volume (Below VWAP)"); score -= 1

        # 3. Momentum Analysis
        if macd > signal: details.append("🚀 MACD Bullish Crossover"); score += 1
        else: details.append("🔻 MACD Bearish Crossover"); score -= 1

        # 4. Strength Analysis
        if rsi > 60: details.append("🔥 RSI High (Strong)"); score += 1
        elif rsi < 40: details.append("❄️ RSI Low (Weak)"); score -= 1

        # Decision Making
        if score >= 2: advice = "🔥 STRONG BUY"
        elif score == 1: advice = "✅ BUY"
        elif score <= -2: advice = "🚫 STRONG SELL"
        elif score == -1: advice = "❌ SELL"
        else: advice = "⏳ NEUTRAL"

        return {"price": current_price, "rsi": rsi, "advice": advice, "details": details}
    except:
        return None
