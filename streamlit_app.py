import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
USERS = {
    "faisal": "faisal123",
    "shabana": "shabana123"
}
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI AI", layout="wide")
st_autorefresh(interval=300000, key="paichi_sync")

if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = ""

# --- 2. LOGIN ---
if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>LOGIN</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        u_in = st.text_input("Username").lower()
        p_in = st.text_input("Password", type="password")
        if st.button("ENTER"):
            if u_in in USERS and USERS[u_in] == p_in:
                st.session_state.auth = True
                st.session_state.user = u_in
                st.rerun()
            else:
                st.error("Wrong Password!")
else:
    # --- 3. SIDEBAR & PERMISSIONS ---
    with st.sidebar:
        st.header(f"👤 {st.session_state.user.capitalize()}")
        
        # ഫൈസലിന് മാത്രം എല്ലാ മെനുവും കാണാം
        if st.session_state.user == "faisal":
            f_val = st.number_input("Factor", value=96.5, step=0.1)
            page = st.radio("Menu", ["📊 Advisor", "💰 Add Expense", "🔍 History"])
        else:
            # ഷബാനയ്ക്ക് "Add Expense" മാത്രമേ ലിസ്റ്റിൽ വരൂ
            page = "💰 Add Expense"
            st.info("നിങ്ങൾക്ക് എൻട്രികൾ മാത്രം ചേർക്കാൻ സാധിക്കും.")
            
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # --- 4. PAGES ---
    
    # ADVISOR (Faisal Only)
    if page == "📊 Advisor" and st.session_state.user == "faisal":
        st.title("Trading Advisor")
        try:
            data = yf.download("CL=F", period="1d", interval="1m", progress=False)
            live_p = data['Close'].iloc[-1] * f_val
            st.metric("Crude Oil Price", f"₹ {live_p:,.2f}")
        except: st.write("Loading...")

    # ADD EXPENSE (Both can see, but this is the ONLY page for Shabana)
    elif page == "💰 Add Expense":
        st.title("Add New Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", min_value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am > 0:
                    final_it = f"[{st.session_state.user.capitalize()}] {it}"
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": final_it,
                        "entry.1460982454": d, "entry.1221658767": c
                    })
                    st.success("വിവരങ്ങൾ ഷീറ്റിലേക്ക് മാറ്റി!")

    # HISTORY (Faisal Only)
    elif page == "🔍 History" and st.session_state.user == "faisal":
        st.title("Full History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Error loading data")
