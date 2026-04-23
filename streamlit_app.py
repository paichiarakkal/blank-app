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

# നിന്റെ വാട്സാപ്പ് നമ്പർ
MY_PHONE = "918714752210" 
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v5.9", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'last_wa_url' not in st.session_state: st.session_state.last_wa_url = None

# --- 3. 📊 ENGINES ---
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
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "ചായ"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട", "സാധനം"]): category = "Shop"
    elif any(x in raw_text for x in ["travel", "യാത്ര"]): category = "Travel"
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
    t_in, t_out, balance = get_totals()
    
    # Available Balance Banner (എല്ലാവർക്കും കാണാം)
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:18px; color: #E0B0FF;">Available Balance</span><br>
        <span style="font-size:32px; color:#FFD700;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    if curr_user == "shabana":
        menu_options = ["💰 Add Entry"]
    else:
        menu_options = ["🏠 Dashboard", "💰 Add Entry", "📊 Advisor", "📊 Report", "🔍 History", "🤝 Debt Tracker"]

    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    # --- 🏠 DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 20px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 30px;">
                <p style="color: #E0B0FF !important; font-size: 20px; margin-bottom: 10px;">Available Balance</p>
                <h1 style="color: #FFD700 !important; font-size: 45px; margin: 0;">₹{balance:,.2f}</h1>
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3);">
                <h2 style="color: white !important; margin-bottom: 20px; font-size: 28px;">Total Credit: <span style="color: #00FF00;">₹{t_in:,.2f}</span></h2>
                <h2 style="color: white !important; margin: 0; font-size: 28px;">Total Debit: <span style="color: #FF3131;">₹{t_out:,.2f}</span></h2>
            </div>
        """, unsafe_allow_html=True)

    # --- 💰 ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        
        if st.session_state.last_wa_url:
            st.success("Data Saved Successfully! ✅")
            st.markdown(f'<a href="{st.session_state.last_wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer; margin-bottom:20px;">🚀 SEND NOTIFICATION</button></a>', unsafe_allow_html=True)
            if st.button("Add New Entry ➕"):
                st.session_state.last_wa_url = None
                st.rerun()
        else:
            v_raw = speech_to_text(language='ml', key='voice_v5_9')
            v_cat, v_amt, v_desc = process_voice(v_raw)
            
            with st.form("entry_form", clear_on_submit=True):
                it = st.text_input("Description", value=v_desc)
                # ഇവിടെ Amount ബോക്സ് കാലിയായി വരും (0.0 ഒഴിവാക്കി)
                am_str = st.text_input("Amount", value=str(v_amt))
                
                cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
                cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
                ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
                
                if st.form_submit_button("SAVE DATA"):
                    try:
                        am = float(am_str)
                        if it and am > 0:
                            d, c = (am, 0) if ty == "Debit" else (0, am)
                            requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", "entry.1460982454": d, "entry.1221658767": c})
                            
                            msg = f"✅ *Entry Saved!*\n📝 Item: {it}\n💰 Amount: ₹{am}\n👤 User: {curr_user}"
                            st.session_state.last_wa_url = f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}"
                            st.rerun()
                        else: st.error("വിവരങ്ങൾ പൂർണ്ണമായി നൽകുക!")
                    except: st.error("Amount ബോക്സിൽ നമ്പർ മാത്രം നൽകുക!")

    # --- 🔍 HISTORY ---
    elif page == "🔍 History":
        st.title("History 🔍")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    # ... മറ്റ് പേജുകൾ (Advisor, Report) നിന്റെ പഴയ കോഡിൽ ഉള്ളത് പോലെ ഇവിടെയും ചേർക്കാം ...
