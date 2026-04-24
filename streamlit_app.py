import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import re
import urllib.parse
import threading

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI v9.3", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. UI DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 20px; text-align: center; }
    .stat-card { background: rgba(255, 255, 255, 0.07); padding: 15px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 215, 0, 0.3); }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. ENGINES ---

def send_whatsapp_auto(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        t_in = df['Credit'].sum()
        t_out = df['Debit'].sum()
        return t_in, t_out, (t_in - t_out), df
    except: return 0.0, 0.0, 0.0, pd.DataFrame()

def get_market():
    try:
        results = []
        for name, sym in {"Nifty": "^NSEI", "Crude": "CL=F"}.items():
            df = yf.Ticker(sym).history(period="2d", interval="15m")
            cp = df['Close'].iloc[-1]
            change = cp - df['Close'].iloc[-2]
            results.append({"name": name, "price": cp, "color": "#00FF00" if change > 0 else "#FF3131"})
        return results
    except: return []

# --- 4. MAIN APP ---
if not st.session_state.auth:
    st.title("🔐 PAICHI AI")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    t_in, t_out, balance, df = get_data()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:16px; color: #E0B0FF;">Total Balance</span><br>
        <span style="font-size:38px; color:#FFD700;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    menu = ["💰 Add Entry", "📊 Advisor", "📈 Tracker", "📊 Report", "🔍 History"] if st.session_state.user != "shabana" else ["💰 Add Entry"]
    page = st.sidebar.radio("Navigate", menu)

    if page == "💰 Add Entry":
        st.title("Add Transaction 🎙️")
        v_raw = speech_to_text(language='ml', key='v93')
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            it = col1.text_input("Item/Description", value=v_raw if v_raw else "")
            am = col2.text_input("Amount")
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Trading", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    val = float(am)
                    d, c = (val, 0) if ty == "Debit" else (0, val)
                    # കാറ്റഗറി ഐറ്റത്തോടൊപ്പം ചേർക്കുന്നു
                    full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c}
                    
                    threading.Thread(target=requests.post, args=(FORM_API,), kwargs={'data': payload}).start()
                    
                    new_bal = balance - val if ty == "Debit" else balance + val
                    msg = f"✅ *Paichi Entry*\n📂 {cat}\n📝 {it}\n💰 ₹{val}\n⚖️ *Bal: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_whatsapp_auto, args=(msg,)).start()
                    st.success("Saved!"); st.rerun()
                except: st.error("Error!")

    elif page == "📈 Tracker":
        st.title("Daily P&L Tracker 🎯")
        # ഇന്നത്തെ ട്രേഡിംഗ് ലാഭം/നഷ്ടം മാത്രം നോക്കുന്നു
        today = datetime.now().strftime("%Y-%m-%d")
        today_df = df[df['Date'] == today]
        today_trade = today_df[today_df['Item'].str.contains("Trading", na=False)]
        pnl = today_trade['Credit'].sum() - today_trade['Debit'].sum()
        
        st.markdown(f"""<div class="stat-card">
            <h3>Today's Trading P&L</h3>
            <h1 style="color:{'#00FF00' if pnl>=0 else '#FF3131'} !important;">₹{pnl:,.2f}</h1>
        </div>""", unsafe_allow_html=True)

    elif page == "📊 Advisor":
        markets = get_market()
        for m in markets:
            st.markdown(f'<div class="stat-card" style="border-color:{m["color"]}"><h3>{m["name"]}</h3><h2 style="color:{m["color"]} !important;">₹{m["price"]:,.2f}</h2></div>', unsafe_allow_html=True)

    elif page == "📊 Report":
        st.title("Expense Analysis")
        # കാറ്റഗറി തിരിച്ച് റിപ്പോർട്ട് ഉണ്ടാക്കുന്നു
        df['Cat_Only'] = df['Item'].apply(lambda x: str(x).split(':')[0].split(']')[-1].strip() if ':' in str(x) else "Others")
        rdf = df[df['Debit'] > 0].groupby('Cat_Only')['Debit'].sum().reset_index()
        if not rdf.empty:
            fig = px.pie(rdf, values='Debit', names='Cat_Only', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

    elif page == "🔍 History":
        st.dataframe(df.iloc[::-1], use_container_width=True)
