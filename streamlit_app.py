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

st.set_page_config(page_title="PAICHI v15.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1A0521 0%, #300150 100%); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.8) !important; backdrop-filter: blur(10px); }
    .glass-card { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    .bal-text { color: #FFD700 !important; font-size: 55px !important; font-weight: bold; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { background: #FFD700; color: #000; border-radius: 12px; font-weight: bold; width: 100%; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. POWERFUL DATA ENGINE ---
def load_clean_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
        df.columns = df.columns.str.strip()
        # നമ്പറുകൾ കറക്റ്റ് ആയി മാറ്റുന്നു
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    user = st.session_state.user
    df = load_clean_data()
    
    # ബാലൻസ് കൃത്യമായി കണക്കാക്കുന്നു
    total_bal = 0
    if df is not None:
        total_bal = df['Credit'].sum() - df['Debit'].sum()

    if user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Transaction")
        st.markdown(f'<div class="glass-card"><h3>Total Net Balance</h3><p class="bal-text">₹{total_bal:,.0f}</p></div>', unsafe_allow_html=True)
        v = speech_to_text(language='ml', key='v')
        with st.form("entry_f"):
            it = st.text_input("Details", value=v if v else "")
            am = st.number_input("Amount", min_value=1, value=None)
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
        st.title("History")
        if df is not None:
            # പുതിയത് മുകളിൽ വരാൻ
            st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "🏠 Dashboard":
        st.title("Balance Overview")
        st.markdown(f'<div class="glass-card"><h1 style="font-size:70px;">₹{total_bal:,.2f}</h1></div>', unsafe_allow_html=True)

    elif page == "📊 Advisor":
        st.title("Market Advisor")
        st.info("ഈ സെക്ഷൻ അപ്‌ഡേറ്റ് ആകുന്നു...")

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
