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

st.set_page_config(page_title="PAICHI v18.0", layout="wide")
st_autorefresh(interval=30000, key="refresh")

# --- 2. THEME ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #2D0844, #1A0521); color: #fff; }
    .purple-box { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid gold; text-align: center; margin-bottom: 15px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { background: gold; color: black; border-radius: 8px; font-weight: bold; width: 100%; }
</style>""", unsafe_allow_html=True)

# --- 3. CORE FUNCTIONS ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={datetime.now().second}")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except: return None

def get_market_signals():
    results = []
    symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
    for name, sym in symbols.items():
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="2d", interval="5m")
            if df.empty: continue
            
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            atr = (df['High'] - df['Low']).rolling(10).mean().iloc[-1]
            lower_band = ((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr)
            
            if last_p > pivot and rsi > 55 and last_p > lower_band: sig, col = "🚀 BUY", "#00FF00"
            elif last_p < pivot and rsi < 45 and last_p < lower_band: sig, col = "📉 SELL", "#FF3131"
            else: sig, col = "⚖️ WAIT", "gold"
            
            # Crude Price Adjustment for Dubai context
            if name == "Crude Fut": last_p *= 83.5
            
            results.append({"name": name, "price": last_p, "sig": sig, "col": col, "rsi": rsi})
        except: continue
    return results

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    # Sidebar navigation
    page = "💰 Add Entry" if curr_user == "shabana" else st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])
    
    df = get_data()

    if page == "📊 Advisor":
        st.title("🚀 Smart Trading Advisor")
        signals = get_market_signals()
        if signals:
            for s in signals:
                st.markdown(f'''<div class="purple-box" style="border-color:{s['col']}">
                    <h2 style="color:lavender !important;">{s['name']}</h2>
                    <h1 style="color:{s['col']} !important; font-size:45px;">{s['sig']}</h1>
                    <h2 style="color:gold !important;">₹{s['price']:,.0f}</h2>
                    <p>RSI: {s['rsi']:.1f}</p></div>''', unsafe_allow_html=True)
        else: st.warning("Market data loading...")

    elif page == "🏠 Dashboard":
        st.title("📈 Performance Tracker")
        if df is not None:
            # P&L Line Chart
            df['Net'] = df['Credit'] - df['Debit']
            daily = df.groupby('Date')['Net'].sum().reset_index().sort_values('Date')
            fig = px.line(daily, x='Date', y='Net', title="Daily P&L Trend", markers=True)
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            
            # Expense Pie Chart
            df['Cat'] = df['Item'].str.extract(r'\[(.*?)\]').fillna("Other")
            expenses = df[df['Debit'] > 0].groupby('Cat')['Debit'].sum().reset_index()
            if not expenses.empty:
                fig_pie = px.pie(expenses, values='Debit', names='Cat', hole=.4, title="Spending Analysis")
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_pie, use_container_width=True)

    elif page == "💰 Add Entry":
        st.title("Transaction Entry")
        balance = (df['Credit'].sum() - df['Debit'].sum()) if df is not None else 0
        st.markdown(f'<div class="purple-box"><h3>Current Balance</h3><h1 style="color:gold;">₹{balance:,.0f}</h1></div>', unsafe_allow_html=True)
        
        voice_val = speech_to_text(language='ml', key='voice_input')
        with st.form("entry_form"):
            item = st.text_input("Details", value=voice_val if voice_val else "")
            amount = st.number_input("Amount", min_value=1, value=None)
            category = st.selectbox("Category", ["Food", "Trading", "Rent", "Salary", "Shopping", "Other"])
            
            if st.form_submit_button("SAVE TO SHEET"):
                if item and amount:
                    is_credit = category in ["Salary"]
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%d/%m/%Y"),
                        "entry.2013476337": f"[{category}] {item}",
                        "entry.1460982454": amount if not is_credit else 0, # Debit
                        "entry.1221658767": amount if is_credit else 0     # Credit
                    })
                    st.success("Entry Saved Successfully! ✅")
                    st.rerun()

    elif page == "🔍 History":
        st.title("Recent Transactions")
        if df is not None: st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
