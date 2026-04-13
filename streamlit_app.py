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

# 1. ലിങ്കുകളും കോൺഫിഗറേഷനും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v31", layout="wide")

# EasyOCR ലോഡ് ചെയ്യുന്നു
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en'])

reader = get_ocr_reader()

# Image Pre-processing for better OCR
def preprocess_image(image):
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    # Contrast കൂട്ടാൻ
    enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return enhanced

# UI തീം - ഗോൾഡൻ & ഡാർക്ക്
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; min-width: 300px !important; }
    div.stButton > button {
        border-radius: 20px !important;
        width: 85px !important; height: 85px !important;
        border: 2px solid #FFD700 !important;
        background-color: #1e293b !important;
        color: #FFD700 !important; font-size: 30px !important;
        box-shadow: 0px 4px 0px #AA771C; margin-bottom: 5px;
    }
    .btn-label { color: #FFD700; font-size: 11px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .balance-box { background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; }
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
    @st.cache_data(ttl=1)
    def load_data():
        try:
            res = requests.get(f"{CSV_URL}&r={random.randint(1,999)}")
            df = pd.read_csv(io.StringIO(res.text))
            for c in ['Amount','Debit','Credit']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- 📱 3x3 SIDEBAR NAVIGATION ---
    st.sidebar.markdown("<h2 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h2>", unsafe_allow_html=True)
    menu_items = [
        ("🏠", "🏠 Dashboard"), ("💰", "💰 Entry"), ("🤝", "🤝 Tracker"),
        ("📸", "📸 Scan Bill"), ("📊", "📊 Report"), ("📄", "📄 Copy"),
        ("🌙", "🌙 Peace"), ("⚙️", "⚙️ Setup"), ("🚪", "Logout")
    ]

    for i in range(0, len(menu_items), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            if i + j < len(menu_items):
                icon, name = menu_items[i+j]
                with cols[j]:
                    if st.button(icon, key=f"btn_{i+j}"):
                        if name == "Logout": st.session_state.auth = False
                        else: st.session_state.page = name
                        st.rerun()
                    st.markdown(f"<p class='btn-label'>{name.split()[-1]}</p>", unsafe_allow_html=True)

    page = st.session_state.page

    if "Dashboard" in page:
        st.title(f"Welcome {st.session_state.user}")
        if df is not None:
            bal = df['Credit'].sum() - (df['Debit'].sum() + df['Amount'].sum())
            st.markdown(f'<div class="balance-box">Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)

    elif "Scan Bill" in page:
        st.title("📸 Scan Bill")
        file = st.file_uploader("ബില്ലിന്റെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക", type=['jpg','png','jpeg'])
        if file:
            img = Image.open(file)
            st.image(img, width=300)
            with st.spinner('പരിശോധിക്കുന്നു...'):
                processed_img = preprocess_image(img)
                res_ocr = reader.readtext(processed_img, detail=0)
                full_text = " ".join(res_ocr)
                
                # Smart Amount Detection (₹ ചിഹ്നം നോക്കുന്നു)
                amounts = re.findall(r'(?:₹|Rs|Total|Paid)\s*[:]*\s*([\d,]+\.?\d*)', full_text, re.IGNORECASE)
                suggested_am = 0.0
                if amounts:
                    valid_nums = [float(a.replace(',', '')) for a in amounts if float(a.replace(',', '')) < 100000]
                    if valid_nums: suggested_am = max(valid_nums)
                
                # Transaction ID തുകയായി വരുന്നത് തടയുന്നു
                if suggested_am == 0.0:
                    numbers = [float(t.replace(',', '')) for t in res_ocr if t.replace(',', '').replace('.', '').isdigit()]
                    valid_nums = [n for n in numbers if n < 100000]
                    suggested_am = max(valid_nums) if valid_nums else 0.0

                # Smart Item Detection ("To" കഴിഞ്ഞ് വരുന്ന പേര്)
                suggested_it = "Bill Entry"
                for i, text in enumerate(res_ocr):
                    if any(x in text for x in ["To", "Paid to"]):
                        if i + 1 < len(res_ocr): suggested_it = res_ocr[i+1]; break

            with st.form("ocr_save"):
                it = st.text_input("Item", value=suggested_it)
                am = st.number_input("Amount", value=float(suggested_am))
                if st.form_submit_button("CONFIRM & SAVE"):
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": am, "entry.1221658767": 0})
                    st.success("Saved! ✅")
                    st.cache_data.clear()

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
                st.cache_data.clear()
