import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="PAICHI AI V5", layout="wide")
st_autorefresh(interval=5000, key="paichi_v5")

# --- 🤖 SIMPLE ENGINE ---
def get_signal(multiplier):
    try:
        ticker = "CL=F"
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if data.empty: return None
        
        last_price = data['Close'].iloc[-1]
        ema = data['Close'].ewm(span=9).mean().iloc[-1] # Simple EMA logic
        
        live_val = last_price * multiplier
        
        if last_price > ema:
            advice, color = "BUY ✅", "#00FF00"
        else:
            advice, color = "SELL ❌", "#FF0000"
            
        return {"price": live_val, "advice": advice, "color": color}
    except: return None

# --- UI ---
st.sidebar.header("Faisal")
f_val = st.sidebar.number_input("Factor", value=96.8, step=0.1)

res = get_signal(f_val)
if res:
    st.markdown(f"""
    <div style="background: #0e1117; padding: 30px; border-radius: 15px; border: 3px solid {res['color']}; text-align: center;">
        <h1 style="color: {res['color']}; font-size: 50px;">{res['advice']}</h1>
        <h1 style="font-size: 80px; color: #FFD700;">₹ {res['price']:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)
