import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. ലിങ്കുകളും ലോഗിൻ വിവരങ്ങളും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v26.8", layout="wide")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "🏠 Home Dashboard"

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം & സർക്കുലർ ഗ്രിഡ് ബട്ടണുകൾ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    
    /* സൈഡ്ബാർ ഡിസൈൻ */
    section[data-testid="stSidebar"] {
        background-color: #1a2233 !important;
        min-width: 300px !important;
    }

    /* വട്ടത്തിലുള്ള ബട്ടണുകൾ */
    div.stButton > button {
        border-radius: 50% !important;
        width: 70px !important;
        height: 70px !important;
        border: 2px solid #FFD700 !important;
        background-color: transparent !important;
        color: white !important;
        font-size: 25px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: auto;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #FFD700 !important;
        color: black !important;
        transform: scale(1.1);
    }

    /* ബട്ടണിന് താഴെയുള്ള ടെക്സ്റ്റ് */
    .btn-label {
        text-align: center;
        color: #FFD700;
        font-size: 10px;
        font-weight: bold;
        margin-top: 5px;
        text-transform: uppercase;
    }

    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .ai-box { background: rgba(0,0,0,0.85); color: #FFD700; padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 20px; font-weight: bold; }
    .log-container { background: #111; padding: 10px; border-radius: 5px; height: 150px; overflow-y:auto; font-family:monospace; font-size: 11px; color: #00FF00; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN SECTION ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN", key="login_btn"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u.capitalize()
                add_log(f"Login success: {u}")
                st.rerun()
            else:
                st.error("Access Denied!")

else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- 📱 SIDEBAR 3x3 GRID MENU ---
    st.sidebar.markdown("<h2 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: white;'>User: {st.session_state.user}</p>", unsafe_allow_html=True)
    st.sidebar.write("---")

    menu_items = [
        ("🏠", "Home Dashboard"), ("💰", "Add Entry"), ("📊", "Expense Report"),
        ("🤝", "Debt Tracker"), ("📄", "View Sheet Copy"), ("📈", "Chart"),
        ("🌙", "Peace"), ("⚙️", "Settings"), ("🚪", "Logout")
    ]

    # 3x3 ഗ്രിഡ് നിർമ്മാണം
    for i in range(0, len(menu_items), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(menu_items):
                icon, name = menu_items[idx]
                with cols[j]:
                    if st.button(icon, key=f"nav_{idx}"):
                        if name == "Logout":
                            st.session_state.auth = False
                            st.rerun()
                        else:
                            st.session_state.page = name
                            st.rerun()
                    st.markdown(f"<p class='btn-label'>{name.split()[0]}</p>", unsafe_allow_html=True)

    # --- CONTENT DISPLAY ---
    page = st.session_state.page

    if page == "Home Dashboard":
        st.title(f"Welcome, {st.session_state.user}!")
        if df is not None:
            bal = df['Credit'].sum() - (df['Debit'].sum() + df['Amount'].sum())
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            st.subheader("🤖 AI Advisor")
            st.markdown('<div class="ai-box">നിങ്ങളുടെ ഫിനാൻഷ്യൽ സ്റ്റാറ്റസ് ഇപ്പോൾ നോർമൽ ആണ്.</div>', unsafe_allow_html=True)

    elif page == "Add Entry":
        st.title("💰 Add New Entry")
        v = speech_to_text(language='ml', key='voice_input')
        with st.form("main_entry", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().date(), "entry.2013476337": it, "entry.1460982454": d, "entry.1221658767": c})
                    st.success("Saved!")

    elif page == "Expense Report":
        st.title("📊 Report")
        if df is not None:
            sdf = df.groupby('Item')[['Debit','Amount']].sum().sum(axis=1).reset_index(name='T')
            fig = px.pie(sdf[sdf['T']>0], values='T', names='Item', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    # --- LOGS IN SIDEBAR ---
    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="log-container">{"<br>".join(st.session_state.app_logs)}</div>', unsafe_allow_html=True)
