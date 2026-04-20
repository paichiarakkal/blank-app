import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI v17.0", layout="wide")
st_autorefresh(interval=30000, key="refresh")

# --- 2. THEME ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #2D0844, #1A0521); color: #fff; }
    .purple-box { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid gold; text-align: center; margin-bottom: 10px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { background: gold; color: black; border-radius: 8px; font-weight: bold; width: 100%; }
</style>""", unsafe_allow_html=True)

# --- 3. FUNCTIONS ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={datetime.now().second}")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        for col in ['Credit', 'Debit']: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

def get_signals():
    results = []
    for name, sym in {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}.items():
        try:
            df = yf.Ticker(sym).history(period="2d", interval="5m")
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            # ATR Logic for Supertrend-like signal
            atr = (df['High'] - df['Low']).rolling(window=10).mean().iloc[-1]
            lower_band = ((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr)
            st_buy = last_p > lower_band

            if last_p > pivot and rsi > 55 and st_buy: sig, col = "🚀 BUY", "#00FF00"
            elif last_p < pivot and rsi < 45 and not st_buy: sig, col = "📉 SELL", "#FF3131"
            else: sig, col = "⚖️ WAIT", "gold"
            
            if name == "Crude Fut": last_p *= 83.5
            results.append({"name": name, "price": last_p, "sig": sig, "col": col, "rsi": rsi})
        except: continue
    return results

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("GO"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    user = st.session_state.user
    # Advisor പേജ് ഇവിടെ മെനുവിൽ ആഡ് ചെയ്തു
    page = "💰 Add Entry" if user == "shabana" else st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])
    df = get_data()

    if page == "📊 Advisor":
        st.title("Market Advisor")
        signals = get_signals()
        for m in signals:
            st.markdown(f'<div class="purple-box" style="border-color:{m["col"]}"><h2>{m["name"]}</h2><h1 style="color:{m["col"]}">{m["sig"]}</h1><h3>₹{m["price"]:,.0f}</h3><p>RSI: {m["rsi"]:.1f}</p></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        if df is not None:
            fig = px.line(df.groupby('Date')[['Credit','Debit']].sum().assign(Net=lambda x: x.Credit-x.Debit).reset_index(), x='Date', y='Net', title="P&L Trend")
            st.plotly_chart(fig, use_container_width=True)
            df['Cat'] = df['Item'].str.extract(r'\[(.*?)\]').fillna("Other")
            st.plotly_chart(px.pie(df[df.Debit>0].groupby('Cat')['Debit'].sum().reset_index(), values='Debit', names='Cat', hole=.4), use_container_width=True)

    elif page == "💰 Add Entry":
        bal = (df['Credit'].sum() - df['Debit'].sum()) if df is not None else 0
        st.markdown(f'<div class="purple-box"><h3>Balance: ₹{bal:,.0f}</h3></div>', unsafe_allow_html=True)
        v = speech_to_text(language='ml', key='v')
        with st.form("entry_form"):
            it, am = st.text_input("Item", v if v else ""), st.number_input("Amount", min_value=1, value=None)
            cat = st.selectbox("Category", ["Food", "Trading", "Rent", "Salary", "Other"])
            if st.form_submit_button("SAVE"):
                if it and am:
                    # Food, Rent, Other, Trading Loss എന്നിവയെല്ലാം Debit
                    ty = "Credit" if cat in ["Salary"] else "Debit"
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%d/%m/%Y"),
                        "entry.2013476337": f"[{cat}] {it}",
                        "entry.1460982454": am if ty=="Debit" else 0,
                        "entry.1221658767": am if ty=="Credit" else 0
                    })
                    st.success(f"{cat} Entry Saved! ✅"); st.rerun()

    elif page == "🔍 History": st.dataframe(df.iloc[::-1], use_container_width=True)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
