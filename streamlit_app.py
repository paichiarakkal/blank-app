import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io
from PIL import Image
import pytesseract
import re

# 1. ലിങ്കുകളും ലോഗിൻ വിവരങ്ങളും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v27", layout="wide")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം & മോഡേൺ ഗ്രിഡ് ബട്ടണുകൾ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; min-width: 320px !important; }
    
    /* 3x3 Button Design with Push Effect */
    div.stButton > button {
        border-radius: 20px !important;
        width: 85px !important;
        height: 85px !important;
        border: 2px solid #FFD700 !important;
        background-color: #1e293b !important;
        color: #FFD700 !important;
        font-size: 30px !important;
        box-shadow: 0px 4px 0px #AA771C;
        transition: 0.1s;
        margin-bottom: 5px;
    }
    div.stButton > button:active { 
        transform: translateY(4px) !important; 
        box-shadow: none !important; 
    }
    div.stButton > button:hover { border-color: white !important; }

    .btn-label { color: #FFD700; font-size: 11px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .ai-box { background: rgba(0,0,0,0.85); color: #FFD700; padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            add_log(f"Login success: {u}")
            st.rerun()
        else: st.error("Access Denied!")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            res = requests.get(f"{CSV_URL}&r={random.randint(1,999)}")
            df = pd.read_csv(io.StringIO(res.text))
            for c in ['Amount','Debit','Credit']: 
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- 📱 SIDEBAR 3x3 GRID NAVIGATION ---
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

    # --- PAGE CONTENT ---
    page = st.session_state.page

    if "Dashboard" in page:
        st.title(f"Hi {st.session_state.user}!")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            st.markdown(f'<div class="balance-box">ബാക്കി: ₹{inc - deb:,.2f}</div>', unsafe_allow_html=True)
            st.subheader("🤖 AI Advisor")
            st.markdown('<div class="ai-box">നിങ്ങളുടെ ഫിനാൻഷ്യൽ സ്റ്റാറ്റസ് നോർമൽ ആണ്.</div>', unsafe_allow_html=True)

    elif "Entry" in page:
        st.title("💰 Add Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form"):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": d, "entry.1221658767": c})
                st.success("സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()

    elif "Tracker" in page:
        st.title("🤝 Debt Tracker")
        with st.form("debt"):
            name = st.text_input("ആളുടെ പേര്")
            amt = st.number_input("തുക", min_value=0)
            cat = st.selectbox("വിഭാഗം", ["Borrowed (വാങ്ങി)", "Lent (കൊടുത്തു)"])
            if st.form_submit_button("SAVE DEBT"):
                add_log(f"Debt: {name} - ₹{amt} ({cat})")
                st.success(f"{name} വിവരം ലോഗ് ചെയ്തു!")

    elif "Scan Bill" in page:
        st.title("📸 Scan Bill (Auto)")
        file = st.file_uploader("ബില്ലിന്റെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക", type=['jpg', 'jpeg', 'png'])
        if file:
            img = Image.open(file)
            st.image(img, caption="Uploaded", width=300)
            
            # OCR logic to extract data
            raw_text = pytesseract.image_to_string(img)
            found_amounts = re.findall(r'(?:Total|INR|Rs|₹|Paid)\s*[:]*\s*([\d,]+\.?\d*)', raw_text, re.IGNORECASE)
            
            # ഗാലറി ബില്ലിൽ നിന്ന് ഷോപ്പ് പേര് എടുക്കുന്നു
            lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
            suggested_it = lines[0] if lines else "Bill Entry"
            suggested_am = 0.0
            if found_amounts:
                suggested_am = float(found_amounts[-1].replace(',', '')) # സാധാരണ ടോട്ടൽ അവസാനം വരും

            with st.form("scan_form"):
                sc_it = st.text_input("Item Detected", value=suggested_it)
                sc_am = st.number_input("Amount Detected", value=suggested_am)
                if st.form_submit_button("CONFIRM & SAVE"):
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[Scan] {sc_it}", "entry.1460982454": sc_am, "entry.1221658767": 0})
                    st.success("വിജയകരമായി ചേർത്തു! ✅")

    elif "Report" in page:
        st.title("📊 Charts")
        if df is not None:
            sdf = df.groupby('Item')['Debit'].sum().reset_index()
            fig = px.pie(sdf[sdf['Debit']>0], values='Debit', names='Item', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    elif "Copy" in page:
        st.title("📄 Data Sheet")
        if df is not None: st.dataframe(df.tail(20), use_container_width=True)
