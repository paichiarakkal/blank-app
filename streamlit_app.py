import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
# ഷബാനയുടെ ലോഗിൻ മാത്രം നിലനിർത്തുന്നു
SHABANA_PW = "shabana123" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI AI", layout="wide")
st_autorefresh(interval=300000, key="paichi_5min_sync")

# --- 2. 🤖 ADVISOR ENGINE ---
def get_original_analysis(multiplier):
    try:
        ticker = "CL=F"
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if data.empty: return None
        live_price = data['Close'].iloc[-1] * multiplier
        last_p = data['Close'].iloc[-1]
        prev_p = data['Close'].iloc[-2]
        advice, color = ("UPWARD TREND 📈", "#00FF00") if last_p > prev_p else ("DOWNWARD TREND 📉", "#FF0000")
        return {"price": live_price, "advice": advice, "color": color}
    except: return None

# --- 3. UI & ACCESS CONTROL ---
# ഫൈസലിന് നേരിട്ട് കയറാം, ഷബാനയ്ക്ക് ലോഗിൻ ചെയ്യാം
if 'is_shabana' not in st.session_state: st.session_state.is_shabana = False

with st.sidebar:
    st.header("👤 Dashboard")
    # ഷബാനയ്ക്ക് ലോഗിൻ ചെയ്യാനുള്ള ഭാഗം
    if not st.session_state.is_shabana:
        if st.checkbox("Shabana Login"):
            pw = st.text_input("Password", type="password")
            if pw == SHABANA_PW:
                st.session_state.is_shabana = True
                st.rerun()
    else:
        st.success("Welcome Shabana")
        if st.button("Logout"):
            st.session_state.is_shabana = False
            st.rerun()

    f_val = st.number_input("Factor", value=96.5, step=0.1)
    page = st.radio("Menu", ["📊 Advisor", "💰 Expense", "🔍 History"])

# --- PAGES ---
if page == "📊 Advisor":
    res = get_original_analysis(f_val)
    if res:
        st.markdown(f"""
        <div style="background: #111; padding: 30px; border-radius: 15px; border: 2px solid {res['color']}; text-align: center;">
            <h2 style="color: {res['color']};">{res['advice']}</h2>
            <h1 style="font-size: 75px; color: #FFD700;">₹ {res['price']:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Data Loading... അല്പം കാത്തിരിക്കൂ.")

elif page == "💰 Expense":
    st.title("Add Expense")
    v = speech_to_text(language='ml', key='ml_voice_free')
    with st.form("expense_form"):
        it = st.text_input("Item", value=v if v else "")
        am = st.number_input("Amount", value=0)
        ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        if st.form_submit_button("SUBMIT"):
            d, c = (am, 0) if ty == "Debit" else (0, am)
            requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": it, "entry.1460982454": d, "entry.1221658767": c})
            st.success("Saved!")

elif page == "🔍 History":
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1], use_container_width=True)
    except: pass
