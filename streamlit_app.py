import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re
import urllib.parse
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# 🟢 നിന്റെ വാട്സാപ്പ് നമ്പർ
MY_PHONE = "919061611013" 
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v5.3", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 SMART ENGINES ---
def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except: return 0.0

def process_voice(text):
    if not text: return "Others", 0.0, ""
    raw_text = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw_text)
    amount = float(nums[0]) if nums else 0.0
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "ചായ", "hotel"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട", "സാധനം"]): category = "Shop"
    elif any(x in raw_text for x in ["travel", "യാത്ര", "bus"]): category = "Travel"
    return category, amount, clean_desc

def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            ticker = yf.Ticker(sym)
            df = ticker.history(period="2d", interval="1m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            if name == "Crude Fut": last_p *= 83.5 * 1.15
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            if last_p > pivot: sig, col = "🚀 BUY", "#00FF00"
            else: sig, col = "📉 SELL", "#FF3131"
            results.append({"name": name, "price": last_p, "signal": sig, "color": col})
        return results
    except: return None

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    # ബാലൻസ് ഫൈസലിനും ഷബാനയ്ക്കും കാണാം
    balance = get_total_balance()
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:18px;">Current Balance</span><br>
        <span style="font-size:32px; color:#FFD700;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    # മെനു കൺട്രോൾ: ഷബാനയ്ക്ക് Add Entry മാത്രം
    if curr_user == "shabana":
        menu_options = ["💰 Add Entry"]
    else:
        menu_options = ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]

    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    # --- PAGE LOGIC ---
    if page == "📊 Advisor":
        st.title("Market Advisor 🚀")
        data = get_triple_advisor()
        if data:
            for m in data:
                st.markdown(f'''<div class="purple-box" style="border-left: 10px solid {m['color']};">
                    <h3 style="margin:0;">{m['name']}</h3>
                    <h1 style="color:{m['color']}; margin:10px 0;">{m['signal']}</h1>
                    <h2 style="margin:0;">₹{m['price']:,.2f}</h2>
                </div>''', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v5_3')
        v_cat, v_amt, v_desc = process_voice(v_raw)
        with st.form("entry_form_v5_3", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc if v_desc else "")
            am = st.number_input("Amount", min_value=0.0, value=v_amt)
            cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
            cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE & NOTIFY"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", "entry.1460982454": d, "entry.1221658767": c})
                    msg = f"✅ *Paichi Entry Saved!*\n📝 Item: {it}\n💰 Amount: ₹{am}\n👤 User: {curr_user}"
                    wa_url = f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}"
                    st.success("Saved! ✅")
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">🚀 SEND WHATSAPP</button></a>', unsafe_allow_html=True)

    elif page == "🔍 History":
        st.title("History 🔍")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "📊 Report":
        st.title("Financial Report 📊")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Tracker 🤝")
        st.write("Track debts here.")
