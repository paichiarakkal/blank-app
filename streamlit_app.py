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

st.set_page_config(page_title="PAICHI Home Finance v27", layout="wide")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Home"
if 'app_logs' not in st.session_state: st.session_state.app_logs = []

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം & അനിമേഷൻ ബട്ടണുകൾ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #0f172a !important; min-width: 320px !important; }
    
    /* 3x3 Grid Buttons Styling */
    div.stButton > button {
        width: 100% !important;
        height: 90px !important;
        border-radius: 15px !important;
        background: linear-gradient(145deg, #1e293b, #0f172a) !important;
        color: #FFD700 !important;
        border: 2px solid #FFD700 !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        margin-bottom: 10px !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-5px) scale(1.02) !important;
        background: #FFD700 !important;
        color: #000 !important;
        box-shadow: 0 0 20px #FFD700 !important;
    }

    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .ai-box { background: rgba(0,0,0,0.85); color: #FFD700; padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 20px; font-weight: bold; }
    .log-container { background: #000; padding: 10px; border-radius: 5px; height: 120px; overflow-y:auto; font-family:monospace; font-size: 10px; color: #00FF00; border: 1px solid #FFD700; }
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
                st.rerun()
            else: st.error("Access Denied!")
else:
    # Sidebar 3x3 Grid Navigation
    st.sidebar.markdown("<h2 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h2>", unsafe_allow_html=True)
    
    # 3x3 ബട്ടണുകൾ സെറ്റ് ചെയ്യുന്നു
    menu_items = [
        ("🏠", "🏠 Home"), ("💰", "💰 Entry"), ("🤝", "🤝 Debt"),
        ("📄", "📄 Sheet"), ("📊", "📊 Chart"), ("🎙️", "🎙️ Voice"),
        ("📱", "📱 App"), ("⚙️", "⚙️ Setup"), ("🚪", "Logout")
    ]

    # Grid നിർമ്മാണം
    for i in range(0, len(menu_items), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            if i + j < len(menu_items):
                icon, name = menu_items[i+j]
                with cols[j]:
                    if st.button(f"{icon}\n{name.split()[-1]}"):
                        if name == "Logout":
                            st.session_state.auth = False
                            st.rerun()
                        else:
                            st.session_state.page = name
                            st.rerun()

    # Data Loading
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- Pages Implementation ---
    if st.session_state.page == "🏠 Home":
        st.title(f"Welcome, {st.session_state.user}!")
        if df is not None:
            bal = df['Credit'].sum() - (df['Debit'].sum() + df['Amount'].sum())
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            st.subheader("🤖 AI Advisor")
            st.markdown('<div class="ai-box">നിങ്ങളുടെ വരുമാനവും ചിലവും ഇപ്പോൾ കൃത്യമായി ട്രാക്ക് ചെയ്യപ്പെടുന്നുണ്ട്.</div>', unsafe_allow_html=True)

    elif st.session_state.page == "💰 Entry":
        st.title("Add New Entry")
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item")
            am = st.number_input("Amount", value=0.0)
            ty = st.selectbox("Type", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"])
            if st.form_submit_button("SAVE DATA"):
                if it and am:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("സേവ് ചെയ്തു! ✅")
                    add_log(f"Added: {it}")

    elif st.session_state.page == "📄 Sheet":
        st.title("History")
        if df is not None: st.dataframe(df.tail(20), use_container_width=True)

    elif st.session_state.page == "📊 Chart":
        st.title("Analysis")
        if df is not None:
            sdf = df.groupby('Item')[['Debit','Amount']].sum().sum(axis=1).reset_index(name='T')
            fig = px.pie(sdf[sdf['T']>0], values='T', names='Item', hole=0.4)
            st.plotly_chart(fig)

    # Sidebar Logs
    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="log-container">{"<br>".join(st.session_state.app_logs)}</div>', unsafe_allow_html=True)
