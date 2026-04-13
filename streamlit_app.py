import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io
from PIL import Image
import easyocr
import numpy as np
import re

# 1. ലിങ്കുകളും ലോഗിൻ വിവരങ്ങളും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v28", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"

# OCR Reader Initialize (EasyOCR)
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en'])

reader = get_ocr_reader()

# CSS - ഗോൾഡൻ തീം & 3x3 ബട്ടൺ ലേഔട്ട്
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; min-width: 300px !important; }
    
    /* 3x3 Grid Buttons */
    div.stButton > button {
        border-radius: 20px !important;
        width: 85px !important;
        height: 85px !important;
        border: 2px solid #FFD700 !important;
        background-color: #1e293b !important;
        color: #FFD700 !important;
        font-size: 30px !important;
        box-shadow: 0px 4px 0px #AA771C;
        margin-bottom: 5px;
    }
    div.stButton > button:active { transform: translateY(4px); box-shadow: none; }
    .btn-label { color: #FFD700; font-size: 11px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .balance-box { background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            st.rerun()
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            res = requests.get(f"{CSV_URL}&r={random.randint(1,999)}")
            df = pd.read_csv(io.StringIO(res.text))
            for c in ['Amount','Debit','Credit']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- 📱 SIDEBAR 3x3 NAVIGATION ---
    st.sidebar.markdown("<h2 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h2>", unsafe_allow_html=True)
    menu = [
        ("🏠", "🏠 Dashboard"), ("💰", "💰 Entry"), ("🤝", "🤝 Tracker"),
        ("📸", "📸 Scan Bill"), ("📊", "📊 Report"), ("📄", "📄 Copy"),
        ("🌙", "🌙 Peace"), ("⚙️", "⚙️ Setup"), ("🚪", "Logout")
    ]

    for i in range(0, len(menu), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(menu):
                icon, name = menu[idx]
                with cols[j]:
                    if st.button(icon, key=f"nav_{idx}"):
                        if name == "Logout": st.session_state.auth = False
                        else: st.session_state.page = name
                        st.rerun()
                    st.markdown(f"<p class='btn-label'>{name.split()[-1]}</p>", unsafe_allow_html=True)

    # --- CONTENT ---
    page = st.session_state.page

    if "Dashboard" in page:
        st.title(f"Welcome {st.session_state.user}")
        if df is not None:
            bal = df['Credit'].sum() - (df['Debit'].sum() + df['Amount'].sum())
            st.markdown(f'<div class="balance-box">Total Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)

    elif "Scan Bill" in page:
        st.title("📸 Scan Bill (EasyOCR)")
        file = st.file_uploader("ഗാലറിയിൽ നിന്ന് ബില്ല് എടുക്കുക", type=['jpg','png','jpeg'])
        if file:
            img = Image.open(file)
            st.image(img, width=300)
            
            # Image to Text
            with st.spinner('ബില്ല് സ്കാൻ ചെയ്യുന്നു...'):
                result = reader.readtext(np.array(img), detail=0)
                full_text = " ".join(result)
                
                # Finding Amount
                amounts = re.findall(r'(?:Total|INR|Rs|₹|Paid)\s*[:]*\s*([\d,]+\.?\d*)', full_text, re.IGNORECASE)
                suggested_am = float(amounts[-1].replace(',', '')) if amounts else 0.0
                suggested_it = result[0] if result else "Bill Entry"

            with st.form("scan_save"):
                it = st.text_input("Item", value=suggested_it)
                am = st.number_input("Amount", value=suggested_am)
                if st.form_submit_button("CONFIRM & SAVE"):
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[Scan] {it}", "entry.1460982454": am, "entry.1221658767": 0})
                    st.success("സേവ് ചെയ്തു! ✅")

    elif "Entry" in page:
        st.title("💰 Add Entry")
        with st.form("manual"):
            it = st.text_input("Item")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")

    elif "Report" in page:
        st.title("📊 Analysis")
        if df is not None:
            fig = px.pie(df[df['Debit']>0], values='Debit', names='Item', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
