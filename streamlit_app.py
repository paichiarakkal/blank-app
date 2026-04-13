import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px

# 1. ലോഗിൻ വിവരങ്ങൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance", layout="wide")

# State Management
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Home"

# --- CSS: നിന്റെ സ്റ്റൈൽ ഒട്ടും മാറ്റാതെ സൈഡ്‌ബാർ ഗ്രിഡ് ചേർത്തു ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 2px solid #FFD700; }
    
    /* 3x3 Grid Styling */
    .stSidebar .stButton > button {
        background-color: #1a1a1a !important;
        color: #FFD700 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 15px !important;
        height: 60px !important;
        width: 100% !important;
        font-size: 20px !important;
    }
    .side-text { color: #FFD700; text-align: center; font-size: 10px; font-weight: bold; margin-bottom: 10px; }
    
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; border: 3px solid #FFD700; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# Navigation Function
def set_page(name):
    st.session_state.page = name

# --- LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u.lower()) == p:
            st.session_state.auth = True
            st.session_state.user = u.capitalize()
            st.rerun()
else:
    # --- SIDEBAR 3x3 GRID ---
    with st.sidebar:
        st.markdown(f"<h3 style='color:#FFD700; text-align:center;'>👤 {st.session_state.user}</h3>", unsafe_allow_html=True)
        
        # Row 1
        c1, c2, c3 = st.columns(3)
        c1.button("🏠", on_click=set_page, args=("🏠 Home",))
        c1.markdown("<p class='side-text'>Home</p>", unsafe_allow_html=True)
        c2.button("💰", on_click=set_page, args=("💰 Add",))
        c2.markdown("<p class='side-text'>Add</p>", unsafe_allow_html=True)
        c3.button("🤝", on_click=set_page, args=("🤝 Debt",))
        c3.markdown("<p class='side-text'>Debt</p>", unsafe_allow_html=True)

        # Row 2
        c4, c5, c6 = st.columns(3)
        c4.button("📊", on_click=set_page, args=("📊 Report",))
        c4.markdown("<p class='side-text'>Report</p>", unsafe_allow_html=True)
        c5.button("📄", on_click=set_page, args=("📄 Sheet",))
        c5.markdown("<p class='side-text'>Sheet</p>", unsafe_allow_html=True)
        c6.button("🔄", on_click=st.cache_data.clear)
        c6.markdown("<p class='side-text'>Sync</p>", unsafe_allow_html=True)

        # Row 3
        c7, c8, c9 = st.columns(3)
        c7.button("⚙️", on_click=set_page, args=("⚙️ Settings",))
        c7.markdown("<p class='side-text'>Set</p>", unsafe_allow_html=True)
        if c8.button("🚪"):
            st.session_state.auth = False
            st.rerun()
        c8.markdown("<p class='side-text'>Exit</p>", unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    page = st.session_state.page
    st.title(page)

    if page == "🏠 Home":
        # ഡാറ്റ ലോഡിംഗ് ലോജിക് ഇവിടെ ചേർക്കാം
        st.markdown('<div class="balance-box">ബാക്കി തുക: ₹0.00</div>', unsafe_allow_html=True)
    
    elif page == "💰 Add":
        with st.form("add_form"):
            item = st.text_input("Item")
            amount = st.number_input("Amount", min_value=0)
            if st.form_submit_button("SAVE"):
                st.success("Saved!")

    else:
        st.info(f"{page} സെക്ഷൻ റെഡിയാണ്.")
