import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime
import streamlit_autorefresh as st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI", layout="wide")
st_autorefresh.st_autorefresh(interval=30000, key="refresh")

# --- 2. LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("User").lower()
    p = st.text_input("Pass", type="password")
    if st.button("GO"):
        if USERS.get(u) == p:
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
else:
    # --- 3. DATA ---
    def get_data():
        try:
            df = pd.read_csv(CSV_URL)
            df.columns = df.columns.str.strip()
            return df
        except: return None

    df = get_data()
    menu = st.sidebar.radio("Menu", ["📊 Advisor", "💰 Add Entry", "🔍 History"])

    # --- 4. ADVISOR ---
    if menu == "📊 Advisor":
        st.title("Market Advisor")
        for name, sym in {"Nifty": "^NSEI", "BankNifty": "^NSEBANK", "Crude": "CL=F"}.items():
            try:
                data = yf.Ticker(sym).history(period="1d")
                price = data['Close'].iloc[-1]
                if name == "Crude": price *= 83.5
                st.metric(name, f"₹{price:,.2f}")
            except: st.write(f"{name} Error")

    # --- 5. ADD ENTRY (Category ഒഴിവാക്കി) ---
    elif menu == "💰 Add Entry":
        st.title("New Entry")
        with st.form("f"):
            it = st.text_input("Item / Description")
            am = st.number_input("Amount", min_value=1)
            ty = st.radio("Type", ["Debit (ചിലവ്)", "Credit (വരവ്)"])
            if st.form_submit_button("SAVE"):
                db = am if "Debit" in ty else 0
                cr = am if "Credit" in ty else 0
                requests.post(FORM_API, data={
                    "entry.1044099436": datetime.now().strftime("%d/%m/%Y"),
                    "entry.2013476337": it,
                    "entry.1460982454": db,
                    "entry.1221658767": cr
                })
                st.success("Saved! ✅")
                st.rerun()

    # --- 6. HISTORY ---
    elif menu == "🔍 History":
        st.title("History")
        if df is not None:
            st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
