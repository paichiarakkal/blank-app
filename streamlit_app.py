import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. ലിങ്കുകളും ലോഗിൻ വിവരങ്ങളും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v26.8", layout="wide", initial_sidebar_state="expanded")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Home Dashboard"

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

def nav(p):
    st.session_state.page = p

# --- CSS: SIDEBAR 3x3 GRID & GOLD THEME ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    
    /* സൈഡ്‌ബാർ ഡിസൈൻ */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        min-width: 300px !important;
        border-right: 2px solid #FFD700;
    }

    /* സൈഡ്‌ബാറിലെ 3x3 ഗ്രിഡ് */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 5px !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div {
        width: 33% !important;
        min-width: 33% !important;
    }

    /* റൗണ്ട് ബട്ടണുകൾ */
    .stSidebar .stButton > button {
        background-color: #1a1a1a !important;
        color: #FFD700 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 50% !important;
        height: 70px !important;
        width: 70px !important;
        margin: 5px auto !important;
        display: flex !important;
        align-items: center;
        justify-content: center;
        font-size: 20px !important;
    }
    
    .side-label {
        text-align: center;
        font-size: 10px;
        color: #FFD700;
        font-weight: bold;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .ai-box { background: rgba(0,0,0,0.85); color: #FFD700; padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 20px; font-weight: bold; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN SECTION ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u.capitalize()
                add_log(f"Login success: {u}")
                st.rerun()
            else:
                st.error("Access Denied!")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: 
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- 📱 SIDEBAR 3x3 GRID MENU ---
    with st.sidebar:
        st.markdown(f"<h3 style='text-align: center; color: #FFD700;'>👤 {st.session_state.user}</h3>", unsafe_allow_html=True)
        st.write("---")
        
        # Row 1
        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.button("🏠", on_click=nav, args=("🏠 Home Dashboard",))
        r1c1.markdown("<p class='side-label'>Home</p>", unsafe_allow_html=True)
        r1c2.button("💰", on_click=nav, args=("💰 Add Entry",))
        r1c2.markdown("<p class='side-label'>Add</p>", unsafe_allow_html=True)
        r1c3.button("🤝", on_click=nav, args=("🤝 Debt Tracker",))
        r1c3.markdown("<p class='side-label'>Debt</p>", unsafe_allow_html=True)

        # Row 2
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.button("📄", on_click=nav, args=("📄 View Sheet Copy",))
        r2c1.markdown("<p class='side-label'>Sheet</p>", unsafe_allow_html=True)
        r2c2.button("📊", on_click=nav, args=("📊 Expense Report",))
        r2c2.markdown("<p class='side-label'>Report</p>", unsafe_allow_html=True)
        r2c3.button("🔄", on_click=st.rerun)
        r2c3.markdown("<p class='side-label'>Sync</p>", unsafe_allow_html=True)

        st.write("---")
        if st.button("🚪 LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    # --- PAGES LOGIC ---
    page = st.session_state.page

    if page == "🏠 Home Dashboard":
        st.title(f"Welcome, {st.session_state.user}!")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            bal = inc - deb
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            st.subheader("🤖 AI Advisor")
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            ratio = (deb / inc * 100) if inc > 0 else 0
            if ratio > 80: st.write("⚠️ ചിലവ് കൂടുതലാണ്, നിയന്ത്രിക്കുക.")
            elif ratio < 40 and inc > 0: st.write("✅ മികച്ച സമ്പാദ്യശീലം!")
            else: st.write("📊 നിലവിൽ കുഴപ്പമില്ല.")
            st.markdown('</div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("New Entry")
        v = speech_to_text(language='ml', key='voice_input')
        with st.form("main_entry", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            am = st.number_input("Amount (തുക)", value=None)
            ty = st.radio("Type", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("Saved! ✅")
                    st.cache_data.clear()

    # (മറ്റ് പേജുകൾ ഡീഫോൾട്ട് ആയി താഴെ വരും...)
    else:
        st.title(page)
        st.info("ഈ സെക്ഷൻ റെഡിയാണ്.")
