import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re
import urllib.parse
import threading
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# നിന്റെ പുതിയ WhatsApp API വിവരങ്ങൾ
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI v7.0", layout="wide")
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

# --- 3. 📊 FUNCTIONS ---

def send_whatsapp_auto(message):
    """വാട്സാപ്പിലേക്ക് തനിയെ മെസ്സേജ് അയക്കുന്നു"""
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def send_to_google_async(data):
    """ഗൂഗിൾ ഷീറ്റിലേക്ക് ഡാറ്റ അയക്കുന്നു"""
    try: requests.post(FORM_API, data=data, timeout=10)
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
    st.title("🔐 PAICHI AI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    t_in, t_out, balance = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #E0B0FF;">Available Balance</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v7')
        _, v_amt, v_desc = process_voice(v_raw)
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am_str = st.text_input("Amount", value=str(v_amt))
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    if it and am > 0:
                        d, c = (am, 0) if ty == "Debit" else (0, am)
                        payload = {
                            "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                            "entry.2013476337": f"[{curr_user.capitalize()}] {it}",
                            "entry.1460982454": d, "entry.1221658767": c
                        }
                        
                        # 1. ബാക്ക്ഗ്രൗണ്ടിൽ ഗൂഗിൾ ഷീറ്റിലേക്ക് അയക്കുന്നു
                        threading.Thread(target=send_to_google_async, args=(payload,)).start()
                        
                        # 2. ബാക്ക്ഗ്രൗണ്ടിൽ വാട്സാപ്പിലേക്ക് ആറ്റോമിക് ആയി അയക്കുന്നു
                        msg = f"✅ *Paichi Entry*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {curr_user}"
                        threading.Thread(target=send_whatsapp_auto, args=(msg,)).start()
                        
                        st.success("Saved! WhatsApp notification sent. ✅")
                    else: st.error("വിവരങ്ങൾ നൽകുക!")
                except: st.error("നമ്പർ മാത്രം നൽകുക!")

    elif page == "🏠 Dashboard":
        st.markdown(f"### Total Credit: ₹{t_in} \n ### Total Debit: ₹{t_out}")

    elif page == "🔍 History":
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1], use_container_width=True)
