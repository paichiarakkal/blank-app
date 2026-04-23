import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v4.3", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🤖 WHATSAPP NOTIFICATION ENGINE ---
def send_wa_notify(item, amount, category, entry_type):
    # നിങ്ങൾ നൽകിയ പുതിയ API വിവരങ്ങൾ
    api_key = "7463030" 
    phone = "971551347989"
    
    # മെസ്സേജ് ഫോർമാറ്റ്
    msg = f"💳 *PAICHI EXPENSE ALERT* 💳\n\n📝 *Item:* {item}\n💰 *Amount:* AED {amount}\n📂 *Category:* {category}\n📊 *Type:* {entry_type}\n⏰ *Time:* {datetime.now().strftime('%I:%M %p')}"
    
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(msg)}&apikey={api_key}"
    try:
        requests.get(url)
    except:
        pass

# --- 3. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'page_selection' not in st.session_state: st.session_state.page_selection = "🏠 Dashboard"

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    # Sidebar Navigation
    menu_options = ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History"]
    page = st.sidebar.radio("Menu", menu_options, index=menu_options.index(st.session_state.page_selection))
    st.session_state.page_selection = page

    # WhatsApp Support Button
    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<a href="https://wa.me/971551347989" target="_blank"><div style="background-color: #25D366; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; cursor: pointer;">💬 WhatsApp Support</div></a>', unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    # --- PAGES ---
    if page == "💰 Add Entry":
        st.title("Smart Entry & WhatsApp Notify 🎙️")
        v_raw = speech_to_text(language='ml', key='v_v1')
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_raw if v_raw else "")
            am = st.number_input("Amount", min_value=0.0)
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Chicken", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    # 1. Save to Google Form
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    # 2. Send WhatsApp Message
                    send_wa_notify(it, am, cat, ty)
                    
                    st.success("Saved & Notified! ✅")
                    st.session_state.page_selection = "🔍 History"
                    st.rerun()

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        # (Dashboard Logic Here...)
        st.write("Dashboard content loading...")

    elif page == "🔍 History":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.write("No history found.")

    # (Add other pages like Advisor/Report from previous code if needed)
