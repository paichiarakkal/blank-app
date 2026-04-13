import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io
import re

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI ROWDY FINANCE", layout="wide")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Home"
if 'app_logs' not in st.session_state: st.session_state.app_logs = []

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - "ROWDY" GOLDEN THEME & ANIMATIONS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #000, #AA771C); color: #fff; }
    
    /* Sidebar Rowdy Styling */
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 2px solid #FFD700; min-width: 320px !important; }
    
    /* Animation for Buttons */
    @keyframes rowdy-glow {
        0% { box-shadow: 0 0 5px #FFD700; }
        50% { box-shadow: 0 0 20px #FFD700, 0 0 30px #BF953F; }
        100% { box-shadow: 0 0 5px #FFD700; }
    }

    div.stButton > button {
        width: 100% !important; height: 95px !important;
        border-radius: 12px !important;
        background: #111 !important;
        color: #FFD700 !important;
        border: 2px solid #FFD700 !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        transition: 0.2s;
        animation: rowdy-glow 2s infinite;
        margin-bottom: 5px !important;
    }
    
    div.stButton > button:hover {
        transform: scale(1.08) rotate(1deg) !important;
        background: #FFD700 !important;
        color: #000 !important;
        border: 2px solid #fff !important;
    }

    .balance-box { background: #111; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 4px solid #FFD700; box-shadow: 0 0 15px #FFD700; }
    .log-container { background: #111; padding: 10px; border-radius: 5px; height: 100px; overflow-y:auto; font-size: 11px; color: #FFD700; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.auth:
    st.title("🔥 PAICHI ROWDY LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("ENTER SYSTEM"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            st.rerun()
else:
    # --- SIDEBAR 3x3 ROWDY GRID ---
    st.sidebar.markdown("<h1 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h1>", unsafe_allow_html=True)
    
    menu_items = [
        ("🏠", "🏠 Home"), ("💰", "💰 Entry"), ("🤝", "🤝 Debt"),
        ("📄", "📄 Sheet"), ("📊", "📊 Chart"), ("🎙️", "🎙️ Voice"),
        ("📱", "📱 App"), ("⚙️", "⚙️ Setup"), ("🚪", "Logout")
    ]

    for i in range(0, len(menu_items), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            if i + j < len(menu_items):
                icon, name = menu_items[i+j]
                with cols[j]:
                    # ബട്ടണിനുള്ളിൽ പേര് വരാൻ \n ഉപയോഗിക്കുന്നു
                    if st.button(f"{icon}\n{name.split()[-1]}", key=f"rowdy_{i+j}"):
                        if name == "Logout":
                            st.session_state.auth = False
                        else:
                            st.session_state.page = name
                        st.rerun()

    # Data Load
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- PAGES ---
    if st.session_state.page == "🏠 Home":
        st.title(f"🔥 Welcome Leader, {st.session_state.user}")
        if df is not None:
            bal = df['Credit'].sum() - (df['Debit'].sum() + df['Amount'].sum())
            st.markdown(f'<div class="balance-box">CASH: ₹{bal:,.2f}</div>', unsafe_allow_html=True)

    elif st.session_state.page == "🎙️ Voice":
        st.title("🎙️ വോയിസ് എൻട്രി (Rowdy Style)")
        st.write("പറയൂ Faisal, ഞാൻ കേൾക്കുന്നുണ്ട്...")
        text = speech_to_text(language='ml', key='v_rec', start_prompt="Speak Now", stop_prompt="Stop")
        if text:
            st.success(f"Captured: {text}")
            nums = re.findall(r'\d+', text)
            suggested_am = float(nums[0]) if nums else 0.0
            with st.form("v_form"):
                it = st.text_input("Item", value=text)
                am = st.number_input("Amount", value=suggested_am)
                if st.form_submit_button("SAVE VOICE DATA"):
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[Voice] {it}", "entry.1460982454": am, "entry.1221658767": 0})
                    st.success("Boom! Saved. ✅")
                    add_log(f"Voice: {it}")

    elif st.session_state.page == "💰 Entry":
        st.title("💰 Quick Entry")
        with st.form("q_entry"):
            it = st.text_input("What for?")
            am = st.number_input("How much?", value=0.0)
            if st.form_submit_button("CONFIRM ENTRY"):
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": am, "entry.1221658767": 0})
                st.balloons()
                st.success("Entry Added!")

    elif st.session_state.page == "📱 App":
        st.title("📱 System Info")
        st.markdown("### PAICHI OS v28.0\n**Status:** Online\n**Security:** Encrypted")

    elif st.session_state.page == "⚙️ Setup":
        st.title("⚙️ System Setup")
        st.write("Configuring system parameters...")
        st.button("Reset Cache")
        st.button("Sync Data")

    # --- Logs ---
    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="log-container">{"<br>".join(st.session_state.app_logs)}</div>', unsafe_allow_html=True)
