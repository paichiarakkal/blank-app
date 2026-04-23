import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import time
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG (നിങ്ങളുടെ ലിങ്കുകൾ) ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI FINANCE", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. ലളിതമായ ബാലൻസ് ചെക്കിംഗ് ---
def get_bal():
    try:
        # cache ഒഴിവാക്കാൻ random നമ്പർ ചേർക്കുന്നു
        u = f"{CSV_URL}&r={random.randint(1,999999)}"
        df = pd.read_csv(u)
        df.columns = df.columns.str.strip()
        return pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum() - pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
    except: return 0.0

# --- 3. വാട്സാപ്പ് എൻജിൻ ---
def send_wa(item, amount, balance):
    api_key = "7463030" 
    phone = "971551347989"
    msg = f"📝 Item: {item}\n💰 Amount: {amount}\n💳 Balance: ₹{balance:,.2f}"
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(msg)}&apikey={api_key}"
    try: requests.get(url, timeout=10)
    except: pass

# --- 4. ഡിസൈൻ ---
st.markdown("<style>.stApp { background: #2D0844; color: white; }</style>", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("User").lower()
    p = st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "🔍 History"])
    
    if page == "🏠 Dashboard":
        b = get_bal()
        st.header(f"Balance: ₹{b:,.2f}")

    elif page == "💰 Add Entry":
        st.title("Add Entry")
        v = speech_to_text(language='ml', key='v1')
        with st.form("f1", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": it, "entry.1460982454": d, "entry.1221658767": c})
                    
                    # ബാലൻസ് മാറാൻ വേണ്ടി 3 സെക്കൻഡ് വെയ്റ്റ് ചെയ്യുന്നു
                    with st.spinner('Wait...'):
                        time.sleep(3)
                    
                    new_b = get_bal()
                    send_wa(it, am, new_b)
                    st.success(f"Saved! New Bal: {new_b}")
                    st.rerun()

    elif page == "🔍 History":
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,99)}")
            st.dataframe(df.iloc[::-1])
        except: st.error("Error")
