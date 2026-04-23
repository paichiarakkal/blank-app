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

# 🟢 നിന്റെ ഒരു വാട്സാപ്പ് നമ്പർ മാത്രം ഇവിടെ നൽകുക
MY_PHONE = "919061611013" 

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v5.1", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
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
    # "ചായ 10" -> "ചായ" എന്ന് മാറ്റുന്നു
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "ചായ", "hotel"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട", "സാധനം", "dress"]): category = "Shop"
    elif any(x in raw_text for x in ["travel", "യാത്ര", "bus", "petrol"]): category = "Travel"
    return category, amount, clean_desc

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
    
    # ബാലൻസ് ഫൈസലിന് മാത്രം (വേണമെങ്കിൽ ഷബാനയ്ക്കും കാണിക്കാം)
    if curr_user != "shabana":
        balance = get_total_balance()
        st.markdown(f'<div class="balance-banner"><span style="font-size:18px;">Total Balance</span><br><span style="font-size:32px; color:#FFD700;">₹{balance:,.2f}</span></div>', unsafe_allow_html=True)

    # മെനു നിയന്ത്രണം
    if curr_user == "shabana":
        menu_options = ["💰 Add Entry"]
    else:
        menu_options = ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]

    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    if page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v5_1')
        v_cat, v_amt, v_desc = process_voice(v_raw)
        
        with st.form("entry_form_v5_1", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc if v_desc else "")
            am = st.number_input("Amount", min_value=0.0, value=v_amt)
            cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
            cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE & NOTIFY"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    # വാട്സാപ്പ് മെസ്സേജ് റെഡിയാക്കുന്നു
                    msg = f"✅ *Paichi Entry Saved!*\n\n📝 Item: {it}\n💰 Amount: ₹{am}\n👤 User: {curr_user}\n📂 Cat: {cat}\n📊 Type: {ty}"
                    wa_url = f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}"
                    
                    st.success("Saved! Click below to send WhatsApp notification.")
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">🚀 SEND WHATSAPP</button></a>', unsafe_allow_html=True)

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Data loading error!")

    # മറ്റ് പേജുകൾ (Advisor, Report etc.) ഇവിടെ ചേർക്കാം...
