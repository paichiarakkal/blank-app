import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. അടിസ്ഥാന വിവരങ്ങൾ
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"},
    "admin": {"pw": "paichi786", "role": "admin"}
}

# നിങ്ങളുടെ ഗൂഗിൾ ഷീറ്റ് ലിങ്ക്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
# നിങ്ങളുടെ ഗൂഗിൾ ഫോം ലിങ്ക്
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Finance", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 🎨 ORIGINAL STYLE ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FAMILY LOGIN")
    u = st.text_input("Username").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u in USERS and USERS[u]["pw"] == p:
            st.session_state.auth = True
            st.session_state.user = u.capitalize()
            st.session_state.role = USERS[u]["role"]
            st.rerun()
        else:
            st.error("Access Denied!")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
            df.columns = df.columns.str.strip()
            for c in ['Debit', 'Credit']:
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()
    st.sidebar.title(f"👤 {st.session_state.user}")
    
    pages = ["💰 Add Entry"]
    if st.session_state.role == "admin":
        pages = ["🏠 Dashboard", "💰 Add Entry", "🔍 Search"]
    
    page = st.sidebar.radio("Menu", pages)

    # --- 🏠 DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title("Financial Summary")
        if df is not None:
            bal = df['Credit'].sum() - df['Debit'].sum()
            st.markdown(f'<div class="balance-box">Total Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            st.subheader("Recent Entries")
            st.dataframe(df.iloc[::-1].head(15), use_container_width=True)

    # --- 💰 ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("New Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": f"[{st.session_state.user}] {it}", 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    }
                    requests.post(FORM_API, data=payload)
                    st.success("Entry Saved! ✅")
                    st.cache_data.clear()

    # --- 🔍 SEARCH ---
    elif page == "🔍 Search":
        st.title("Search History")
        s = st.text_input("Search...")
        if df is not None:
            res = df[df['Item'].str.contains(s, case=False, na=False)]
            st.dataframe(res.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
