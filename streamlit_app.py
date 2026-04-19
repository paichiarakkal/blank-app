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
FORM_API = "https://docs.google.com/forms/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# ലോഗിൻ വിവരങ്ങൾ
USERS = {
    "faisal": "faisal123",
    "shabana": "shabana123",
    "admin": "paichi786"
}

st.set_page_config(page_title="PAICHI PRO FINANCE & TRADING", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh") # ഓരോ മിനിറ്റിലും റിഫ്രഷ് ആകും

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 2. 📊 MARKET & NEWS ENGINE ---
def get_market_data():
    try:
        symbols = {
            "Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", 
            "Crude Fut": "CL=F", "HDFC Bank": "HDFCBANK.NS"
        }
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="2d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            high, low = df['High'].iloc[-2], df['Low'].iloc[-2]
            pivot = (high + low + prev_close) / 3
            
            signal = "🚀 BUY CALL" if last_p > pivot else "📉 BUY PUT"
            color = "#00FF00" if last_p > pivot else "#FF0000"
            
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15 # Currency conversion
            results.append({"name": name, "price": last_p, "signal": signal, "color": color})
        return results
    except: return None

def get_latest_news():
    try:
        ticker = yf.Ticker("^NSEI")
        news = ticker.news
        return news[0]['title'] if news else "No major updates."
    except: return "Updating news..."

# --- 3. 🔐 LOGIN ---
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
            else:
                st.error("Access Denied!")
else:
    # സൈഡ് ബാർ മെനു
    user_type = st.session_state.user
    st.sidebar.title(f"👤 {user_type.capitalize()}")
    
    if user_type == "shabana":
        page = "💰 Add Entry" # ഷബാനയ്ക്ക് ഇത് മാത്രമേ കാണൂ
        st.sidebar.info("നിങ്ങൾക്ക് എൻട്രികൾ മാത്രം ചേർക്കാൻ സാധിക്കും.")
    else:
        page = st.sidebar.radio("Menu", ["📊 Trading Advisor", "🏠 Dashboard", "💰 Add Entry", "🤝 Debt Tracker", "🔍 History"])

    if st.sidebar.button("Log Out"):
        st.session_state.auth = False
        st.rerun()

    # --- PAGE: TRADING ADVISOR ---
    if page == "📊 Trading Advisor" and user_type != "shabana":
        st.title("🚀 Pro Trading Terminal")
        news_item = get_latest_news()
        st.warning(f"📰 NEWS: {news_item}")
        
        markets = get_market_data()
        if markets:
            cols = st.columns(len(markets))
            for i, m in enumerate(markets):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:#000; padding:20px; border-radius:10px; border-top:5px solid {m['color']}; text-align:center;">
                        <h4 style="color:white;">{m['name']}</h4>
                        <h2 style="color:{m['color']};">{m['signal']}</h2>
                        <h3 style="color:#FFD700;">₹{m['price']:,.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
        else: st.error("Market data currently unavailable.")

    # --- PAGE: ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("New Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v if v else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit (Expense)", "Credit (Income)"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am > 0:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": f"[{user_type.capitalize()}] {it}", 
                        "entry.1460982454": d, "entry.1221658767": c
                    }
                    requests.post(FORM_API, data=payload)
                    st.success("Saved Successfully! ✅")

    # --- PAGE: DASHBOARD & HISTORY (Faisal Only) ---
    elif user_type != "shabana":
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        
        if page == "🏠 Dashboard":
            st.title("Financial Overview")
            total_in = pd.to_numeric(df['Credit'], errors='coerce').sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').sum()
            balance = total_in - total_out
            st.metric("Total Balance", f"₹{balance:,.2f}")
            
        elif page == "🔍 History":
            st.title("Recent Transactions")
            st.dataframe(df.iloc[::-1], use_container_width=True)

        elif page == "🤝 Debt Tracker":
            st.title("Debt Management")
            st.info("ഇവിടെ കടം കൊടുത്തതും വാങ്ങിയതും രേഖപ്പെടുത്താം.")
            # Debt logic as in your code...
