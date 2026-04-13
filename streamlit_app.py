import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px

# വോയിസ് റെക്കോർഡർ എറർ ഒഴിവാക്കാൻ (image_8.png പ്രശ്നം പരിഹരിക്കാൻ)
try:
    from streamlit_mic_recorder import speech_to_text
except ImportError:
    st.warning("streamlit-mic-recorder ഇൻസ്റ്റാൾ ചെയ്തിട്ടില്ല. വോയിസ് ഫീച്ചർ വർക്ക് ചെയ്യില്ല.")
    speech_to_text = None

# 1. ലിങ്കുകളും ലോഗിൻ വിവരങ്ങളും (നിന്റെ കോഡിൽ ഉള്ളത്)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Home Finance v26.8", layout="wide", initial_sidebar_state="expanded")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False
# ഡിഫോൾട്ട് പേജ് ഹോം ആയി സെറ്റ് ചെയ്യുന്നു
if 'page' not in st.session_state: st.session_state.page = "🏠 Home Dashboard"

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# പേജ് മാറാനുള്ള ഫങ്ക്ഷൻ (callback)
def nav_to(page_name):
    st.session_state.page = page_name

# സിങ്ക് ചെയ്യാനുള്ള ഫങ്ക്ഷൻ (st.rerun വാണിംഗ് ഒഴിവാക്കാൻ)
def sync_data():
    st.cache_data.clear()
    add_log("Data synced/refreshed.")

# --- CSS: നിന്റെ ഗോൾഡൻ തീമും പുതിയ 3x3 ഗ്രിഡും ---
st.markdown("""
    <style>
    /* നിന്റെ ഗോൾഡൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    
    /* സൈഡ്‌ബാർ കറുപ്പ് നിറം */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        min-width: 300px !important;
        border-right: 2px solid #FFD700;
    }

    /* സൈഡ്‌ബാറിലെ 3x3 ഗ്രിഡ് ക്രമീകരണം */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 5px !important;
        justify-content: center !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div {
        width: 33% !important;
        min-width: 33% !important;
    }

    /* റൗണ്ട് ഗോൾഡൻ ബട്ടണുകൾ */
    .stSidebar .stButton > button {
        background-color: #1a1a1a !important;
        color: #FFD700 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 50% !important;
        height: 75px !important;
        width: 75px !important;
        margin: 5px auto !important;
        display: flex !important;
        align-items: center;
        justify-content: center;
        font-size: 22px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    
    /* ബട്ടണിന് താഴെയുള്ള പേര് */
    .side-label {
        text-align: center;
        font-size: 10px;
        color: #FFD700;
        font-weight: bold;
        margin-bottom: 15px;
        text-transform: uppercase;
    }

    /* നിന്റെ പഴയ ബോക്സ് സ്റ്റൈലുകൾ */
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .ai-box { background: rgba(0,0,0,0.85); color: #FFD700; padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 20px; font-weight: bold; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN SECTION (നിന്റെ കോഡിൽ ഉള്ളത് പോലെ) ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u.capitalize()
                add_log(f"Login success: {u}")
                st.rerun()
            else:
                st.error("Access Denied!")
                add_log(f"Failed login attempt: {u}")
else:
    # --- DATA LOADING ---
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: 
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()

    # --- 📱 SIDEBAR 3x3 GRID MENU (പുതിയ ഡിസൈൻ) ---
    with st.sidebar:
        st.markdown(f"<h3 style='text-align: center; color: #FFD700;'>👤 {st.session_state.user}</h3>", unsafe_allow_html=True)
        st.write("---")
        
        # Row 1 (Home, Add, Debt)
        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.button("🏠", key="btn_home", on_click=nav_to, args=("🏠 Home Dashboard",))
        r1c1.markdown("<p class='side-label'>Home</p>", unsafe_allow_html=True)
        
        r1c2.button("💰", key="btn_add", on_click=nav_to, args=("💰 Add Entry",))
        r1c2.markdown("<p class='side-label'>Add</p>", unsafe_allow_html=True)
        
        r1c3.button("🤝", key="btn_debt", on_click=nav_to, args=("🤝 Debt Tracker",))
        r1c3.markdown("<p class='side-label'>Debt</p>", unsafe_allow_html=True)

        # Row 2 (Sheet, Report, Sync)
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.button("📄", key="btn_sheet", on_click=nav_to, args=("📄 View Sheet Copy",))
        r2c1.markdown("<p class='side-label'>Sheet</p>", unsafe_allow_html=True)
        
        r2c2.button("📊", key="btn_report", on_click=nav_to, args=("📊 Expense Report",))
        r2c2.markdown("<p class='side-label'>Report</p>", unsafe_allow_html=True)
        
        # Sync બટન - st.rerun വാണിംഗ് ഒഴിവാക്കാൻ പ്രത്യേക ഫങ്ക്ഷൻ ഉപയോഗിക്കുന്നു
        r2c3.button("🔄", key="btn_sync", on_click=sync_data)
        r2c3.markdown("<p class='side-label'>Sync</p>", unsafe_allow_html=True)

        st.write("---")
        # ലോഗ് ഔട്ട് ബട്ടൺ താഴെ നൽകുന്നു
        if st.button("🚪 LOGOUT", key="btn_logout"):
            st.session_state.auth = False
            st.rerun()

    # --- MAIN PAGES LOGIC ---
    # സൈഡ്‌ബാറിൽ സെലക്ട് ചെയ്ത പേജ് ഇവിടെ കാണിക്കുന്നു
    current_page = st.session_state.page

    if current_page == "🏠 Home Dashboard":
        st.title(f"Welcome, {st.session_state.user}!")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            bal = inc - deb
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            st.subheader("🤖 AI Advisor Insights")
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            ratio = (deb / inc * 100) if inc > 0 else 0
            if ratio > 80: st.write("⚠️ ചിലവ് കൂടുതലാണ്, നിയന്ത്രിക്കുക.")
            elif ratio < 40 and inc > 0: st.write("✅ മികച്ച സമ്പാദ്യശീലം!")
            else: st.write("📊 ഫിനാൻഷ്യൽ സ്റ്റാറ്റസ് നോർമൽ ആണ്.")
            st.markdown('</div>', unsafe_allow_html=True)

    elif current_page == "💰 Add Entry":
        st.title("New Expense/Income")
        # വോയിസ് ഇൻപുട്ട് (ലഭ്യമാണെങ്കിൽ മാത്രം)
        v = ""
        if speech_to_text:
            v = speech_to_text(language='ml', key='voice_input')
            
        with st.form("main_entry", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            am = st.number_input("Amount (തുക)", value=None, placeholder="Amount നൽകുക...")
            ty = st.radio("Type", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("Saved! ✅")
                    st.cache_data.clear()

    # നീ നൽകിയ കോഡിൽ Debt Tracker, Sheet, Report എന്നിവയ്ക്ക് ഡിസൈൻ ഇല്ലായിരുന്നു. 
    # അത് കൊണ്ട് ഡിഫോൾട്ട് ആയി ഈ വരി കാണിക്കും.
    else:
        st.title(current_page)
        st.info("ഈ സെക്ഷൻ റെഡിയാണ്. (ഇവിടെ ലിസ്റ്റ്/റിപ്പോർട്ട് ചേർക്കാം)")
