import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import os
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# 1. ലോഗിൻ & ലിങ്കുകൾ
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"},
    "admin": {"pw": "paichi786", "role": "admin"}
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
TRADE_FILE = 'trade_journal.csv'

st.set_page_config(page_title="PAICHI All-in-One Finance", layout="wide")

# --- 🎨 AI & Golden Theme Design ---
st.markdown("""
<style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); 
        color: #000; 
    }

    /* സൈഡ് ബാർ AI Dark Style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e293b) !important;
        border-right: 2px solid #FFD700;
    }
    
    /* സൈഡ് ബാർ ടെക്സ്റ്റ് വൈറ്റ് ആക്കാൻ */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h3 {
        color: #e2e8f0 !important;
    }

    /* ബട്ടണുകൾക്ക് ഗ്ലോ ഇഫക്റ്റ് */
    .stButton>button {
        border-radius: 10px;
        background: #000 !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        box-shadow: 0px 0px 10px rgba(255, 215, 0, 0.3);
    }
    
    .stButton>button:hover {
        box-shadow: 0px 0px 20px rgba(255, 215, 0, 0.6);
        transform: scale(1.02);
    }

    .balance-box { 
        background: rgba(0, 0, 0, 0.9); 
        color: #00FF00; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
        font-size: 24px; 
        font-weight: bold; 
        border: 2px solid #FFD700; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    
    .info-box { 
        background-color: rgba(255, 255, 255, 0.1); 
        padding: 10px; 
        border-radius: 8px; 
        color: #FFD700 !important; 
        text-align: center; 
        border: 1px solid #FFD700; 
        margin-bottom: 5px; 
    }
    h1, h2, h3, label { color: black !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# 30 സെക്കൻഡിൽ ഓട്ടോ റിഫ്രഷ്
st_autorefresh(interval=30000, key="paichi_hub_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ഫംഗ്ഷനുകൾ ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- 🔐 ലോഗിൻ ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE HUB LOGIN")
    u_raw = st.text_input("Username").lower().strip()
    p_raw = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u_raw in USERS and USERS[u_raw]["pw"] == p_raw:
            st.session_state.auth, st.session_state.user, st.session_state.role = True, u_raw.capitalize(), USERS[u_raw]["role"]
            st.rerun()
        else: st.error("Access Denied!")
else:
    # --- 👤 സൈഡ് ബാർ (AI Style) ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        
        # ലൈവ് റേറ്റുകൾ
        st.write("📊 **Live Market**")
        ex_rate = get_live_price("AEDINR=X")
        crude = get_live_price("CL=F")
        nifty = get_live_price("^NSEI")
        
        st.markdown(f'<div class="info-box">AED/INR: ₹{ex_rate:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">Crude Oil: ${crude:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">Nifty 50: {nifty:,.1f}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # മെനു
        if st.session_state.role == "admin":
            menu = ["🏠 Dashboard", "💰 Add Entry", "🤝 Debt Tracker", "📈 Trading Journal", "🔍 Search & View"]
        else:
            menu = ["💰 Add Entry"]
        
        page = st.radio("Menu", menu)
        
        st.divider()
        if st.button("Log Out"):
            st.session_state.auth = False
            st.rerun()
        st.markdown("[💬 Contact on WhatsApp](https://wa.me/918714752210)")

    # --- 🏠 DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title(f"Welcome, {st.session_state.user}!")
        col1, col2 = st.columns(2)
        
        try:
            df_exp = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
            df_exp.columns = df_exp.columns.str.strip()
            bal = pd.to_numeric(df_exp['Credit'], errors='coerce').sum() - pd.to_numeric(df_exp['Debit'], errors='coerce').sum()
            col1.markdown(f'<div class="balance-box">Family Balance<br>₹{bal:,.2f}</div>', unsafe_allow_html=True)
        except: col1.error("Sheet Sync Error")

        if os.path.exists(TRADE_FILE):
            df_t = pd.read_csv(TRADE_FILE)
            t_pnl = df_t['P&L'].sum()
            col2.markdown(f'<div class="balance-box">Trading P&L<br>₹{t_pnl:,.2f}</div>', unsafe_allow_html=True)

        st.subheader("Recent Activity")
        st.dataframe(df_exp.iloc[::-1].head(10), use_container_width=True)

    # --- 💰 ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("Add New Transaction")
        v = speech_to_text(language='ml', key='voice_exp')
        with st.form("exp_form", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            am = st.number_input("Amount (₹)", value=None)
            ty = st.radio("Entry Type", ["Debit (Expense)", "Credit (Income)"], horizontal=True)
            if st.form_submit_button("SAVE TO SHEET"):
                if it and am:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": f"[{st.session_state.user}] {it}", 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    }
                    requests.post(FORM_API, data=payload)
                    st.success("Transaction recorded successfully! ✅")
                    st.cache_data.clear()

    # --- 📈 TRADING JOURNAL ---
    elif page == "📈 Trading Journal":
        st.title("Option Trading Log")
        with st.form("trade_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            idx = col1.selectbox("Asset", ["NIFTY", "BANKNIFTY", "CRUDE OIL", "MCX"])
            stk = col2.text_input("Strike/Contract", placeholder="Ex: 22500 CE")
            e_p = col1.number_input("Entry Price")
            ex_p = col2.number_input("Exit Price")
            q = col1.number_input("Qty", step=1)
            mood = col2.selectbox("Trading Mood", ["Calm", "Disciplined", "Fear", "Greedy"])
            
            if st.form_submit_button("LOG TRADE"):
                pnl = (ex_p - e_p) * q
                df_new = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), f"{idx} {stk}", e_p, ex_p, q, pnl, mood]], 
                                      columns=['Date', 'Item', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
                if not os.path.isfile(TRADE_FILE): df_new.to_csv(TRADE_FILE, index=False)
                else: df_new.to_csv(TRADE_FILE, mode='a', header=False, index=False)
                st.success(f"Trade saved! P&L: ₹{pnl:,.2f}")

    # --- 🔍 SEARCH & VIEW ---
    elif page == "🔍 Search & View":
        st.title("Full History")
        search = st.text_input("Search items...")
        if df_exp is not None:
            filtered = df_exp[df_exp['Item'].str.contains(search, case=False, na=False)]
            st.dataframe(filtered.iloc[::-1], use_container_width=True)

st.markdown('<p style="text-align: center; color: #000; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
