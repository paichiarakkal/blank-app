import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v4.3", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🤖 WHATSAPP NOTIFY (Item & Amount Only) ---
def send_wa_notify(item, amount):
    api_key = "7463030" 
    phone = "971551347989"
    msg = f"📝 Item: {item}\n💰 Amount: {amount}"
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(msg)}&apikey={api_key}"
    try:
        requests.get(url)
    except:
        pass

# --- 3. 🎨 PREMIUM DESIGN (Your Original Color & Style) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 4. DATA ENGINES ---
def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except: return 0.0

def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="1d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            if last_p > pivot: signal, color = "🚀 BUY", "#00FF00"
            else: signal, color = "📉 SELL", "#FF3131"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "color": color})
        return results
    except: return None

# --- 5. MAIN APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    # --- NAVIGATION (Shabana Limitation) ---
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f'<div class="purple-box" style="border-color:{m["color"]};"><h2>{m["name"]}</h2><h1 style="color:{m["color"]};">{m["signal"]}</h1><h3>₹{m["price"]:,.2f}</h3></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        balance = get_total_balance()
        st.markdown(f'<div class="balance-banner"><h1>Available Balance</h1><h1 style="color:#FFD700;">₹{balance:,.2f}</h1></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Add New Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v_v1')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_raw if v_raw else "")
            am = st.number_input("Amount", min_value=0.0)
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Chicken", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    # 1. Save to Sheet
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    # 2. WhatsApp Notify
                    send_wa_notify(it, am)
                    
                    st.success("Saved! ✅")
                    st.rerun()

    elif page == "🔍 History":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Data error")

    elif page == "📊 Report":
        st.title("Expense Analysis")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            report_df = df[df['Debit'] > 0].groupby('Item')['Debit'].sum().reset_index()
            fig = px.pie(report_df, values='Debit', names='Item', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        except: st.write("No report data.")
