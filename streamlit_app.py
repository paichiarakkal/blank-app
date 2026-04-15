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

# --- 🎨 ഹെഡർ, ലോഗോ, എംബ്ലം എന്നിവ നീക്കം ചെയ്യാനുള്ള ശക്തമായ CSS ---
st.markdown("""
    <style>
    /* 1. മുകളിലെ Fork, GitHub, ഹെഡർ ബാർ എന്നിവ പൂർണ്ണമായും ഒഴിവാക്കാൻ */
    header, [data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
    }
    
    /* 2. താഴെയുള്ള Streamlit എംബ്ലവും ബാഡ്ജും ഒഴിവാക്കാൻ */
    footer {display: none !important;}
    .viewerBadge_container__1QS1n, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}

    /* 3. സൈഡ് ബാർ കൃത്യമായി കാണാൻ (ഇത് മറയ്ക്കാൻ പാടില്ല) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.1);
        top: 0px !important;
    }

    /* 4. ബാക്ക്ഗ്രൗണ്ട് തീം */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); 
        color: #000; 
    }
    
    /* തുക കാണിക്കുന്ന ബോക്സ് */
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

# --- 🔐 LOGIN SECTION ---
if not st.session_state.auth:
    st.title("🔐 FAMILY LOGIN")
    u_raw = st.text_input("Username")
    p_raw = st.text_input("Password", type="password")
    
    if st.button("LOGIN"):
        u_clean = u_raw.lower().strip()
        if u_clean in USERS and USERS[u_clean]["pw"] == p_raw:
            st.session_state.auth = True
            st.session_state.user = u_clean.capitalize()
            st.session_state.role = USERS[u_clean]["role"]
            st.rerun()
        else: 
            st.error("Access Denied!")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            # പുതിയ ഡാറ്റ ഉടൻ വരാൻ random string ഉപയോഗിക്കുന്നു
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
            df.columns = df.columns.str.strip()
            for c in ['Debit', 'Credit']:
                if c in df.columns: 
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()
    
    # സൈഡ് ബാറിലെ യൂസർ വിവരങ്ങൾ
    st.sidebar.markdown(f"### 👤 {st.session_state.user}")
    
    menu_options = ["💰 Add Entry"]
    if st.session_state.role == "admin":
        menu_options = ["🏠 Home Dashboard", "💰 Add Entry", "🔍 Search & View", "📊 Expense Report"]
    
    page = st.sidebar.radio("Menu", menu_options)
    
    if st.sidebar.button("Log Out"): 
        st.session_state.auth = False
        st.rerun()

    # --- താളുകൾ (Pages) ---
    if page == "🏠 Home Dashboard":
        st.title("Financial Overview")
        if df is not None:
            # ബാലൻസ് കണക്കാക്കുന്നു
            bal = df['Credit'].sum() - df['Debit'].sum()
            st.markdown(f'<div class="balance-box">Total Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
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
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": f"[{st.session_state.user}] {it}", 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    }
                    requests.post(FORM_API, data=payload)
                    st.success(f"Saved successfully! ✅")
                    st.cache_data.clear()
