import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
# നിന്റെ യൂസർലോഗിൻ വിവരങ്ങൾ
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI ORIGINAL", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. STYLE ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #1A0521); color: #fff; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 15px; border: 1px solid gold;
        text-align: center; margin-bottom: 15px;
    }
    h1, h2, h3, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. LOGIN ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("തെറ്റായ പാസ്‌വേഡ്!")

else:
    # --- 4. DATA ENGINE ---
    def get_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            return df
        except:
            return None

    df = get_data()
    menu = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    # --- 5. PAGES ---
    if menu == "📊 Advisor":
        st.title("🚀 Market Advisor")
        symbols = {"Nifty": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Oil": "CL=F"}
        for name, sym in symbols.items():
            try:
                data = yf.Ticker(sym).history(period="2d", interval="5m")
                price = data['Close'].iloc[-1]
                if name == "Crude Oil": price *= 83.5
                st.markdown(f'<div class="purple-box"><h2>{name}</h2><h1>₹{price:,.2f}</h1></div>', unsafe_allow_html=True)
            except:
                st.write(f"{name} ഡാറ്റ ലഭ്യമല്ല")

    elif menu == "🏠 Dashboard":
        st.title("📈 Performance")
        if df is not None:
            df['Net'] = df['Credit'] - df['Debit']
            daily = df.groupby('Date')['Net'].sum().reset_index()
            st.plotly_chart(px.line(daily, x='Date', y='Net', title="Daily Profit/Loss"), use_container_width=True)

    elif menu == "💰 Add Entry":
        st.title("Add Transaction")
        v = speech_to_text(language='ml', key='voice')
        with st.form("my_form"):
            item = st.text_input("Details", value=v if v else "")
            amount = st.number_input("Amount", min_value=1)
            cat = st.selectbox("Category", ["Food", "Trading", "Rent", "Salary", "Other"])
            if st.form_submit_button("SAVE"):
                cr = amount if cat == "Salary" else 0
                db = amount if cat != "Salary" else 0
                requests.post(FORM_API, data={
                    "entry.1044099436": datetime.now().strftime("%d/%m/%Y"),
                    "entry.2013476337": f"[{cat}] {item}",
                    "entry.1460982454": db,
                    "entry.1221658767": cr
                })
                st.success("സേവ് ചെയ്തു! ✅")
                st.rerun()

    elif menu == "🔍 History":
        st.title("Transaction History")
        if df is not None:
            st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
