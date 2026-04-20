import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI ULTIMATE v17.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM GLASS DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1A0521 0%, #300150 100%); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.8) !important; backdrop-filter: blur(10px); border-right: 1px solid rgba(255,255,255,0.1); }
    .glass-card { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; border: 1px solid #FFD700; text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { background: #FFD700; color: #000; border-radius: 12px; font-weight: bold; width: 100%; height: 50px; border: none; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. DATA ENGINE ---
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&nocache={random.randint(1,9999)}")
        df.columns = df.columns.str.strip()
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except: return None

# --- 4. MAIN APP ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
        else: st.error("Access Denied!")
else:
    user = st.session_state.user
    df = load_data()
    total_bal = df['Credit'].sum() - df['Debit'].sum() if df is not None else 0

    if user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Transaction Entry")
        st.markdown(f'<div class="glass-card"><h3>Live Net Balance</h3><h1 style="color:#FFD700 !important; font-size:60px; margin:0;">₹{total_bal:,.2f}</h1></div>', unsafe_allow_html=True)
        
        v = speech_to_text(language='ml', key='v_rec')
        with st.form("entry_form"):
            it = st.text_input("Details (മലയാളത്തിലും പറയാം)", value=v if v else "")
            am = st.number_input("Amount", min_value=1.0, step=0.5, value=None, placeholder="Enter value...")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE TO SHEET"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%d/%m/%Y"), 
                        "entry.2013476337": f"[{user.capitalize()}] {it}", 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    })
                    st.success("സേവ് ചെയ്തു! ✅"); st.rerun()

    elif page == "🔍 History":
        st.title("Transaction History")
        if df is not None:
            # ആവശ്യമില്ലാത്ത കോളങ്ങൾ (Amount, Timestamp) ഒഴിവാക്കുന്നു
            clean_df = df[['Date', 'Item', 'Debit', 'Credit']].copy()
            st.dataframe(clean_df.iloc[::-1], use_container_width=True, hide_index=True)

    elif page == "🏠 Dashboard":
        st.title("Overview")
        st.markdown(f'<div class="glass-card"><h1>₹{total_bal:,.2f}</h1><p>Available Balance</p></div>', unsafe_allow_html=True)

    elif page == "📊 Advisor":
        st.title("Trading Advisor")
        st.info("മാർക്കറ്റ് അപ്‌ഡേറ്റുകൾ ഇവിടെ വരും...")

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
