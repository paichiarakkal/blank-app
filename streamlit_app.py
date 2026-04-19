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
USERS = {"faisal": "faisal123", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GLASS v7.5", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 ULTIMATE GLASS DESIGN ---
st.markdown("""
    <style>
    /* Main Purple Background */
    .stApp { 
        background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); 
        color: #fff; 
    }
    
    /* 💎 Transparent Black Glass Sidebar */
    [data-testid="stSidebar"] { 
        background: rgba(0, 0, 0, 0.6) !important; 
        backdrop-filter: blur(25px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important; 
    }
    
    /* 💎 Glass Cards */
    .glass-card { 
        background: rgba(0, 0, 0, 0.4); 
        padding: 25px; 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        backdrop-filter: blur(15px);
        text-align: center; 
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Gold Buttons */
    .stButton>button { 
        background-color: #FFD700 !important; 
        color: #000 !important; 
        border-radius: 12px; 
        border: none;
        width: 100%;
    }
    
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    st.sidebar.title(f"👤 {curr_user.capitalize()}")
    
    # 🔒 Access Control
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        st.sidebar.markdown("---")
        n_alert = st.sidebar.number_input("Nifty Alert", value=0.0)
        c_alert = st.sidebar.number_input("Crude Alert", value=0.0)
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    # --- PAGES ---
    if page == "💰 Add Entry":
        st.title("Quick Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Details", value=v if v else "")
            # എക്സ്ട്രാ പൂജ്യം ഒഴിവാക്കി
            am = st.number_input("Amount", min_value=0, step=1, value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am > 0:
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {it}",
                        "entry.1460982454": am if ty == "Debit" else 0,
                        "entry.1221658767": am if ty == "Credit" else 0
                    })
                    st.success("സേവ് ചെയ്തു! ✅")

    elif page == "📊 Advisor" and curr_user != "shabana":
        st.title("Live Market")
        # Market fetch simulation for clean code
        st.markdown('<div class="glass-card"><h3>Crude Oil</h3><h1 style="color:#FFD700;">Loading...</h1></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Net Balance")
        st.markdown('<div class="glass-card"><h1>₹ 00.00</h1></div>', unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
