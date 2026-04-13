import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io
from PIL import Image

# 1. ലിങ്കുകളും ലോഗിൻ വിവരങ്ങളും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v27", layout="wide")

if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം & 3x3 ബട്ടൺ സ്റ്റൈൽ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; min-width: 320px !important; }
    
    /* 3x3 Button Grid */
    div.stButton > button {
        border-radius: 20px !important;
        width: 85px !important;
        height: 85px !important;
        border: 2px solid #FFD700 !important;
        background-color: #1e293b !important;
        color: #FFD700 !important;
        font-size: 28px !important;
        box-shadow: 0px 4px 0px #AA771C;
        margin-bottom: 5px;
    }
    div.stButton > button:active { transform: translateY(4px); box-shadow: none; }
    .btn-label { color: #FFD700; font-size: 10px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
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

    # --- 📱 SIDEBAR 3x3 GRID NAVIGATION ---
    st.sidebar.markdown("<h2 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h2>", unsafe_allow_html=True)
    menu = [
        ("🏠", "🏠 Dashboard"), ("💰", "💰 Entry"), ("🤝", "🤝 Tracker"),
        ("📸", "📸 Photo Add"), ("📊", "📊 Report"), ("📄", "📄 Copy"),
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
        st.title("🏠 Dashboard")
        if df is not None:
            bal = df['Credit'].sum() - (df['Debit'].sum() + df['Amount'].sum())
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)

    elif "Entry" in page:
        st.title("💰 Add Entry")
        with st.form("entry_form"):
            it = st.text_input("Item")
            am = st.number_input("Amount", min_value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")

    elif "Tracker" in page:
        st.title("🤝 Debt Tracker")
        with st.form("debt_form"):
            name = st.text_input("ആളുടെ പേര്")
            amt = st.number_input("തുക", min_value=0)
            mode = st.selectbox("വിഭാഗം", ["Borrowed (വാങ്ങി)", "Lent (കൊടുത്തു)"])
            if st.form_submit_button("RECORD DEBT"):
                if name and amt:
                    add_log(f"Debt: {name} - ₹{amt} ({mode})")
                    st.success(f"{name} എന്നയാളുടെ വിവരം സേവ് ചെയ്തു!")

    elif "Photo Add" in page:
        st.title("📸 Photo വഴി ചിലവ് ചേർക്കുക")
        img_file = st.file_uploader("ബില്ലിന്റെയോ സാധനത്തിന്റെയോ ഫോട്ടോ എടുക്കുക", type=['jpg', 'png', 'jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, caption="Uploaded Photo", width=300)
            st.warning("ഫോട്ടോയിലെ വിവരങ്ങൾ താഴെ നൽകി സേവ് ചെയ്യുക.")
            with st.form("photo_entry"):
                p_it = st.text_input("ഫോട്ടോയിലുള്ളത് എന്താണ്?", value="Bill Entry")
                p_am = st.number_input("Amount", min_value=0)
                if st.form_submit_button("SAVE PHOTO DATA"):
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[Photo] {p_it}", "entry.1460982454": p_am, "entry.1221658767": 0})
                    st.success("ഫോട്ടോ ഡാറ്റ സേവ് ചെയ്തു!")

    elif "Report" in page:
        st.title("📊 Analysis")
        if df is not None:
            fig = px.pie(df[df['Debit']>0], values='Debit', names='Item', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="log-container" style="color:white; font-size:10px;">{"<br>".join(st.session_state.app_logs[:5])}</div>', unsafe_allow_html=True)
