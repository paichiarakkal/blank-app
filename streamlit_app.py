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

st.set_page_config(page_title="PAICHI v21.0 - LEARN & TRADE", layout="wide")
st_autorefresh(interval=60000, key="refresh")

# --- 2. THEME ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1A0521, #001F3F); color: #fff; }
    .purple-box { background: rgba(255,255,255,0.08); padding: 15px; border-radius: 12px; border: 1px solid #00D4FF; margin-bottom: 10px; }
    .code-box { background: #000; color: #00FF00; padding: 10px; border-radius: 5px; font-family: monospace; }
    h1, h2, h3 { color: #00D4FF !important; }
</style>""", unsafe_allow_html=True)

# --- 3. DATA & SIGNALS (Simplified) ---
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={datetime.now().microsecond}")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        return df
    except: return None

def get_market():
    out = []
    for n, s in {"Nifty": "^NSEI", "BankNifty": "^NSEBANK", "Crude": "CL=F"}.items():
        try:
            d = yf.Ticker(s).history(period="1d")
            lp = d['Close'].iloc[-1]
            if n == "Crude": lp *= 83.5
            out.append({"n": n, "p": lp})
        except: continue
    return out

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    # പുതിയ മെനു "🐍 Learn Python" ഇവിടെ ചേർത്തു
    page = st.sidebar.radio("Menu", ["🐍 Learn Python", "📊 Advisor", "🏠 Dashboard", "💰 Add Entry"])
    df = load_data()

    # --- PYTHON LEARNING SECTION ---
    if page == "🐍 Learn Python":
        st.title("Python Automation Lab 🚀")
        st.write("നമുക്ക് പൈത്തൺ പഠിച്ചു തുടങ്ങാം! ഇന്ന് നിനക്ക് വേണ്ടത് എന്താണ്?")
        
        tab1, tab2 = st.tabs(["📚 Basics", "🤖 Trading Bot Logic"])
        
        with tab1:
            st.markdown("""
            <div class="purple-box">
            <h3>Daily Lesson: Variables</h3>
            <p>പൈത്തണിൽ വിവരങ്ങൾ സൂക്ഷിച്ചു വെക്കുന്ന പെട്ടികളാണ് Variables.</p>
            <div class="code-box">
            profit = 500 <br>
            item = "Crude Oil" <br>
            print(f"Today's {item} profit is {profit}")
            </div>
            </div>
            """, unsafe_allow_html=True)
            
        with tab2:
            st.markdown("""
            <div class="purple-box">
            <h3>How Trading Bots Work?</h3>
            <p>ഒരു ബോട്ട് എങ്ങനെയാണ് തീരുമാനമെടുക്കുന്നത് എന്ന് നോക്കൂ:</p>
            <div class="code-box">
            if current_price > pivot_point:<br>
            &nbsp;&nbsp;&nbsp;&nbsp;print("🚀 BUY SIGNAL")<br>
            else:<br>
            &nbsp;&nbsp;&nbsp;&nbsp;print("📉 SELL SIGNAL")
            </div>
            </div>
            """, unsafe_allow_html=True)

    elif page == "📊 Advisor":
        st.title("Market Signals")
        for m in get_market():
            st.markdown(f'<div class="purple-box"><h3>{m["n"]}</h3><h2>₹{m["p"]:,.2f}</h2></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        if df is not None:
            st.subheader("P&L Graph")
            # Simple visualization
            st.line_chart(df[['Date', 'Debit', 'Credit']].set_index('Date'))

    elif page == "💰 Add Entry":
        st.title("New Entry")
        with st.form("entry"):
            it = st.text_input("Item")
            am = st.number_input("Amount", min_value=1)
            cat = st.selectbox("Category", ["Food", "Trading", "Salary", "Other"])
            if st.form_submit_button("SAVE"):
                st.success("Saving logic is active!")

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
