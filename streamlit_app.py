import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GLASS PREMIUM v7.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 GLASSMORPHISM DESIGN (Transparent Black Glass) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { 
        background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); 
        color: #fff; 
    }
    
    /* 📱 Transparent Black Glass Sidebar */
    [data-testid="stSidebar"] { 
        background-color: rgba(0, 0, 0, 0.4) !important; 
        backdrop-filter: blur(20px) saturate(150%);
        border-right: 1px solid rgba(255, 255, 255, 0.1); 
    }
    
    /* 💎 Glass Boxes for Advisor & Dashboard */
    .glass-box { 
        background: rgba(0, 0, 0, 0.3); 
        padding: 30px !important; 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        backdrop-filter: blur(10px);
        text-align: center; 
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Gold Buttons */
    .stButton>button { 
        background-color: #FFD700 !important; 
        color: #000 !important; 
        border-radius: 12px; 
        font-weight: bold;
        border: none;
    }
    
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def play_notification():
    audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. MARKET ENGINE ---
def get_market_data():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = {}
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="1d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            if name == "Crude Fut": last_p = round(last_p * 83.5 * 1.15, 0)
            else: last_p = round(last_p, 0)
            results[name] = last_p
        return results
    except: return None

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI GLASS LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    st.sidebar.title(f"👤 {curr_user.capitalize()}")
    
    # 🔒 Restriction Logic
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🚀 Set Price Alerts")
        n_alert = st.sidebar.number_input("Nifty 50 Level", value=0.0)
        c_alert = st.sidebar.number_input("Crude Oil Level", value=0.0)
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    # --- PAGES ---
    if page == "💰 Add Entry":
        st.title("Add Transaction")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            # എക്സ്ട്രാ പൂജ്യങ്ങൾ ഒഴിവാക്കാൻ value=0 ആയി സെറ്റ് ചെയ്തു
            am = st.number_input("Amount", min_value=0, step=1, value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                    st.success("സേവ് ചെയ്തു! ✅")

    elif page == "📊 Advisor" and curr_user != "shabana":
        st.title("Live Market")
        markets = get_market_data()
        if markets:
            # Check Alerts
            if n_alert > 0 and markets.get("Nifty 50", 0) >= n_alert:
                st.warning(f"🚀 NIFTY reached {markets['Nifty 50']}"); play_notification()
            if c_alert > 0 and markets.get("Crude Fut", 0) >= c_alert:
                st.error(f"🛢️ CRUDE reached {markets['Crude Fut']}"); play_notification()

            for name, price in markets.items():
                st.markdown(f'<div class="glass-box"><h3>{name}</h3><h1 style="color:#FFD700;">₹{price:,.0f}</h1></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Financial Status")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            st.markdown(f'<div class="glass-box"><h3>Current Balance</h3><h1 style="color:#FFD700;">₹{total_in - total_out:,.0f}</h1></div>', unsafe_allow_html=True)
        except: st.error("Error loading data")

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("Loading...")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
