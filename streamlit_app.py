import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import io

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {
    "faisal": "faisal123",
    "shabana": "shabana123",
    "admin": "paichi786"
}

st.set_page_config(page_title="PAICHI PRO FINANCE v3.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 2. 📊 ADVANCED MARKET ADVISOR (Triple Indicator) ---
def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            
            # 1. PIVOT POINT
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            
            # 2. RSI (14)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            # 3. SUPERTREND (ATR 10, 3)
            atr = (df['High'] - df['Low']).rolling(window=10).mean().iloc[-1]
            lower_band = ((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr)
            st_buy = last_p > lower_band
            
            # LOGIC
            if last_p > pivot and rsi > 55 and st_buy:
                signal, color = "🚀 TRIPLE BUY", "#00FF00"
            elif last_p < pivot and rsi < 45 and not st_buy:
                signal, color = "📉 TRIPLE SELL", "#FF0000"
            else:
                signal, color = "⚖️ NEUTRAL", "#FFFF00"
            
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": rsi, "color": color})
        return results
    except: return None

# --- 3. 🔐 LOGIN SYSTEM ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    # --- 4. NAVIGATION & PERMISSIONS ---
    curr_user = st.session_state.user
    st.sidebar.title(f"👤 {curr_user.capitalize()}")
    
    if curr_user == "shabana":
        page = "💰 Add Entry"
        st.sidebar.info("എൻട്രികൾ ആഡ് ചെയ്യാൻ മാത്രം അനുവാദം.")
    else:
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🤝 Debt Tracker", "🔍 History"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- 5. PAGES ---
    
    # --- ADVISOR ---
    if page == "📊 Advisor" and curr_user != "shabana":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            cols = st.columns(len(markets))
            for i, m in enumerate(markets):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:#111; padding:20px; border-radius:10px; border:2px solid {m['color']}; text-align:center;">
                        <h3 style="color:white;">{m['name']}</h3>
                        <h2 style="color:{m['color']};">{m['signal']}</h2>
                        <h1 style="color:#FFD700; font-size:35px;">₹{m['price']:,.0f}</h1>
                        <p style="color:#aaa;">RSI: {m['rsi']:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else: st.warning("Market Data loading...")

    # --- DASHBOARD ---
    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Financial Overview")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            total_in = pd.to_numeric(df['Credit'], errors='coerce').sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').sum()
            balance = total_in - total_out
            st.metric("കയ്യിലുള്ള ബാക്കി തുക", f"₹{balance:,.2f}")
            
            # AI Tip
            if balance < 5000: st.error("⚠️ സൂക്ഷിക്കുക, കയ്യിലുള്ള തുക കുറവാണ്!")
            else: st.success("✅ സമ്പാദ്യം മെച്ചപ്പെടുന്നുണ്ട്. ഇതേപോലെ തുടരുക!")
        except: st.error("ഷീറ്റ് ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

    # --- ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("Add New Transaction")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit (Expense)", "Credit (Income)"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": f"[{curr_user.capitalize()}] {it}", 
                        "entry.1460982454": d, "entry.1221658767": c
                    }
                    requests.post(FORM_API, data=payload)
                    st.success("വിജയകരമായി സേവ് ചെയ്തു! ✅")

    # --- DEBT TRACKER ---
    elif page == "🤝 Debt Tracker" and curr_user != "shabana":
        st.title("Debt Management")
        with st.form("debt_f", clear_on_submit=True):
            n = st.text_input("Name")
            a = st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["Borrowed (വാങ്ങി)", "Lent (കൊടുത്തു)"])
            if st.form_submit_button("RECORD DEBT"):
                desc = f"DEBT: {t} - {n}"
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                requests.post(FORM_API, data={
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": f"[{curr_user.capitalize()}] {desc}", 
                    "entry.1460982454": d, "entry.1221658767": c
                })
                st.success("കടം വിവരങ്ങൾ രേഖപ്പെടുത്തി!")

    # --- HISTORY ---
    elif page == "🔍 History" and curr_user != "shabana":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("No data found.")
