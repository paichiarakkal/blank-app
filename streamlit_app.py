import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & AUTH ---
USERS = {"faisal": {"pw": "faisal123", "role": "admin"}}
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI AI PRO V5", layout="wide")

# 🚀 റേറ്റ് ലിമിറ്റ് ഒഴിവാക്കാൻ 20 സെക്കൻഡിൽ റിഫ്രഷ് ചെയ്യുന്നു
st_autorefresh(interval=20000, key="paichi_v5_safe")

# --- 2. 🤖 ENGINE (CRUDE + VIX) ---
def get_market_data(multiplier):
    try:
        # Crude Oil Data
        crude = yf.download("CL=F", period="1d", interval="1m", progress=False)
        # India VIX Data
        vix = yf.download("^INDIAVIX", period="1d", interval="1m", progress=False)
        
        if crude.empty: return None
        
        last_price = crude['Close'].iloc[-1]
        ema = crude['Close'].ewm(span=9).mean().iloc[-1]
        vix_val = vix['Close'].iloc[-1] if not vix.empty else 0
        
        # RSI Calculation
        delta = crude['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        live_mcx = last_price * multiplier
        
        if last_price > ema:
            advice, color = "BUY ✅", "#00FF00"
        else:
            advice, color = "SELL ❌", "#FF0000"
            
        return {
            "price": live_mcx, 
            "advice": advice, 
            "color": color, 
            "vix": vix_val, 
            "rsi": rsi
        }
    except Exception as e:
        return None

# --- 3. UI ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u.lower() in USERS and USERS[u.lower()]["pw"] == p:
            st.session_state.auth = True
            st.rerun()
else:
    with st.sidebar:
        st.header("👤 Faisal")
        f_val = st.number_input("Price Factor", value=96.8, step=0.1)
        page = st.radio("Menu", ["📊 Advisor", "💰 Expense", "🔍 History"])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    if page == "📊 Advisor":
        res = get_market_data(f_val)
        if res:
            st.markdown(f"""
            <div style="background: #0e1117; padding: 25px; border-radius: 15px; border: 3px solid {res['color']}; text-align: center;">
                <h1 style="color: {res['color']}; font-size: 55px; margin:0;">{res['advice']}</h1>
                <h1 style="font-size: 85px; color: #FFD700; margin: 10px 0;">₹ {res['price']:,.2f}</h1>
                <div style="display: flex; justify-content: space-around; color: #aaa; font-size: 20px;">
                    <span>VIX: {res['vix']:.2f}</span>
                    <span>RSI: {res['rsi']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # VIX Warning
            if res['vix'] > 18:
                st.warning("⚠️ Volatility കൂടുതലാണ് (VIX > 18). ജാഗ്രത പാലിക്കുക!")
            
            # RSI Advice
            if res['rsi'] < 30:
                st.info("💡 RSI Oversold മേഖലയിലാണ്. സെൽ ഒഴിവാക്കുന്നത് നന്നായിരിക്കും.")
        else:
            st.error("Yahoo Finance Connection Error! അല്പനേരം കാത്തിരിക്കൂ.")

    elif page == "💰 Expense":
        st.title("Expense Tracker")
        v = speech_to_text(language='ml', key='ml_voice')
        with st.form("exp_form"):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SUBMIT"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": it, "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")

    elif page == "🔍 History":
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: pass
