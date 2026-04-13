import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import io
from PIL import Image
import easyocr
import numpy as np
import re
import cv2

# 1. Config & URLs
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance", layout="wide")

# EasyOCR Loader
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en'])

reader = get_ocr_reader()

# Golden Theme
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; min-width: 300px !important; }
    div.stButton > button {
        border-radius: 20px !important;
        width: 85px !important; height: 85px !important;
        background-color: #1e293b !important;
        color: #FFD700 !important; font-size: 30px !important;
        border: 2px solid #FFD700 !important;
        margin-bottom: 5px;
    }
    .btn-label { color: #FFD700; font-size: 11px; font-weight: bold; text-align: center; margin-bottom: 15px; }
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
    # 📱 Sidebar 3x3 Menu
    st.sidebar.markdown("<h2 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h2>", unsafe_allow_html=True)
    menu = [("🏠", "🏠 Dashboard"), ("💰", "💰 Entry"), ("🤝", "🤝 Tracker"), ("📸", "📸 Scan Bill"), ("📊", "📊 Report"), ("🚪", "Logout")]

    for i in range(0, len(menu), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            if i + j < len(menu):
                icon, name = menu[i + j]
                with cols[j]:
                    if st.button(icon, key=f"nav_{i+j}"):
                        if name == "Logout": st.session_state.auth = False
                        else: st.session_state.page = name
                        st.rerun()
                    st.markdown(f"<p class='btn-label'>{name.split()[-1]}</p>", unsafe_allow_html=True)

    # --- Scan Bill Page (Corrected OCR) ---
    if "Scan Bill" in st.session_state.page:
        st.title("📸 Scan Bill")
        file = st.file_uploader("Upload Bill", type=['jpg','png','jpeg'])
        if file:
            img = Image.open(file)
            st.image(img, width=300)
            with st.spinner('Reading...'):
                res_ocr = reader.readtext(np.array(img), detail=0)
                full_text = " ".join(res_ocr)
                
                # തുക കണ്ടെത്തുന്നു (Transaction ID ഒഴിവാക്കി)
                amounts = re.findall(r'(?:₹|Rs|Total|Paid)\s*[:]*\s*([\d,]+\.?\d*)', full_text, re.IGNORECASE)
                suggested_am = 0.0
                if amounts:
                    valid = [float(a.replace(',', '')) for a in amounts if float(a.replace(',', '')) < 100000]
                    if valid: suggested_am = max(valid)
                
                if suggested_am == 0.0:
                    nums = [float(t.replace(',', '')) for t in res_ocr if t.replace(',', '').replace('.', '').isdigit()]
                    valid = [n for n in nums if n < 100000]
                    if valid: suggested_am = max(valid)

                # പേര് കണ്ടെത്തുന്നു
                suggested_it = "Bill Entry"
                for k, text in enumerate(res_ocr):
                    if any(x in text for x in ["To", "Paid to"]):
                        if k + 1 < len(res_ocr): suggested_it = res_ocr[k+1]; break

            with st.form("ocr_save"):
                it = st.text_input("Item", value=suggested_it)
                am = st.number_input("Amount", value=float(suggested_am))
                if st.form_submit_button("CONFIRM & SAVE"):
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": am, "entry.1221658767": 0})
                    st.success("Successfully Saved! ✅")
