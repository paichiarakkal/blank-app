import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import time
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v4.7", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🤖 UPDATED WHATSAPP ENGINE ---
def send_wa_notify(item, amount, balance):
    api_key = "7463030" 
    phone = "971551347989"
    
    # മെസ്സേജ് ഫോർമാറ്റ് ഒന്നുകൂടി ക്ലീൻ ആക്കി
    msg = f"📝 *Item:* {item}\n💰 *Amount:* {amount}\n💳 *Total Balance:* ₹{balance:,.2f}"
    
    # URL നിർമ്മാണം കൂടുതൽ സുരക്ഷിതമാക്കി
    params = {
        'phone': phone,
        'text': msg,
        'apikey': api_key
    }
    
    url = "https://api.callmebot.com/whatsapp.php"
    try:
        # നേരിട്ട് ലിങ്ക് ഉണ്ടാക്കുന്നതിന് പകരം params ഉപയോഗിക്കുന്നു
        requests.get(url, params=params, timeout=10)
    except Exception as e:
        st.error(f"WhatsApp Error: {e}")

# --- 3. DATA ENGINE ---
def get_total_balance():
    try:
        # Cache ഒഴിവാക്കാൻ റാൻഡം നമ്പർ ലിങ്കിന്റെ കൂടെ ചേർക്കുന്നു
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except:
        return 0.0

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700 !important; color: #000 !important; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else:
            st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "💰 Add Entry":
        st.title("Add New Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v_v1')
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_raw if v_raw else "")
            am = st.number_input("Amount", min_value=0.0)
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Chicken", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    
                    # 1. ഗൂഗിൾ ഷീറ്റിലേക്ക് സേവ് ചെയ്യുന്നു
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": full_desc, 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    })
                    
                    # 2. ഷീറ്റിൽ ഡാറ്റ അപ്ഡേറ്റ് ആകാൻ 3 സെക്കൻഡ് കാക്കുന്നു
                    with st.spinner('Updating Balance...'):
                        time.sleep(3) 
                    
                    # 3. പുതിയ ബാലൻസ് എടുക്കുന്നു
                    new_bal = get_total_balance()
                    
                    # 4. വാട്സാപ്പിൽ അയക്കുന്നു
                    send_wa_notify(it, am, new_bal)
                    
                    st.success(f"Saved! Balance Updated: ₹{new_bal:,.2f} ✅")
                    time.sleep(1)
                    st.rerun()

    elif page == "🏠 Dashboard":
        st.title("Welcome Faisal")
        balance = get_total_balance()
        st.markdown(f'<div class="balance-banner"><h1>Available Balance</h1><h1 style="color:#FFD700;">₹{balance:,.2f}</h1></div>', unsafe_allow_html=True)

    elif page == "🔍 History":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.error("Data error")
