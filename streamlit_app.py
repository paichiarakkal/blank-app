import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re
import urllib.parse
import threading

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v9.2", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.08); padding: 20px; border-radius: 20px; border: 1px solid #FFD700; text-align: center; margin-bottom: 15px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. ENGINES ---

def send_whatsapp_auto(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=15)
    except: pass

def get_totals():
    try:
        # Cache busting using random number
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out), df
    except: return 0.0, 0.0, 0.0, pd.DataFrame()

def get_market_data():
    """Advisor ഫീച്ചറിനായി ലൈവ് ഡാറ്റ എടുക്കുന്നു"""
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            ticker = yf.Ticker(sym)
            df = ticker.history(period="2d", interval="15m")
            if not df.empty:
                cp = df['Close'].iloc[-1]
                prev_cp = df['Close'].iloc[-2]
                color = "#00FF00" if cp >= prev_cp else "#FF3131"
                signal = "🚀 BUY" if cp >= prev_cp else "📉 SELL"
                if name == "Crude Fut": cp = cp * 84 * 1.15 # Approx Conversion
                results.append({"name": name, "price": cp, "signal": signal, "color": color})
        return results
    except: return []

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    t_in, t_out, balance, main_df = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:18px; color: #E0B0FF;">Available Balance</span><br>
        <span style="font-size:42px; color:#FFD700;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    if curr_user == "shabana": menu = ["💰 Add Entry"]
    else: menu = ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History"]

    page = st.sidebar.radio("Navigate", menu)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    if page == "📊 Advisor":
        st.title("Market Advisor")
        markets = get_market_data()
        if markets:
            for m in markets:
                st.markdown(f"""<div class="purple-box" style="border-color: {m['color']};">
                    <h3>{m['name']}</h3>
                    <h1 style="color:{m['color']} !important;">{m['signal']}</h1>
                    <h2>₹{m['price']:,.2f}</h2>
                </div>""", unsafe_allow_html=True)
        else: st.warning("Market data loading... Please refresh.")

    elif page == "💰 Add Entry":
        st.title("Add Transaction")
        v_raw = speech_to_text(language='ml', key='v92')
        with st.form("f1", clear_on_submit=True):
            it = st.text_input("Item", value=v_raw if v_raw else "")
            am = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                try:
                    val = float(am)
                    d, c = (val, 0) if ty == "Debit" else (0, val)
                    new_bal = balance - val if ty == "Debit" else balance + val
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    
                    threading.Thread(target=requests.post, args=(FORM_API,), kwargs={'data': payload}).start()
                    
                    # വാട്സാപ്പിൽ ബാലൻസ് കൂടി അയക്കുന്നു
                    msg = f"✅ *Paichi Saved*\n📝 {it}\n💰 ₹{val}\n⚖️ *Balance: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_whatsapp_auto, args=(msg,)).start()
                    st.success(f"Saved! Balance: ₹{new_bal}")
                except: st.error("നമ്പർ നൽകുക")

    elif page == "📊 Report":
        st.title("Expense Chart")
        if not main_df.empty:
            rdf = main_df[pd.to_numeric(main_df['Debit'], errors='coerce') > 0].copy()
            if not rdf.empty:
                fig = px.pie(rdf, values='Debit', names='Item', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("No debit entries for report.")

    elif page == "🔍 History":
        st.dataframe(main_df.iloc[::-1], use_container_width=True)
