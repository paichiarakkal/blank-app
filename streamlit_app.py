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

st.set_page_config(page_title="PAICHI PURPLE GOLD v10.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. PREMIUM UI ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'currency' not in st.session_state: st.session_state.currency = "INR"

# --- 3. HELPER ENGINES ---

def get_exchange_rate():
    try:
        data = yf.Ticker("AEDINR=X").history(period="1d")
        return data['Close'].iloc[-1]
    except: return 22.80

def send_whatsapp_auto(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,99999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out), df
    except: return 0.0, 0.0, 0.0, pd.DataFrame()

def parse_voice(text):
    if not text: return "", ""
    nums = re.findall(r'\d+', text)
    amt = nums[0] if nums else ""
    desc = re.sub(r'\d+', '', text).strip()
    return amt, desc

def get_market():
    try:
        syms = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        res = []
        for name, s in syms.items():
            d = yf.Ticker(s).history(period="2d", interval="15m")
            cp = d['Close'].iloc[-1]
            ch = cp - d['Close'].iloc[-2]
            res.append({"n": name, "p": cp, "c": "#00FF00" if ch > 0 else "#FF3131", "s": "🚀 BUY" if ch > 0 else "📉 SELL"})
        return res
    except: return []

# --- 4. MAIN LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    t_in, t_out, bal_inr, main_df = get_data()
    ex_rate = get_exchange_rate()
    
    # Sidebar Currency Toggle
    if st.sidebar.button(f"Switch to {'AED' if st.session_state.currency == 'INR' else 'INR'}"):
        st.session_state.currency = "AED" if st.session_state.currency == "INR" else "INR"; st.rerun()

    disp_bal = bal_inr / ex_rate if st.session_state.currency == "AED" else bal_inr
    sym = "AED" if st.session_state.currency == "AED" else "₹"

    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:18px; color: #E0B0FF;">Total Balance ({st.session_state.currency})</span><br>
        <span style="font-size:42px; color:#FFD700;">{sym} {disp_bal:,.2f}</span>
        <p style="font-size:12px; color:gray;">1 AED = ₹{ex_rate:.2f}</p>
    </div>''', unsafe_allow_html=True)

    menu = ["💰 Add Entry"] if st.session_state.user == "shabana" else ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Navigate", menu)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    if page == "💰 Add Entry":
        st.title("Smart Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v10')
        v_amt, v_desc = parse_voice(v_raw)
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item/Description", value=v_desc)
            am = st.text_input("Amount (INR)", value=v_amt)
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Trading", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    val = float(am.strip())
                    d, c = (val, 0) if ty == "Debit" else (0, val)
                    full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c}
                    threading.Thread(target=requests.post, args=(FORM_API,), kwargs={'data': payload}).start()
                    
                    new_bal = bal_inr - val if ty == "Debit" else bal_inr + val
                    msg = f"✅ *Paichi Entry*\n📂 {cat}\n📝 {it}\n💰 ₹{val}\n⚖️ *Balance: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_whatsapp_auto, args=(msg,)).start()
                    st.success(f"Saved! Bal: ₹{new_bal:,.2f}"); st.rerun()
                except: st.error("Amount ബോക്സിൽ നമ്പർ നൽകുക!")

    elif page == "📊 Advisor":
        st.title("Trading Advisor")
        markets = get_market()
        for m in markets:
            st.markdown(f'<div class="purple-box" style="border-color:{m["c"]}"><h3>{m["n"]}</h3><h1 style="color:{m["c"]} !important;">{m["s"]}</h1><h2>₹{m["p"]:,.2f}</h2></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.markdown(f"""<div class="purple-box">
            <h2 style="color: #00FF00;">Total Credit: ₹{t_in:,.2f}</h2>
            <h2 style="color: #FF3131;">Total Debit: ₹{t_out:,.2f}</h2>
        </div>""", unsafe_allow_html=True)

    elif page == "📊 Report":
        st.title("Expense Analysis")
        main_df['Category'] = main_df['Item'].apply(lambda x: str(x).split(':')[0].split(']')[-1].strip() if ':' in str(x) else "Others")
        rdf = main_df[pd.to_numeric(main_df['Debit'], errors='coerce') > 0].groupby('Category')['Debit'].sum().reset_index()
        if not rdf.empty:
            fig = px.pie(rdf, values='Debit', names='Category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig, use_container_width=True)

    elif page == "🔍 History":
        st.dataframe(main_df.iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("d_f"):
            n, a = st.text_input("Name"), st.number_input("Amount")
            t = st.selectbox("Type", ["Borrowed", "Lent"])
            if st.form_submit_button("SAVE DEBT"):
                d, c = (0, a) if t == "Borrowed" else (a, 0)
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.capitalize()}] DEBT: {t}-{n}", "entry.1460982454": d, "entry.1221658767": c}
                threading.Thread(target=requests.post, args=(FORM_API,), kwargs={'data': payload}).start()
                st.success("Debt Saved!")
