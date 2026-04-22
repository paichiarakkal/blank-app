import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v4.2", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521);
        color: #fff;
    }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button {
        background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold;
    }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center; margin-bottom: 20px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 SMART ENGINES ---

def process_voice(text):
    """വോയ്‌സിൽ നിന്ന് വിവരങ്ങൾ വേർതിരിക്കുന്നു (Updated with more keywords)"""
    if not text: return "Others", None
    text = text.lower()
    
    # എമൗണ്ട് കണ്ടെത്തുന്നു
    nums = re.findall(r'\d+', text)
    amount = float(nums[0]) if nums else None
    
    # കാറ്റഗറി മാപ്പിംഗ്
    category = "Others"
    if any(x in text for x in ["food", "ഭക്ഷണം", "ഹോട്ടൽ", "ചായ", "tea", "coffee", "ബിരിയാണി"]): category = "Food"
    elif any(x in text for x in ["shop", "കട", "സാധനം", "ഷോപ്പിംഗ്", "ബസാർ"]): category = "Shop"
    elif any(x in text for x in ["fish", "മീൻ", "മത്തി"]): category = "Fish"
    elif any(x in text for x in ["travel", "യാത്ര", "ബസ്", "പെട്രോൾ", "diesel", "auto"]): category = "Travel"
    elif any(x in text for x in ["chicken", "ചിക്കൻ", "കോഴി"]): category = "Chicken"
    elif any(x in text for x in ["rent", "വാടക"]): category = "Rent"
    elif any(x in text for x in ["trading", "ട്രേഡിംഗ്", "profit", "loss"]): category = "Trading"
    
    return category, amount

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        cols = df.columns.tolist()
        for col in cols: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln()
        pdf.set_font("Arial", size=9)
        for i, row in df.iterrows():
            for col in cols:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(38, 10, txt=val, border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

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
            elif last_p < pivot and rsi < 45 and not st_buy: signal, color = "📉 SELL", "#FF3131"
            else: signal, color = "⚖️ WAIT", "#FFFF00"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": rsi, "color": color})
        return results
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
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
    if curr_user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    if page == "📊 Advisor" and curr_user != "shabana":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f"""<div class="purple-box" style="border-color: {m['color']} !important;">
                    <h2 style="color:#E0B0FF !important;">{m["name"]}</h2>
                    <h1 style="color:{m["color"]} !important; font-size:55px;">{m["signal"]}</h1>
                    <h1 style="color:#FFD700 !important; font-size:50px;">₹{m["price"]:,.0f}</h1>
                    <p>RSI: {m["rsi"]:.1f}</p>
                </div>""", unsafe_allow_html=True)

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Financial Status")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            balance = total_in - total_out
            st.markdown(f"""<div class="purple-box" style="border-color: #FFD700 !important;">
                <p style="color:#E0B0FF !important; font-size:20px;">Net Balance</p>
                <h1 style="color:#FFD700 !important; font-size:65px;">₹{balance:,.2f}</h1>
            </div>""", unsafe_allow_html=True)
        except: st.error("Error loading data.")

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_text = speech_to_text(language='ml', key='smart_voice_v2')
        v_cat, v_amt = process_voice(v_text)
        
        if v_text: st.info(f"തിരിച്ചറിഞ്ഞത്: {v_cat} | Amount: {v_amt if v_amt else '??'}")

        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Description", value=v_text if v_text else "")
            am = st.number_input("Amount", min_value=0.0, value=v_amt, placeholder="Enter Amount...")
            cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Trading", "Others"]
            default_idx = cat_list.index(v_cat) if v_cat in cat_list else 7
            cat = st.selectbox("Category", cat_list, index=default_idx)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE DATA"):
                if it and am and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    st.success(f"✅ {cat} saved!")
                    st.rerun()

    elif page == "📊 Report" and curr_user != "shabana":
        st.title("Expense Analysis")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            if 'Debit' in df.columns:
                df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
                df['Category'] = df['Item'].apply(lambda x: str(x).split(':')[0] if ':' in str(x) else 'Other')
                report_df = df[df['Debit'] > 0].groupby('Category')['Debit'].sum().reset_index()
                fig = px.pie(report_df, values='Debit', names='Category', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Error loading Report")

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            pdf_bytes = create_pdf(df)
            if pdf_bytes:
                st.download_button(label="📥 Download PDF", data=pdf_bytes, file_name="Finance_Report.pdf", mime="application/pdf")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("Loading History...")

    elif page == "🤝 Debt Tracker" and curr_user != "shabana":
        st.title("Debt Management")
        with st.form("debt_f"):
            n, a = st.text_input("Name"), st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["Borrowed", "Lent"])
            if st.form_submit_button("SAVE"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t} - {n}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")
