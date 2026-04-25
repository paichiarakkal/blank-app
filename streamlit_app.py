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
import time

# ലോട്ടീ ആനിമേഷൻ ലൈബ്രറി ചെക്ക് ചെയ്യുന്നു
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except:
    LOTTIE_OK = False

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v6.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN (Black Glass & Animations) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #000000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 215, 0, 0.2);
    }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.2);
        text-align: center; margin-bottom: 20px;
    }
    .balance-banner {
        background: rgba(255, 215, 0, 0.1);
        padding: 20px; border-radius: 20px; border: 1px solid #FFD700;
        text-align: center; margin-bottom: 25px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER ENGINES ---
def load_lottieurl(url):
    if not LOTTIE_OK: return None
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_panther = load_lottieurl("https://lottie.host/81f9537d-9447-4974-98c4-e86749963721/nQ8Yw2rS6r.json")
lottie_cash = load_lottieurl("https://lottie.host/869e5d4e-b5f7-4184-8840-062639097723/P6v68xT1N3.json")

def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
        st.session_state['last_balance'] = bal
        return bal
    except: return st.session_state.get('last_balance', 0.0)

def get_trading_advisor():
    try:
        symbols = {"NIFTY 50": "^NSEI", "CRUDE OIL": "CL=F", "GIFT NIFTY": "NQ=F"}
        results = []
        for name, sym in symbols.items():
            ticker = yf.Ticker(sym)
            df = ticker.history(period="1d", interval="5m")
            if not df.empty:
                last_price = df['Close'].iloc[-1]
                # Simple Pivot Point Logic
                pivot = (df['High'].max() + df['Low'].min() + df['Close'].iloc[-1]) / 3
                signal = "🚀 BUY" if last_price > pivot else "📉 SELL"
                color = "#00FF00" if "BUY" in signal else "#FF3131"
                results.append({"name": name, "price": last_price, "signal": signal, "color": color})
        return results
    except: return None

# --- 4. LOGIN LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if LOTTIE_OK and lottie_panther: st_lottie(lottie_panther, height=250)
        st.markdown("<h2 style='text-align:center;'>PAICHI VAULT</h2>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome {st.session_state.user.upper()}!")
        page = st.radio("SELECT PAGE", ["💰 Add Entry", "📈 Trading Advisor", "🔍 History"])
        
        # SMS Offline Shortcut
        st.divider()
        current_bal = st.session_state.get('last_balance', 0.0)
        sms_url = f"sms:{WA_PHONE}?body=Current Balance: ₹{current_bal:,.2f}"
        st.markdown(f'**Offline Check:**')
        st.markdown(f'<a href="{sms_url}"><button style="width:100%; border-radius:10px; background:#4CAF50; color:white; border:none; padding:10px;">Get Balance via SMS</button></a>', unsafe_allow_html=True)
        
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    balance = get_total_balance()
    st.markdown(f"""<div class="balance-banner">
        <p style="margin:0; font-size:16px; color:#E0B0FF;">Live Vault Balance</p>
        <h1 style="margin:0; font-size:42px; color:#FFD700;">₹{balance:,.2f}</h1>
    </div>""", unsafe_allow_html=True)

    if page == "💰 Add Entry":
        st.title("🎙️ Add Transaction")
        if LOTTIE_OK and lottie_cash: st_lottie(lottie_cash, height=150)
        
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description")
            am_str = st.text_input("Amount")
            cat = st.selectbox("Category", ["Food", "Shop", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE TO GOOGLE SHEET"):
                try:
                    am = float(am_str)
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{st.session_state.user}] {cat}: {it}"
                    
                    st.toast('Saving to Cloud...', icon='⏳')
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    
                    st.toast('Data Saved!', icon='✅')
                    st.snow()
                    
                    # വാട്സ്ആപ്പിൽ ടോട്ടൽ ബാലൻസ് സഹിതം മെസ്സേജ് അയക്കുന്നു
                    new_bal = balance + (c - d)
                    wa_text = f"✅ *Paichi Entry*\n💰 Amt: ₹{am}\n📝 {it}\n⚖️ *New Balance: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_wa, args=(wa_text,)).start()
                except: st.error("Amount തെറ്റാണ്")

    elif page == "📈 Trading Advisor":
        st.title("🚀 Live Trading Signals")
        signals = get_trading_advisor()
        if signals:
            for s in signals:
                st.markdown(f"""<div class="purple-box" style="border-left: 10px solid {s['color']}">
                    <h3 style="margin:0;">{s['name']}</h3>
                    <h1 style="color:{s['color']} !important;">{s['signal']}</h1>
                    <h2 style="color:#FFD700 !important;">₹{s['price']:,.2f}</h2>
                </div>""", unsafe_allow_html=True)
        else:
            st.warning("Market ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

    elif page == "🔍 History":
        st.title("Transaction History 📜")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("No Data Found")
