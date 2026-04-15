import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import os
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# 1. ലോഗിൻ & ലിങ്കുകൾ
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"},
    "admin": {"pw": "paichi786", "role": "admin"}
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
TRADE_FILE = 'trade_journal.csv'

st.set_page_config(page_title="PAICHI All-in-One Finance", layout="wide")

# --- 🎨 ഡിസൈൻ (ഗോൾഡൻ തീം) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background-color: #1a1a1a !important; color: white !important; }
    .balance-box { background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 15px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .info-box { background-color: #f8f9fa; padding: 10px; border-radius: 8px; color: #333; font-weight: bold; text-align: center; border: 1px solid #ddd; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# 30 സെക്കൻഡിൽ ഓട്ടോ റിഫ്രഷ്
st_autorefresh(interval=30000, key="paichi_hub_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ഫംഗ്ഷനുകൾ ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- 🔐 ലോഗിൻ ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE HUB LOGIN")
    u_raw = st.text_input("Username").lower().strip()
    p_raw = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u_raw in USERS and USERS[u_raw]["pw"] == p_raw:
            st.session_state.auth, st.session_state.user, st.session_state.role = True, u_raw.capitalize(), USERS[u_raw]["role"]
            st.rerun()
        else: st.error("Access Denied!")
else:
    # --- 👤 സൈഡ് ബാർ ടൂളുകൾ ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        
        # ലൈവ് റേറ്റുകൾ
        st.write("💰 **Rates**")
        ex_rate = get_live_price("AEDINR=X")
        crude = get_live_price("CL=F")
        st.markdown(f'<div class="info-box">AED/INR: ₹{ex_rate:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">Crude Oil: ${crude:.2f}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # മെനു സെലക്ഷൻ
        menu = ["🏠 Dashboard", "💰 Add Expense"]
        if st.session_state.role == "admin":
            menu = ["🏠 Dashboard", "💰 Add Expense", "📈 Trading Journal", "📊 Reports"]
        
        page = st.radio("Menu", menu)
        
        st.divider()
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()
        st.markdown("[💬 Contact on WhatsApp](https://wa.me/918714752210)")

    # --- 🏠 DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        col1, col2 = st.columns(2)
        
        try:
            df_exp = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
            bal = pd.to_numeric(df_exp['Credit'], errors='coerce').sum() - pd.to_numeric(df_exp['Debit'], errors='coerce').sum()
            col1.markdown(f'<div class="balance-box">Family Balance<br>₹{bal:,.2f}</div>', unsafe_allow_html=True)
        except: col1.error("Sheet Load Error")

        if os.path.exists(TRADE_FILE):
            df_trade = pd.read_csv(TRADE_FILE)
            trade_bal = df_trade['P&L'].sum()
            col2.markdown(f'<div class="balance-box">Trading P&L<br>₹{trade_bal:,.2f}</div>', unsafe_allow_html=True)

        st.subheader("Recent Expenses")
        st.dataframe(df_exp.iloc[::-1].head(10), use_container_width=True)

    # --- 💰 ADD EXPENSE ---
    elif page == "💰 Add Expense":
        st.title("Add New Expense")
        v = speech_to_text(language='ml', key='voice_exp')
        with st.form("exp_form", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE EXPENSE"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("സേവ് ചെയ്തു! ✅")

    # --- 📈 TRADING JOURNAL ---
    elif page == "📈 Trading Journal":
        st.title("Trading Entry")
        col1, col2 = st.columns(2)
        idx = col1.selectbox("Index", ["NIFTY", "BANKNIFTY", "CRUDE OIL"])
        strike = col2.text_input("Strike", placeholder="Ex: 22400 CE")
        
        with st.form("trade_form", clear_on_submit=True):
            e_p = st.number_input("Entry Price")
            ex_p = st.number_input("Exit Price")
            q = st.number_input("Qty", step=1)
            t_mood = st.selectbox("Mood", ["Calm", "Fear", "Greedy"])
            if st.form_submit_button("SAVE TRADE"):
                pnl = (ex_p - e_p) * q
                df_new = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), f"{idx} {strike}", e_p, ex_p, q, pnl, t_mood]], 
                                      columns=['Date', 'Item', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
                if not os.path.isfile(TRADE_FILE): df_new.to_csv(TRADE_FILE, index=False)
                else: df_new.to_csv(TRADE_FILE, mode='a', header=False, index=False)
                st.success(f"Trade Saved! P&L: ₹{pnl}")

st.markdown(f'<p style="text-align: center; margin-top: 30px;">Created by Faisal Arakkal</p>', unsafe_allow_html=True)
