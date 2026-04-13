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

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം & സ്ലൈഡ് ആനിമേഷൻ
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); 
        color: #000; 
    }
    
    /* സൈഡ്ബാർ സ്റ്റൈലിംഗ് */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.95) !important;
    }
    
    /* സൈഡ്ബാർ മെനു ബട്ടണുകൾ സ്ലൈഡ് ആനിമേഷൻ */
    div[data-testid="stSidebarNav"] li {
        animation: slideIn 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
        opacity: 0;
        margin-bottom: 15px;
        border-left: 0px solid #FFD700;
        transition: 0.3s;
    }
    
    div[data-testid="stSidebarNav"] li:hover {
        border-left: 10px solid #FFD700;
        padding-left: 10px;
    }

    @keyframes slideIn {
        from { transform: translateX(-100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* ഓരോ ബട്ടണിനും ഡിലേ നൽകുന്നു */
    div[data-testid="stSidebarNav"] li:nth-child(1) { animation-delay: 0.1s; }
    div[data-testid="stSidebarNav"] li:nth-child(2) { animation-delay: 0.2s; }
    div[data-testid="stSidebarNav"] li:nth-child(3) { animation-delay: 0.3s; }
    div[data-testid="stSidebarNav"] li:nth-child(4) { animation-delay: 0.4s; }
    div[data-testid="stSidebarNav"] li:nth-child(5) { animation-delay: 0.5s; }

    /* UI എലമെന്റുകൾ */
    .balance-box { 
        background: #000; color: #00FF00; padding: 25px; 
        border-radius: 15px; text-align: center; font-size: 30px; 
        font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.3);
    }
    
    .ai-box { 
        background: rgba(0,0,0,0.85); color: #FFD700; padding: 20px; 
        border-radius: 15px; border-left: 8px solid #FFD700; 
        margin-bottom: 20px; font-weight: bold; 
    }
    
    .log-container { 
        background: #111; padding: 10px; border-radius: 5px; 
        height: 200px; overflow-y:auto; font-family:monospace; 
        font-size: 12px; color: #00FF00; border: 1px solid #333;
    }
    
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    
    /* സൈഡ്ബാറിലെ അക്ഷരങ്ങൾ വെളുത്ത നിറത്തിലാക്കാൻ */
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN SECTION ---
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
    st.sidebar.title(f"👤 {st.session_state.user}")
    page = st.sidebar.radio("Menu", ["🏠 Home Dashboard", "💰 Add Entry", "🤝 Debt Tracker", "📄 View Sheet Copy", "📊 Expense Report"])
    
    if st.sidebar.button("🚪 Log Out"): 
        st.session_state.auth = False
        st.rerun()

    # --- 🏠 HOME DASHBOARD ---
    if page == "🏠 Home Dashboard":
        st.title(f"Welcome, {st.session_state.user}!")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            bal = inc - deb
            st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            st.subheader("🤖 AI Advisor Insights")
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            ratio = (deb / inc * 100) if inc > 0 else 0
            if ratio > 80:
                st.write("⚠️ ഫൈസൽ, ഈ മാസത്തെ ചിലവ് വളരെ കൂടുതലാണ്. അത്യാവശ്യമല്ലാത്ത കാര്യങ്ങൾക്കായി പണം ചിലവാക്കുന്നത് നിയന്ത്രിക്കുക.")
            elif ratio < 40 and inc > 0:
                st.write("✅ മികച്ച സമ്പാദ്യശീലം! പണം ശരിയായ രീതിയിൽ കൈകാര്യം ചെയ്യാൻ നിങ്ങൾക്ക് സാധിക്കുന്നുണ്ട്.")
            else:
                st.write("📊 നിങ്ങളുടെ ഫിനാൻഷ്യൽ സ്റ്റാറ്റസ് ഇപ്പോൾ നോർമൽ ആണ്. ഇതേപോലെ തുടരുക.")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- 💰 ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("New Expense/Income")
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
                    add_log(f"Added Entry: {it} (₹{am})")
                    st.success("വിജയകരമായി സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()
 
    # --- 🤝 DEBT TRACKER ---
    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("debt_f", clear_on_submit=True):
            n = st.text_input("ആളുടെ പേര്")
            a = st.number_input("തുക", value=None)
            t = st.selectbox("വിഭാഗം", ["Borrowed (വാങ്ങി)", "Lent (കൊടുത്തു)"])
            if st.form_submit_button("SAVE DEBT"):
                if n and a:
                    add_log(f"Debt Recorded: {n} ({a})")
                    st.success("കടം വിവരങ്ങൾ രേഖപ്പെടുത്തി! ✅")

    # --- 📄 VIEW SHEET COPY ---
    elif page == "📄 View Sheet Copy":
        st.title("Google Sheet Records")
        if df is not None:
            st.write("ഷീറ്റിലെ അവസാന എൻട്രികൾ:")
            st.dataframe(df.tail(20), use_container_width=True)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
            st.download_button("📥 Download Full Excel", buf.getvalue(), "Finance_History.xlsx")

    # --- 📊 EXPENSE REPORT ---
    elif page == "📊 Expense Report":
        st.title("Analysis Chart")
        if df is not None:
            sdf = df.groupby('Item')[['Debit','Amount']].sum().sum(axis=1).reset_index(name='T')
            fig = px.pie(sdf[sdf['T']>0], values='T', names='Item', hole=0.4, color_discrete_sequence=px.colors.sequential.Sunset)
            st.plotly_chart(fig, use_container_width=True)

    # --- 📜 LOGS (SideBar) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Activity Logs")
    st.sidebar.markdown(f'<div class="log-container">{"<br>".join(st.session_state.app_logs)}</div>', unsafe_allow_html=True)
