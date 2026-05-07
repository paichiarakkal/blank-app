import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import urllib.parse
import threading

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123"}

st.set_page_config(page_title="PAICHI GOLD v8.1", layout="wide")
# ഓരോ മിനിറ്റിലും ആപ്പ് തനിയെ റിഫ്രഷ് ആകും (റിമൈൻഡർ ചെക്ക് ചെയ്യാൻ ഇത് സഹായിക്കും)
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 2. FUNCTIONS ---
def send_whatsapp(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=5)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

# --- 3. LOGIN & UI ---
if not st.session_state.auth:
    st.title("🔐 Login")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    df = get_data()
    menu = ["💰 Add Entry", "📊 Report", "🔍 History"]
    if st.session_state.user == "faisal": menu.insert(0, "📊 Advisor")
    
    page = st.sidebar.radio("Menu", menu)

    if page == "📊 Report":
        st.title("Monthly Expense Analysis")
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Month'] = df['Date'].dt.strftime('%B %Y')
            month = st.selectbox("Select Month", df['Month'].unique())
            
            m_df = df[df['Month'] == month].copy()
            m_df['Debit'] = pd.to_numeric(m_df['Debit'], errors='coerce').fillna(0)
            
            # ചാർട്ട് ശരിയാക്കാൻ കാറ്റഗറി തിരിക്കുന്നു
            m_df['Category'] = m_df['Item'].apply(lambda x: x.split(':')[0] if ':' in x else 'Others')
            
            fig = px.pie(m_df[m_df['Debit'] > 0], values='Debit', names='Category', hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Total Expense", f"₹{m_df['Debit'].sum():,.2f}")

    elif page == "🔍 History":
        st.title("Transaction History")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    # --- 4. SIMPLE REMINDER LOGIC (Faisal Only) ---
    if st.session_state.user == "faisal":
        st.sidebar.markdown("---")
        st.sidebar.subheader("Private Reminder")
        rem_msg = st.sidebar.text_input("What to remind?")
        rem_time = st.sidebar.time_input("When?")
        if st.sidebar.button("Set Reminder"):
            st.sidebar.success(f"Set for {rem_time}")
            # ഇവിടെ ശരിക്കും ബാക്ക്ഗ്രൗണ്ടിൽ ചെക്ക് ചെയ്യണമെങ്കിൽ ഡാറ്റാബേസ് വേണം.
            # തൽക്കാലം സെറ്റ് ചെയ്ത ഉടനെ ഒരു ടെസ്റ്റ് മെസേജ് അയക്കാം:
            # send_whatsapp(f"Reminder Set: {rem_msg}")
