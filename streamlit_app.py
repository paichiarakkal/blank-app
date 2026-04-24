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

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# വാട്സാപ്പ് സെറ്റിംഗ്സ്
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v4.4", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521);
        color: #fff;
    }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button {
        background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold;
    }
    .balance-banner {
        background: rgba(255, 215, 0, 0.1);
        padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700;
        margin-bottom: 25px; text-align: center;
    }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center; margin-bottom: 20px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 SMART ENGINES ---

def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except: return 0.0

def process_voice(text):
    if not text: return "Others", None, ""
    raw_text = text.lower()
    nums = re.findall(r'\d+', raw_text)
    amount = float(nums[0]) if nums else None
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "ഹോട്ടൽ", "ചായ", "tea"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട", "സാധനം"]): category = "Shop"
    elif any(x in raw_text for x in ["rent", "വാടക"]): category = "Rent"
    
    return category, amount, clean_desc

# (ബാക്കി ഫംഗ്ഷനുകൾ create_pdf, get_triple_advisor എന്നിവ നിന്റെ കോഡിലുള്ളത് പോലെ തന്നെ...)
def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C'); pdf.ln(10)
        cols = df.columns.tolist()
        pdf.set_font("Arial", 'B', 10)
        for col in cols: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln(); pdf.set_font("Arial", size=9)
        for i, row in df.iterrows():
            for col in cols:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(38, 10, txt=val, border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            if last_p > pivot and rsi > 55: signal, color = "🚀 BUY", "#00FF00"
            elif last_p < pivot and rsi < 45: signal, color = "📉 SELL", "#FF3131"
            else: signal, color = "⚖️ WAIT", "#FFFF00"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": rsi, "color": color})
        return results
    except: return None

# --- 4. APP LOGIC ---
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
    balance = get_total_balance()
    st.markdown(f"""<div class="balance-banner">
        <span style="font-size:18px; color:#E0B0FF;">Available Balance</span><br>
        <span style="font-size:32px; color:#FFD700;">₹{balance:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    if curr_user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    if page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v44')
        v_cat, v_amt, v_desc = process_voice(v_raw)

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc if v_desc else "")
            am = st.number_input("Amount", min_value=0.0, value=v_amt if v_amt else 0.0)
            cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
            cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE DATA"):
                if am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    new_bal = balance + (c - d)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    
                    # ഗൂഗിൾ ഷീറ്റിൽ സേവ് ചെയ്യുന്നു
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    # വാട്സാപ്പ് മെസ്സേജ് അയക്കുന്നു
                    wa_msg = f"✅ *Paichi Entry*\n📂 {cat}\n📝 {it}\n💰 ₹{am}\n⚖️ *Bal: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_wa, args=(wa_msg,)).start()
                    
                    st.success(f"Saved! Balance: ₹{new_bal:,.2f}"); st.rerun()

    # (ബാക്കി പേജുകൾ Dashboard, Advisor, History എല്ലാം നിന്റെ ഒറിജിനൽ കോഡിലുള്ളത് പോലെ തന്നെ വരും)
    elif page == "📊 Advisor":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f"""<div class="purple-box" style="border-color: {m['color']} !important;">
                    <h2 style="color:#E0B0FF !important;">{m["name"]}</h2>
                    <h1 style="color:{m["color"]} !important; font-size:55px;">{m["signal"]}</h1>
                    <h1 style="color:#FFD700 !important; font-size:50px;">₹{m["price"]:,.0f}</h1>
                    <p>RSI: {m["rsi"]:.1f}</p>
                </div>""", unsafe_allow_html=True)

    elif page == "🔍 History":
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("No history.")
