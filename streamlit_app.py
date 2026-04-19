import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI ULTIMATE v6.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN (Transparent Black Sidebar) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.3) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 30px !important; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 25px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def play_notification():
    audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 MARKET ENGINE ---
def get_market_data():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = {}
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="2d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            if name == "Crude Fut": last_p = round(last_p * 83.5 * 1.15, 0)
            else: last_p = round(last_p, 2)
            results[name] = last_p
        return results
    except: return None

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    st.sidebar.title(f"👤 {curr_user.capitalize()}")
    
    # 🚨 MULTI-ALERT SYSTEM
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Set Alerts")
    n_alert = st.sidebar.number_input("Nifty 50 Level", value=0.0)
    bn_alert = st.sidebar.number_input("Bank Nifty Level", value=0.0)
    c_alert = st.sidebar.number_input("Crude Oil Level", value=0.0)
    
    # NAVIGATION
    page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])
    
    markets = get_market_data()
    
    if markets:
        if n_alert > 0 and markets.get("Nifty 50", 0) >= n_alert:
            st.warning(f"🚀 NIFTY ALERT: {markets['Nifty 50']}"); play_notification()
        if bn_alert > 0 and markets.get("Bank Nifty", 0) >= bn_alert:
            st.warning(f"🏦 BANK NIFTY ALERT: {markets['Bank Nifty']}"); play_notification()
        if c_alert > 0 and markets.get("Crude Fut", 0) >= c_alert:
            st.error(f"🛢️ CRUDE ALERT: {markets['Crude Fut']}"); play_notification()

    # --- PAGES ---
    if page == "📊 Advisor":
        st.title("Live Advisor")
        if markets:
            for name, price in markets.items():
                st.markdown(f"""<div class="purple-box"><h3>{name}</h3><h1 style="color:#FFD700;">₹{price:,.0f}</h1></div>""", unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Financial Status")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            st.markdown(f"""<div class="purple-box"><h3>Net Balance</h3><h1 style="color:#FFD700;">₹{total_in - total_out:,.2f}</h1></div>""", unsafe_allow_html=True)
        except: st.error("Data error")

    elif page == "💰 Add Entry":
        st.title("Quick Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")

    elif page == "📊 Report":
        st.title("Report")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            fig = px.pie(df[df['Debit']>0], values='Debit', names='Item', hole=0.3)
            st.plotly_chart(fig)
        except: st.write("No data for report")

    elif page == "🔍 History":
        st.title("History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("Loading...")

    elif page == "🤝 Debt Tracker":
        st.title("Debt Tracker")
        with st.form("debt_f"):
            n = st.text_input("Name")
            a = st.number_input("Amount")
            t = st.selectbox("Category", ["Borrowed (വാങ്ങി)", "Lent (കൊടുത്തു)"])
            if st.form_submit_button("SAVE"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user}] DEBT: {t} - {n}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
