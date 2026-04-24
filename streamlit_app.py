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

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v9.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'currency' not in st.session_state: st.session_state.currency = "INR"

# --- 3. 📊 SMART ENGINES ---

def get_exchange_rate():
    """Live AED to INR റേറ്റ് എടുക്കുന്നു"""
    try:
        data = yf.Ticker("AEDINR=X").history(period="1d")
        return data['Close'].iloc[-1]
    except: return 22.70 # എറർ വന്നാൽ ഒരു ആവറേജ് റേറ്റ്

def send_whatsapp_auto(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out)
    except: return 0.0, 0.0, 0.0

def process_voice(text):
    if not text: return "Others", "", ""
    raw = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw)
    amt = nums[0] if nums else ""
    desc = re.sub(r'\d+', '', raw).strip()
    return "Others", amt, desc

# --- 4. APP MAIN ---
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
    t_in, t_out, balance_inr = get_totals()
    rate = get_exchange_rate()
    
    # കറൻസി സ്വിച്ച് ചെയ്യാനുള്ള ബട്ടൺ
    st.sidebar.markdown("### 🇦E Currency Settings")
    if st.sidebar.button(f"Switch to {'AED' if st.session_state.currency == 'INR' else 'INR'}"):
        st.session_state.currency = "AED" if st.session_state.currency == "INR" else "INR"
        st.rerun()

    # ബാലൻസ് കാണിക്കുന്നു
    if st.session_state.currency == "AED":
        disp_bal = balance_inr / rate
        sym = "AED"
    else:
        disp_bal = balance_inr
        sym = "₹"

    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #E0B0FF;">Total Balance ({st.session_state.currency})</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">{sym} {disp_bal:,.2f}</span>
        <p style="font-size:12px; color:gray;">Live Rate: 1 AED = ₹{rate:.2f}</p>
    </div>''', unsafe_allow_html=True)

    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📊 Advisor", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v9')
        _, v_amt, v_desc = process_voice(v_raw)
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am_str = st.text_input("Amount (in INR)", value=str(v_amt))
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip())
                    if it and am > 0:
                        d, c = (am, 0) if ty == "Debit" else (0, am)
                        payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                        threading.Thread(target=requests.post, args=(FORM_API,), kwargs={'data': payload}).start()
                        
                        msg = f"✅ *Entry Saved*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {curr_user}"
                        threading.Thread(target=send_whatsapp_auto, args=(msg,)).start()
                        st.success("Saved! ✅")
                    else: st.error("വിവരങ്ങൾ നൽകുക!")
                except: st.error("നമ്പർ മാത്രം നൽകുക!")

    elif page == "🏠 Dashboard":
        st.markdown(f"### Credit: ₹{t_in:,.2f} \n ### Debit: ₹{t_out:,.2f}")
        st.info(f"ഇന്നത്തെ എക്സ്ചേഞ്ച് റേറ്റ്: 1 AED = {rate:.2f} INR")

    elif page == "🔍 History":
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "📊 Advisor":
        # പഴയ അഡ്വൈസർ കോഡ് ഇവിടെയും വർക്ക് ചെയ്യും
        st.write("Market Advisor Loading...")
