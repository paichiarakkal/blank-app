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
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI ORIGINAL CODE", layout="wide")
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
    h1, h2, h3, p { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
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

    # --- 5. ADVISOR ENGINE ---
    def get_advisor_signals():
        try:
            symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Oil": "CL=F"}
            results = []
            for name, sym in symbols.items():
                data = yf.Ticker(sym).history(period="5d", interval="5m")
                if data.empty: continue
                last_p = data['Close'].iloc[-1]
                
                # Pivot Point
                h, l, c = data['High'].iloc[-2], data['Low'].iloc[-2], data['Close'].iloc[-2]
                pivot = (h + l + c) / 3
                
                # RSI
                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = -delta.where(delta < 0, 0).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                
                # Signal
                if last_p > pivot and rsi > 55: sig, col = "🚀 BUY", "#00FF00"
                elif last_p < pivot and rsi < 45: sig, col = "📉 SELL", "#FF3131"
                else: sig, col = "⚖️ WAIT", "#FFFF00"
                
                if name == "Crude Oil": last_p *= 83.5
                results.append({"name": name, "price": last_p, "sig": sig, "col": col, "rsi": rsi})
            return results
        except:
            return None

    df = get_data()
    menu = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    # --- 6. PAGES ---
    if menu == "📊 Advisor":
        st.title("🚀 Smart Advisor")
        signals = get_advisor_signals()
        if signals:
            for s in signals:
                st.markdown(f'''<div class="purple-box" style="border-color:{s['col']};">
                    <h2>{s['name']}</h2>
                    <h1 style="color:{s['col']} !important; font-size:50px;">{s['sig']}</h1>
                    <h2 style="color:gold !important;">₹{s['price']:,.2f}</h2>
                    <p>RSI: {s['rsi']:.1f}</p></div>''', unsafe_allow_html=True)

    elif menu == "🏠 Dashboard":
        st.title("📈 Performance")
        if df is not None:
            df['Net'] = df['Credit'] - df['Debit']
            daily = df.dropna(subset=['Date']).groupby('Date')['Net'].sum().reset_index()
            fig = px.line(daily, x='Date', y='Net', markers=True)
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)

    elif menu == "💰 Add Entry":
        st.title("Add Transaction")
        voice_val = speech_to_text(language='ml', key='voice')
        with st.form("my_form"):
            item = st.text_input("Details", value=voice_val if voice_val else "")
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
