import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import pandas_ta as ta
import numpy as np
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & AUTH ---
USERS = {"faisal": {"pw": "faisal123", "role": "admin"}}
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI AI PRO V4.0", layout="wide")

# 🚀 5 സെക്കൻഡിൽ ഓട്ടോ റിഫ്രഷ് (ലൈവ് ഫീൽ കിട്ടാൻ)
st_autorefresh(interval=5000, key="paichi_final_sync")

# --- 2. 🤖 SUPERTREND ENGINE ---
def get_supertrend_analysis(multiplier_val):
    try:
        # അന്താരാഷ്ട്ര ക്രൂഡ് ഓയിൽ 1-മിനിറ്റ് ഡാറ്റ
        ticker = "CL=F"
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        if data.empty: return None

        # SuperTrend (10, 3) - Upstox-ലെ അതേ സെറ്റിംഗ്സ്
        sti = ta.supertrend(data['High'], data['Low'], data['Close'], length=10, multiplier=3)
        
        last_close = data['Close'].iloc[-1]
        st_direction = sti['SUPERTd_10_3.0'].iloc[-1] # 1 = Buy, -1 = Sell
        st_line = sti['SUPERT_10_3.0'].iloc[-1]

        # MCX രൂപയിലേക്ക് മാറ്റുന്നു
        live_price = last_close * multiplier_val
        st_mcx_level = st_line * multiplier_val

        if st_direction == 1:
            advice, color = "SUPER BUY 🟢", "#00FF00"
        else:
            advice, color = "SUPER SELL 🔴", "#FF0000"

        return {
            "price": live_price, 
            "advice": advice, 
            "color": color, 
            "st_level": st_mcx_level
        }
    except Exception as e:
        return None

# --- 3. UI INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI AI LOGIN")
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u.lower() in USERS and USERS[u.lower()]["pw"] == p:
            st.session_state.auth = True
            st.rerun()
else:
    with st.sidebar:
        st.header(f"👤 Faisal")
        # വില അഡ്ജസ്റ്റ് ചെയ്യാൻ ഇത് ഉപയോഗിക്കാം
        f_val = st.number_input("Price Factor (Adj)", value=96.8, step=0.1)
        
        page = st.radio("Menu", ["📊 Live Advisor", "💰 Add Expense", "🔍 History"])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    if page == "📊 Live Advisor":
        st.subheader("MCX Crude Oil - SuperTrend AI")
        res = get_supertrend_analysis(f_val)
        
        if res:
            st.markdown(f"""
            <div style="background: #0e1117; padding: 30px; border-radius: 15px; border: 3px solid {res['color']}; text-align: center;">
                <h1 style="color: {res['color']}; font-size: 50px; margin-bottom: 0;">{res['advice']}</h1>
                <p style="color: #888;">Live Trend based on 1m candles</p>
                <hr style="border-color: #333;">
                <h1 style="font-size: 85px; color: #FFD700; margin: 10px 0;">₹ {res['price']:,.2f}</h1>
                <p style="font-size: 20px; color: #fff;">SuperTrend Line: ₹ {res['st_level']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if "BUY" in res['advice']:
                st.success(f"ട്രെൻഡ് ബൈ ആണ്. വില ₹{res['st_level']:,.2f}-ന് മുകളിൽ നിൽക്കുന്നത് വരെ തുടരാം.")
            else:
                st.error(f"ട്രെൻഡ് സെൽ ആണ്. വില ₹{res['st_level']:,.2f}-ന് താഴെ നിൽക്കുന്നത് വരെ തുടരാം.")

        # ഫണ്ട് ബാലൻസ് കാണിക്കാൻ
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
            st.metric("Total Balance", f"₹{bal:,.2f}")
        except: pass

    elif page == "💰 Add Expense":
        st.title("Quick Expense Tracker")
        v = speech_to_text(language='ml', key='ml_voice_final')
        with st.form("expense_form"):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SUBMIT"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": it, 
                    "entry.1460982454": d, 
                    "entry.1221658767": c
                })
                st.success("Entry Saved Successfully!")

    elif page == "🔍 History":
        st.title("Transaction History")
        try:
            dfh = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(dfh.iloc[::-1], use_container_width=True)
        except: st.error("Database connection failed.")

st.markdown("<p style='text-align:center; color: #555; margin-top: 50px;'>PAICHI AI HUB v4.0 | SuperTrend (10,3)</p>", unsafe_allow_html=True)
