import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re
import urllib.parse
import threading # 🟢 സ്പീഡ് കൂട്ടാൻ ഇത് സഹായിക്കും
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

MY_PHONE = "918714752210" 
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v6.1", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'last_wa_url' not in st.session_state: st.session_state.last_wa_url = None

# --- 3. 📊 FUNCTIONS ---
def send_data_async(data):
    # 🟢 ഡാറ്റ ബാക്ക്ഗ്രൗണ്ടിൽ അയക്കുന്നു, അതിനാൽ ആപ്പ് ഹാങ്ങ് ആകില്ല
    try:
        requests.post(FORM_API, data=data, timeout=5)
    except:
        pass

def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in, total_out, (total_in - total_out)
    except: return 0.0, 0.0, 0.0

def process_voice(text):
    if not text: return "Others", "", ""
    raw_text = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw_text)
    amount = nums[0] if nums else ""
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട"]): category = "Shop"
    return category, amount, clean_desc

# --- 4. APP ---
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
    t_in, t_out, balance = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #E0B0FF;">Available Balance</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        
        if st.session_state.last_wa_url:
            st.success("Entry Saved! ✅ (Sending to Sheet...)")
            st.markdown(f'<a href="{st.session_state.last_wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">🚀 SEND WHATSAPP</button></a>', unsafe_allow_html=True)
            if st.button("➕ Add New Entry"):
                st.session_state.last_wa_url = None
                st.rerun()
        else:
            v_raw = speech_to_text(language='ml', key='voice_v6_1')
            v_cat, v_amt, v_desc = process_voice(v_raw)
            
            with st.form("entry_form", clear_on_submit=True):
                it = st.text_input("Description", value=v_desc)
                am_str = st.text_input("Amount", value=str(v_amt))
                cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Others"])
                ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
                
                if st.form_submit_button("QUICK SAVE"):
                    try:
                        am = float(am_str.strip().replace(',', ''))
                        if it and am > 0:
                            d, c = (am, 0) if ty == "Debit" else (0, am)
                            
                            # 🟢 ഡാറ്റ റെഡിയാക്കുന്നു
                            payload = {
                                "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                                "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}",
                                "entry.1460982454": d,
                                "entry.1221658767": c
                            }
                            
                            # 🟢 മൾട്ടി-ത്രെഡിംഗ് ഉപയോഗിച്ച് ബാക്ക്ഗ്രൗണ്ടിൽ അയക്കുന്നു (ഇതാണ് സ്പീഡ് കൂട്ടുന്നത്)
                            threading.Thread(target=send_data_async, args=(payload,)).start()
                            
                            msg = f"✅ *Entry Saved!*\n📝 Item: {it}\n💰 Amount: ₹{am}\n👤 User: {curr_user}"
                            st.session_state.last_wa_url = f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}"
                            st.rerun()
                        else: st.error("Details നൽകുക!")
                    except: st.error("നമ്പർ മാത്രം നൽകുക!")

    elif page == "🏠 Dashboard":
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 20px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 20px;">
                <p style="color: #E0B0FF;">Net Balance</p>
                <h1>₹{balance:,.2f}</h1>
            </div>
        """, unsafe_allow_html=True)

    elif page == "🔍 History":
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1], use_container_width=True)
