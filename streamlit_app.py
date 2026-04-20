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

st.set_page_config(page_title="PAICHI v20.0", layout="wide")
st_autorefresh(interval=30000, key="refresh")

# --- 2. THEME ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1A0521, #4B0082); color: #fff; }
    .purple-box { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 12px; border: 1px solid gold; margin-bottom: 10px; }
    h1, h2, h3 { color: #FFD700 !important; }
</style>""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
def load_data():
    try:
        # Cache ഒഴിവാക്കാൻ റാൻഡം നമ്പർ ചേർക്കുന്നു
        df = pd.read_csv(f"{CSV_URL}&r={datetime.now().microsecond}")
        df.columns = df.columns.str.strip()
        
        # തീയതി ശരിയാക്കുന്നു
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        
        # Credit/Debit നമ്പറുകളാക്കുന്നു
        for c in ['Credit', 'Debit', 'Amount']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_market():
    out = []
    for n, s in {"Nifty": "^NSEI", "BankNifty": "^NSEBANK", "Crude": "CL=F"}.items():
        try:
            d = yf.Ticker(s).history(period="2d", interval="5m")
            lp = d['Close'].iloc[-1]
            # Simple RSI/Pivot logic
            rsi = 50 # Default
            sig, col = "⚖️ WAIT", "gold"
            if lp > d['Close'].mean(): sig, col = "🚀 BUY", "#00FF00"
            if n == "Crude": lp *= 83.5
            out.append({"n": n, "p": lp, "s": sig, "c": col})
        except: continue
    return out

# --- 4. APP ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])
    df = load_data()

    if page == "📊 Advisor":
        for m in get_market():
            st.markdown(f'<div class="purple-box" style="border-color:{m["c"]}"><h3>{m["n"]}</h3><h1 style="color:{m["c"]}">{m["s"]}</h1><h2>₹{m["p"]:,.0f}</h2></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        if df is not None:
            st.subheader("Profit & Loss Graph")
            df['Net'] = df['Credit'] - df['Debit']
            daily = df.groupby('Date')['Net'].sum().reset_index()
            st.plotly_chart(px.line(daily, x='Date', y='Net', markers=True), use_container_width=True)
            
            st.subheader("Expense by Category")
            df['Category'] = df['Item'].str.extract(r'\[(.*?)\]').fillna("Other")
            expenses = df[df['Debit'] > 0].groupby('Category')['Debit'].sum().reset_index()
            st.plotly_chart(px.pie(expenses, values='Debit', names='Category', hole=.3), use_container_width=True)

    elif page == "💰 Add Entry":
        bal = (df['Credit'].sum() - df['Debit'].sum()) if df is not None else 0
        st.markdown(f'<div class="purple-box"><h2>Balance: ₹{bal:,.0f}</h2></div>', unsafe_allow_html=True)
        v = speech_to_text(language='ml', key='v')
        with st.form("entry"):
            it = st.text_input("Item", v if v else "")
            am = st.number_input("Amount", min_value=1)
            cat = st.selectbox("Category", ["Food", "Rent", "Trading", "Salary", "Other"])
            if st.form_submit_button("SAVE"):
                cr = am if cat == "Salary" else 0
                db = am if cat != "Salary" else 0
                requests.post(FORM_API, data={
                    "entry.1044099436": datetime.now().strftime("%d/%m/%Y"),
                    "entry.2013476337": f"[{cat}] {it}",
                    "entry.1460982454": db,
                    "entry.1221658767": cr
                })
                st.success("Saved!"); st.rerun()

    elif page == "🔍 History":
        if df is not None: st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)
    
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
