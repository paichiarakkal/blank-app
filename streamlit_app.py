import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from PIL import Image
import easyocr
import numpy as np
import re
import io

# 1. Configuration
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance", layout="wide")

@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = get_ocr_reader()

# Custom Golden Theme
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    div.stButton > button {
        border-radius: 20px !important;
        width: 80px !important; height: 80px !important;
        background-color: #1e293b !important;
        color: #FFD700 !important; border: 2px solid #FFD700 !important;
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
    # Sidebar
    st.sidebar.title("NAVY")
    if st.sidebar.button("🏠 Dashboard"): st.session_state.page = "🏠 Dashboard"; st.rerun()
    if st.sidebar.button("📸 Scan Bill"): st.session_state.page = "📸 Scan Bill"; st.rerun()
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    if st.session_state.page == "📸 Scan Bill":
        st.title("📸 Scan Bill")
        file = st.file_uploader("Upload Bill", type=['jpg','png','jpeg'])
        if file:
            img = Image.open(file)
            st.image(img, width=300)
            with st.spinner('Scanning...'):
                res_ocr = reader.readtext(np.array(img), detail=0)
                full_text = " ".join(res_ocr)
                
                # --- Advanced Amount Extraction ---
                # തീയതികൾ (2026 പോലെ) ഒഴിവാക്കി ₹ അല്ലെങ്കിൽ തുക മാത്രമായി കണ്ടെത്താൻ
                suggested_am = 0.0
                potential_amounts = []
                for text in res_ocr:
                    # ₹ ചിഹ്നമുള്ള തുകകൾ നോക്കുന്നു
                    if '₹' in text:
                        val = text.replace('₹', '').replace(',', '').strip()
                        try: potential_amounts.append(float(val))
                        except: pass
                
                if not potential_amounts:
                    # ₹ ചിഹ്നം ഇല്ലെങ്കിൽ വലിയ സംഖ്യകൾ തിരയുന്നു (തീയതികൾ ഒഴിവാക്കി)
                    nums = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})', full_text)
                    for n in nums:
                        val = n.replace(',', '')
                        if float(val) < 2000: # തീയതികൾ ഒഴിവാക്കാൻ ഒരു പരിധി
                             potential_amounts.append(float(val))

                if potential_amounts:
                    suggested_am = potential_amounts[0]

                # --- Item Detection ---
                suggested_it = "Bill Entry"
                for i, t in enumerate(res_ocr):
                    if "Paid to" in t or "To" in t:
                        if i + 1 < len(res_ocr): suggested_it = res_ocr[i+1]; break

            with st.form("save_scan"):
                it = st.text_input("Item", value=suggested_it)
                am = st.number_input("Amount", value=float(suggested_am))
                if st.form_submit_button("CONFIRM & SAVE"):
                    data = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": it, "entry.1460982454": am, "entry.1221658767": 0}
                    requests.post(FORM_API, data=data)
                    st.success("Saved! ✅")

    elif st.session_state.page == "🏠 Dashboard":
        st.title(f"🏠 Welcome {st.session_state.user}")
