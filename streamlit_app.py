import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import io

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal123", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD & SILVER v3.1", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN (Silver & Gold Mix) ---
st.markdown("""
    <style>
    /* മെയിൻ ബോഡി - GOLDEN GRADIENT */
    .stApp {
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        color: #000;
    }
    /* സൈഡ് ബാർ - SILVER GRADIENT */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #BDBDBD, #E0E0E0, #757575) !important;
    }
    /* ബട്ടണുകൾ */
    .stButton>button {
        background-color: #000;
        color: #FFD700;
        border-radius: 10px;
        border: 1px solid #FFD700;
    }
    /* ബോക്സുകൾ */
    .metric-box {
        background: rgba(0,0,0,0.8);
        color: #FFD700;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FFD700;
        text-align: center;
    }
    h1, h2, h3, p { color: #000 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 TRIPLE INDICATOR ENGINE ---
def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            atr = (df['High'] - df['Low']).rolling(window=10).mean().iloc[-1]
            lower_band = ((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr)
            st_buy = last_p > lower_band
            if last_p > pivot and rsi > 55 and st_buy: signal, color = "🚀 BUY", "#00FF00"
            elif last_p < pivot and rsi < 45 and not st_buy: signal, color = "📉 SELL", "#FF0000"
            else: signal, color = "⚖️ WAIT", "#FFFF00"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": rsi, "color": color})
        return results
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    st.sidebar.title(f"👤 {curr_user.capitalize()}")
    
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor" and curr_user != "shabana":
        st.title("🚀 Triple Signal Terminal")
        markets = get_triple_advisor()
        if markets:
            cols = st.columns(len(markets))
            for i, m in enumerate(markets):
                with cols[i]:
                    st.markdown(f'<div class="metric-box"><h3>{m["name"]}</h3><h2 style="color:{m["color"]}">{m["signal"]}</h2><h1 style="color:#FFD700">₹{m["price"]:,.0f}</h1><p>RSI: {m["rsi"]:.1f}</p></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Financial Status")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        total_in = pd.to_numeric(df['Credit'], errors='coerce').sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').sum()
        st.markdown(f'<div class="metric-box" style="font-size:40px">Balance: ₹{total_in - total_out:,.2f}</div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Add Transaction")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved! ✅")

    elif page == "📊 Report" and curr_user != "shabana":
        st.title("Expense Analysis")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        # ക്ലീനിംഗ്
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        report_df = df[df['Debit'] > 0].groupby('Item')['Debit'].sum().reset_index()
        if not report_df.empty:
            fig = px.pie(report_df, values='Debit', names='Item', title="ചിലവുകളുടെ വിഭജനം", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        else: st.write("ഡാറ്റ ലഭ്യമല്ല.")

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("History")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1], use_container_width=True)
