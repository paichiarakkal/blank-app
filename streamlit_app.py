import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from PIL import Image
import easyocr
import numpy as np
import re

# 1. Configuration
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance", layout="wide")

# EasyOCR Reader
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en'])

reader = get_ocr_reader()

# Golden Theme Styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    div.stButton > button {
        border-radius: 20px !important;
        background-color: #1e293b !important;
        color: #FFD700 !important;
        border: 2px solid #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"

if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            st.rerun()
else:
    # Sidebar Navigation
    st.sidebar.title(f"Welcome, {st.session_state.user}")
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Entry", "📸 Scan Bill"])
    st.session_state.page = page

    if page == "📸 Scan Bill":
        st.title("📸 Scan Bill")
        file = st.file_uploader("Upload Bill Image", type=['jpg','png','jpeg'])
        if file:
            img = Image.open(file)
            st.image(img, width=300)
            with st.spinner('Reading...'):
                res_ocr = reader.readtext(np.array(img), detail=0)
                full_text = " ".join(res_ocr)
                
                # Simple Logic to find Amount
                amounts = re.findall(r'[\d,]+\.\d{2}', full_text)
                suggested_am = float(amounts[0].replace(',', '')) if amounts else 0.0

            with st.form("scan_form"):
                it = st.text_input("Item", value="Bill Entry")
                am = st.number_input("Amount", value=suggested_am)
                if st.form_submit_button("CONFIRM & SAVE"):
                    data = {"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": am}
                    requests.post(FORM_API, data=data)
                    st.success("Saved! ✅")
