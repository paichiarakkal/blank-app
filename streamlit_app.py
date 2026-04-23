import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import time
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. ലിങ്കുകൾ (നിങ്ങളുടെ ഷീറ്റ് ലിങ്ക് തന്നെ) ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI FINANCE v5.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. ലൈവ് ബാലൻസ് എടുക്കാൻ ---
def get_live_balance():
    try:
        # cache_buster ചേർക്കുന്നത് വഴി ഗൂഗിൾ പഴയ ബാലൻസ് കാണിക്കില്ല
        fresh_url = f"{CSV_URL}&r={random.randint(1, 999999)}"
        df = pd.read_csv(fresh_url)
        df.columns = df.columns.str.strip()
        credit = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        debit = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return credit - debit
    except:
        return 0.0

# --- 3. വാട്സാപ്പ് നോട്ടിഫിക്കേഷൻ ---
def send_wa(item, amount, balance):
    api_key = "7463030" 
    phone = "971551347989"
    msg = f"📝 *Item:* {item}\n💰 *Amount:* {amount}\n💳 *New Balance:* ₹{balance:,.2f}"
    
    # URL നിർമ്മാണം
    encoded_msg = requests.utils.quote(msg)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_msg}&apikey={api_key}"
    try:
        requests.get(url, timeout=10)
    except:
        pass

# --- 4. ഡിസൈൻ ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .stButton>button { background-color: #FFD700 !important; color: #000 !important; font-weight: bold; border-radius: 10px; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; text-align: center; margin-bottom: 20px; }
    h1, h2, h3, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ലോഗിൻ സിസ്റ്റം ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    # പേജ് സെലക്ഷൻ
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "🔍 History"])
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    # --- ഡാഷ്ബോർഡ് ---
    if page == "🏠 Dashboard":
        bal = get_live_balance()
        st.markdown(f'<div class="balance-banner"><h1>Available Balance</h1><h1 style="color:#FFD700;">₹{bal:,.2f}</h1></div>', unsafe_allow_html=True)

    # --- ആഡ് എൻട്രി (ഇതാണ് പ്രധാനം) ---
    elif page == "💰 Add Entry":
        st.title("Add New Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v_v1')
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item Description", value=v_raw if v_raw else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{st.session_state.user.capitalize()}] {it}"
                    
                    # 1. ഗൂഗിൾ ഫോമിലേക്ക് അയക്കുന്നു
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": full_desc, 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    })
                    
                    # 2. ഷീറ്റിൽ അപ്ഡേറ്റ് ആകാൻ 3 സെക്കൻഡ് വെയ്റ്റ് ചെയ്യുന്നു
                    with st.spinner('Updating Balance...'):
                        time.sleep(3.5)
                    
                    # 3. ഏറ്റവും പുതിയ ബാലൻസ് എടുക്കുന്നു
                    updated_bal = get_live_balance()
                    
                    # 4. വാട്സാപ്പിൽ അയക്കുന്നു
                    send_wa(it, am, updated_bal)
                    
                    st.success(f"സേവ് ആയി! പുതിയ ബാലൻസ്: ₹{updated_bal:,.2f} ✅")
                    time.sleep(1)
                    st.rerun()

    # --- ഹിസ്റ്ററി ---
    elif page == "🔍 History":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Data error")
