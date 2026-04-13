import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from PIL import Image
import easyocr
import numpy as np
import re
import io

# 1. Configuration & URLs
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance", layout="wide")

# EasyOCR Loader (Removed Pytesseract to fix error)
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = get_ocr_reader()

# Custom Golden Theme CSS
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
    # --- 📱 Sidebar Navigation ---
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

    # --- Page Routing ---
    if st.session_state.page == "📸 Scan Bill":
        st.title("📸 Scan Bill")
        file = st.file_uploader("Upload Bill Image", type=['jpg','png','jpeg'])
        if file:
            img = Image.open(file)
            st.image(img, width=300)
            with st.spinner('Scanning Bill...'):
                res_ocr = reader.readtext(np.array(img), detail=0)
                full_text = " ".join(res_ocr)
                
                # --- Improved Amount Detection Logic ---
                # തിരയേണ്ട പാറ്റേൺ: ₹230.00, 230.00, 230, Rs 230
                amount_pattern = r'(?:₹|Rs|INR)?\s?([\d,]+\.?\d*)'
                all_numbers = re.findall(amount_pattern, full_text)
                
                suggested_am = 0.0
                valid_amounts = []
                for val in all_numbers:
                    clean_val = val.replace(',', '')
                    try:
                        f_val = float(clean_val)
                        if 1.0 <= f_val < 100000.0: # വളരെ ചെറിയ സംഖ്യകളും വലിയ ഐഡികളും ഒഴിവാക്കാൻ
                            valid_amounts.append(f_val)
                    except: continue
                
                if valid_amounts:
                    # സാധാരണയായി പേയ്‌മെന്റ് സ്‌ക്രീനുകളിൽ ഏറ്റവും വലിയ സംഖ്യയായിരിക്കും തുക
                    suggested_am = max(valid_amounts)

                # --- Improved Item/Name Detection ---
                suggested_it = "Bill Entry"
                for k, text in enumerate(res_ocr):
                    if any(x in text for x in ["Paid to", "To:", "To"]):
                        if k + 1 < len(res_ocr): suggested_it = res_ocr[k+1]; break

            with st.form("save_scan"):
                it = st.text_input("Item", value=suggested_it)
                am = st.number_input("Amount", value=float(suggested_am), step=1.0)
                if st.form_submit_button("CONFIRM & SAVE"):
                    data = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                            "entry.2013476337": it, 
                            "entry.1460982454": am, 
                            "entry.1221658767": 0}
                    requests.post(FORM_API, data=data)
                    st.success("Successfully Saved! ✅")
    
    elif st.session_state.page == "🏠 Dashboard":
        st.title(f"🏠 Welcome {st.session_state.user}")
        st.write("Finance app is running smoothly.")
        if st.button("Refresh Data"): st.rerun()
