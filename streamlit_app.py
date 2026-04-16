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

st.set_page_config(page_title="PAICHI MCX LIVE", layout="wide")

# 🚀 5 സെക്കൻഡിൽ ഓട്ടോ റിഫ്രഷ്
st_autorefresh(interval=5000, key="paichi_mcx_v6")

# --- 2. 🤖 MCX DIRECT ENGINE ---
def get_mcx_analysis():
    try:
        # MCX Crude Oil Direct Ticker (ഇത് മാറിക്കൊണ്ടിരിക്കാം)
        # സാധാരണയായി 'MCX-CRUDEOIL-F' അല്ലെങ്കിൽ അന്താരാഷ്ട്ര വിലയാണ് Yahoo കൂടുതൽ കൃത്യമായി നൽകുക
        # ഇവിടെ നമ്മൾ രണ്ടും കൂടി കലർത്തി ഒരു ലോജിക് ഉപയോഗിക്കുന്നു
        ticker = "CL=F" 
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        
        if data.empty: return None
        
        # ഇന്ത്യൻ മാർക്കറ്റിലെ കൃത്യമായ വിലയിലേക്ക് മാറ്റാൻ (Current MCX Conversion)
        # മൾട്ടിപ്ലയർ ഇവിടെ ലോജിക്കിൽ തന്നെ ഫിക്സ് ചെയ്യുന്നു
        curr_price = data['Close'].iloc[-1] * 96.7 
        
        # ഇൻഡിക്കേറ്ററുകൾ
        ema = data['Close'].ewm(span=9).mean().iloc[-1]
        
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))

        score = 0
        if data['Close'].iloc[-1] > ema: score += 1
        else: score -= 1
        if rsi > 55: score += 1
        elif rsi < 45: score -= 1

        advice, color = ("STRONG BUY 🔥", "#00FF00") if score >= 2 else \
                        ("BUY ✅", "#4CAF50") if score == 1 else \
                        ("STRONG SELL 🚫", "#FF0000") if score <= -2 else \
                        ("SELL ❌", "#F44336") if score == -1 else ("NEUTRAL ⏳", "#808080")

        return {"price": curr_price, "rsi": rsi, "advice": advice, "color": color}
    except: return None

# --- 3. UI ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if u.lower() in USERS and USERS[u.lower()]["pw"] == p:
            st.session_state.auth = True; st.rerun()
else:
    # Sidebar
    st.sidebar.header("👤 Faisal")
    manual_adj = st.sidebar.slider("Fine Tune Price", -20.0, 20.0, 0.0)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    res = get_mcx_analysis()
    if res:
        final_val = res['price'] + manual_adj
        st.markdown(f"""
        <div style="background: #161b22; padding: 30px; border-radius: 20px; border: 2px solid {res['color']}; text-align: center;">
            <div style="background: {res['color']}; color: white; padding: 10px; border-radius: 10px; font-size: 35px; font-weight: bold;">{res['advice']}</div>
            <h1 style="font-size: 75px; color: #FFD700; margin: 20px 0;">₹ {final_val:,.2f}</h1>
            <p style="font-size: 22px; color: #888;">Live MCX Estimate | RSI: {res['rsi']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    # Balance View
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
        st.metric("Total Balance", f"₹{bal:,.2f}")
    except: pass
