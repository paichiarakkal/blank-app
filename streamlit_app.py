import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ലോഗിൻ വിവരങ്ങൾ
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"},
    "admin": {"pw": "paichi786", "role": "admin"}
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Finance", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 🎨 ഹെഡർ ചിഹ്നങ്ങൾ കളയാനും സൈഡ് ബാർ നിലനിർത്താനുമുള്ള CSS ---
st.markdown("""
    <style>
    /* 1. സൈഡ് ബാർ ബട്ടൺ നിലനിർത്തിക്കൊണ്ട് Fork/GitHub ചിഹ്നങ്ങൾ മാത്രം കളയാൻ */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
    
    /* Fork, GitHub, Menu ബട്ടണുകൾ ഹൈഡ് ചെയ്യുന്നു */
    button[title="View source"], 
    .stAppDeployButton, 
    #MainMenu {
        display: none !important;
    }

    /* 2. താഴെയുള്ള റെഡ് ക്രൗൺ എംബ്ലം ഒഴിവാക്കാൻ */
    footer {display: none !important;}
    .viewerBadge_container__1QS1n, [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* 3. കണ്ടന്റ് അല്പം താഴേക്ക് ഇറക്കി വെക്കാൻ (Padding) */
    .block-container {
        padding-top: 5rem !important;
    }

    /* 4. ബാക്ക്ഗ്രൗണ്ട് തീം */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); 
        color: #000; 
    }
    
    .balance-box { 
        background: #000; 
        color: #00FF00; 
        padding: 25px; 
        border-radius: 15px; 
        text-align: center; 
        font-size: 30px; 
        font-weight: bold; 
        border: 3px solid #FFD700; 
    }
    
    h1, h2, h3, label, p { 
        color: black !important; 
        font-weight: bold !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FAMILY LOGIN")
    u_raw = st.text_input("Username")
    p_raw = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        u_clean = u_raw.lower().strip()
        if u_clean in USERS and USERS[u_clean]["pw"] == p_raw:
            st.session_state.auth, st.session_state.user, st.session_state.role = True, u_clean.capitalize(), USERS[u_clean]["role"]
            st.rerun()
        else: st.error("Access Denied!")
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
    
    # സൈഡ് ബാറിലെ ഡിസൈൻ
    st.sidebar.markdown(f"### 👤 {st.session_state.user}")
    
    menu = ["💰 Add Entry"]
    if st.session_state.role == "admin":
        menu = ["🏠 Home Dashboard", "💰 Add Entry", "🔍 Search & View", "📊 Expense Report"]
    
    page = st.sidebar.radio("Menu", menu)
    
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- Pages ---
    if page == "🏠 Home Dashboard":
        st.title("Financial Overview")
        if df is not None:
            bal = df['Credit'].sum() - df['Debit'].sum()
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            st.dataframe(df.iloc[::-1].head(10), use_container_width=True)

    elif page == "💰 Add Entry":
        st.title("Add New Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()
