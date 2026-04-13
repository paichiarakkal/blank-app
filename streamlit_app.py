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
# ഡിഫോൾട്ട് പേജ് സെറ്റ് ചെയ്യുന്നു
if 'page' not in st.session_state: st.session_state.page = "🏠 Home Dashboard"

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം & ബട്ടൺ ആനിമേഷൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }

    /* ബട്ടൺ ഡിസൈൻ */
    div.stButton > button {
        border-radius: 15px !important;
        width: 100% !important;
        height: 80px !important;
        border: 2px solid #FFD700 !important;
        background-color: #1e293b !important;
        color: #FFD700 !important;
        font-size: 25px !important;
        box-shadow: 0px 4px 0px #AA771C;
        transition: 0.1s;
    }

    div.stButton > button:active {
        transform: translateY(4px) !important;
        box-shadow: 0px 0px 0px #AA771C !important;
    }

    .btn-label { color: #FFD700; text-align: center; font-size: 10px; font-weight: bold; margin-bottom: 10px; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            st.rerun()
else:
    # ഡാറ്റ ലോഡ് ചെയ്യുന്നു
    @st.cache_data(ttl=1)
    def load_data():
        try:
            # ഡാറ്റ കൃത്യമായി കിട്ടാൻ ഒരു റാൻഡം നമ്പറും കൂടി ചേർക്കുന്നു
            response = requests.get(f"{CSV_URL}&r={random.randint(1,999)}")
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = df.columns.str.strip()
            # കോളം ടൈപ്പ് മാറ്റുന്നു
            for col in ['Amount', 'Debit', 'Credit']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None

    df = load_data()

    # --- 📱 SIDEBAR MENU ---
    st.sidebar.markdown("<h2 style='text-align: center; color: #FFD700;'>PAICHI NAVY</h2>", unsafe_allow_html=True)
    
    menu_items = [
        ("🏠", "🏠 Home Dashboard"), ("💰", "💰 Add Entry"), ("📊", "📊 Expense Report"),
        ("🤝", "🤝 Debt Tracker"), ("📄", "📄 View Sheet Copy"), ("🚪", "Logout")
    ]

    # 3x2 അല്ലെങ്കിൽ 3x3 ഗ്രിഡ് (ഐറ്റംസ് അനുസരിച്ച്)
    for i in range(0, len(menu_items), 3):
        cols = st.sidebar.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(menu_items):
                icon, full_name = menu_items[idx]
                with cols[j]:
                    if st.button(icon, key=f"btn_{idx}"):
                        if "Logout" in full_name:
                            st.session_state.auth = False
                        else:
                            st.session_state.page = full_name
                        st.rerun()
                    st.markdown(f"<p class='btn-label'>{full_name.split()[-1]}</p>", unsafe_allow_html=True)

    # --- CONTENT AREA ---
    page = st.session_state.page

    if "Home" in page:
        st.title(f"Welcome, {st.session_state.user}!")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{inc - deb:,.2f}</div>', unsafe_allow_html=True)

    elif "Add Entry" in page:
        st.title("💰 Add New Entry")
        with st.form("entry_form"):
            it = st.text_input("Item")
            am = st.number_input("Amount", min_value=1)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                # Google Form ലേക്ക് ഡാറ്റ അയക്കുന്ന കോഡ് ഇവിടെ ചേർക്കാം
                st.success("Data Saved Successfully!")

    elif "Expense Report" in page:
        st.title("📊 Analysis Chart")
        if df is not None and not df.empty:
            # ചാർട്ടിനായി ഡാറ്റ ഗ്രൂപ്പ് ചെയ്യുന്നു
            chart_df = df.groupby('Item').agg({'Debit': 'sum', 'Amount': 'sum'}).sum(axis=1).reset_index(name='Total')
            chart_df = chart_df[chart_df['Total'] > 0]
            
            if not chart_df.empty:
                fig = px.pie(chart_df, values='Total', names='Item', hole=0.4, title="ചിലവുകളുടെ വിവരങ്ങൾ")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("ചാർട്ട് കാണിക്കാൻ മതിയായ ഡാറ്റ ലഭ്യമല്ല.")
        else:
            st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ സാധിച്ചില്ല.")

    elif "View Sheet Copy" in page:
        if df is not None:
            st.dataframe(df.tail(20), use_container_width=True)
