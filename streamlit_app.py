import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. ലോഗിൻ വിവരങ്ങൾ
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"}
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Finance", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 🎨 ചിഹ്നങ്ങൾ ഒഴിവാക്കാനുള്ള അന്തിമ CSS ---
st.markdown("""
    <style>
    /* 1. മുകളിലെ Fork, GitHub ബാർ പൂർണ്ണമായും ഹൈഡ് ചെയ്യുന്നു */
    header, [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 2. താഴെയുള്ള റെഡ് ക്രൗൺ ചിഹ്നം ഒഴിവാക്കുന്നു */
    footer {display: none !important;}
    .viewerBadge_container__1QS1n {display: none !important;}
    
    /* 3. സൈഡ് ബാർ ഹൈഡ് ചെയ്യുന്നു (നമ്മൾ മെയിൻ പേജിൽ മെനു വെക്കും) */
    [data-testid="stSidebar"] {display: none !important;}

    /* പേജ് ഡിസൈൻ */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); 
        padding-top: 20px;
    }
    
    .balance-box { 
        background: #000; color: #00FF00; padding: 20px; 
        border-radius: 15px; text-align: center; font-size: 24px; 
        font-weight: bold; border: 3px solid #FFD700; 
    }
    
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u_raw = st.text_input("Username")
    p_raw = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        u_clean = u_raw.lower().strip()
        if u_clean in USERS and USERS[u_clean]["pw"] == p_raw:
            st.session_state.auth, st.session_state.user, st.session_state.role = True, u_clean.capitalize(), USERS[u_clean]["role"]
            st.rerun()
        else: st.error("Access Denied!")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
            df.columns = df.columns.str.strip()
            return df
        except: return None

    df = load_data()
    
    # NAVIGATION
    col1, col2 = st.columns([3, 1])
    col1.subheader(f"👤 {st.session_state.user}")
    if col2.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    menu = ["💰 Add Entry"]
    if st.session_state.role == "admin":
        menu = ["🏠 Dashboard", "💰 Add Entry", "🔍 Search"]
    
    page = st.radio("Go to:", menu, horizontal=True)
    st.markdown("---")

    if page == "🏠 Dashboard":
        if df is not None:
            # ടോട്ടൽ ബാലൻസ് കാണിക്കുന്നു
            bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
            st.markdown(f'<div class="balance-box">Total Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            st.write("Recent Entries:")
            st.dataframe(df.iloc[::-1].head(10), use_container_width=True)

    elif page == "💰 Add Entry":
        st.title("Add Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("my_form", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    # ഡാറ്റ ഗൂഗിൾ ഷീറ്റിലേക്ക് അയക്കുന്നു
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{st.session_state.user}] {it}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    })
                    st.success("Saved! ✅")
                    st.cache_data.clear()
