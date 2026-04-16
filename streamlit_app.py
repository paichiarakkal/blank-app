import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import numpy as np
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
USERS = {"faisal": {"pw": "faisal123", "role": "admin"}}
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI AI PRO", layout="wide")

# 🚀 3 സെക്കൻഡിൽ ഓട്ടോ റിഫ്രഷ് (ലൈവ് ഫീൽ കിട്ടാൻ)
st_autorefresh(interval=3000, key="paichi_ultra_live")

# --- 2. 🤖 MCX ULTRA-FAST ENGINE ---
def get_ai_analysis(multiplier):
    try:
        ticker = "CL=F"
        # 🎯 കൃത്യതയ്ക്കായി 1-minute ഇന്റർവെൽ ഉപയോഗിക്കുന്നു
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        if data.empty: return None
        
        curr_usd = data['Close'].iloc[-1]
        final_price = curr_usd * multiplier
        
        # ഇൻട്രാഡേ സിഗ്നലുകൾ (Upstox ചാർട്ടുമായി പൊരുത്തപ്പെടാൻ)
        ema_fast = data['Close'].ewm(span=9).mean().iloc[-1]
        ema_slow = data['Close'].ewm(span=21).mean().iloc[-1]
        
        # RSI (14 period)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))

        # 🔥 SIGNAL LOGIC
        score = 0
        details = []
        
        # Trend Logic (EMA Cross similar to SuperTrend)
        if curr_usd > ema_fast: 
            details.append("🟢 UpTrend (Price > EMA 9)")
            score += 1
        else: 
            details.append("🔴 DownTrend (Price < EMA 9)")
            score -= 1
            
        # Momentum Logic
        if rsi > 60: 
            details.append("⚡ Strong Buy Momentum")
            score += 1
        elif rsi < 40: 
            details.append("❄️ Strong Sell Pressure")
            score -= 1

        advice, color = ("STRONG BUY 🔥", "#00FF00") if score >= 2 else \
                        ("BUY ✅", "#4CAF50") if score == 1 else \
                        ("STRONG SELL 🚫", "#FF0000") if score <= -2 else \
                        ("SELL ❌", "#F44336") if score == -1 else ("NEUTRAL ⏳", "#808080")

        return {"price": final_price, "rsi": rsi, "advice": advice, "color": color, "details": details}
    except: return None

# --- 3. UI INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if u.lower() in USERS and USERS[u.lower()]["pw"] == p:
            st.session_state.auth = True
            st.rerun()
else:
    with st.sidebar:
        st.header("👤 Faisal")
        # വില അപ്സ്റ്റോക്സുമായി ഒത്തുപോകാൻ ഇത് അഡ്ജസ്റ്റ് ചെയ്യുക
        f_val = st.number_input("Price Factor", value=96.2, step=0.1)
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    res = get_ai_analysis(f_val)
    if res:
        st.markdown(f"""
        <div style="background: #161b22; padding: 25px; border-radius: 15px; border: 2px solid {res['color']}; text-align: center;">
            <div style="background: {res['color']}; color: white; padding: 10px; border-radius: 10px; font-size: 30px; font-weight: bold;">{res['advice']}</div>
            <h1 style="font-size: 65px; color: #FFD700; margin: 15px 0;">₹ {res['price']:,.2f}</h1>
            <p style="font-size: 22px; color: #aaa;">RSI: {res['rsi']:.2f} | Factor: {f_val}</p>
            <hr style="border-color: #333;">
            <div style="text-align: left; display: inline-block;">
                {"".join([f"<p style='font-size: 18px;'>{d}</p>" for d in res['details']])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Fund Balance Quick View
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
        st.info(f"💰 Available Fund: ₹{bal:,.2f}")
    except: pass
