import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ക്രമീകരണങ്ങൾ
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"},
    "admin": {"pw": "paichi786", "role": "admin"}
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Smart Finance", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 🎨 THEME & STYLE ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; }
    .quick-btn { margin: 5px; border-radius: 10px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FAMILY LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u in USERS and USERS[u]["pw"] == p:
            st.session_state.auth, st.session_state.user, st.session_state.role = True, u.capitalize(), USERS[u]["role"]
            st.rerun()
        else: st.error("Access Denied!")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
            df.columns = df.columns.str.strip()
            for c in ['Debit', 'Credit']:
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()
    st.sidebar.title(f"👤 {st.session_state.user}")
    
    pages = ["💰 Add Entry"]
    if st.session_state.role == "admin":
        pages = ["🏠 Dashboard", "💰 Add Entry", "🔍 Search & History", "📊 Analysis"]
    
    page = st.sidebar.radio("Go to", pages)

    # --- 🏠 DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title("Financial Summary")
        if df is not None:
            bal = df['Credit'].sum() - df['Debit'].sum()
            st.markdown(f'<div class="balance-box">Total Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            # Comparison Logic
            st.subheader("Monthly Comparison")
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            curr_month = datetime.now().month
            this_month_exp = df[df['Date'].dt.month == curr_month]['Debit'].sum()
            st.metric("This Month Expenses", f"₹{this_month_exp:,.2f}")

    # --- 💰 ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("New Entry")
        
        # Quick Buttons
        st.write("Quick Add:")
        col1, col2, col3, col4 = st.columns(4)
        q_item, q_amt = "", None
        if col1.button("☕ Tea (10)"): q_item, q_amt = "Tea", 10
        if col2.button("⛽ Petrol (500)"): q_item, q_amt = "Petrol", 500
        if col3.button("🥛 Milk (30)"): q_item, q_amt = "Milk", 30
        if col4.button("🏠 Rent"): q_item, q_amt = "House Rent", None

        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=q_item if q_item else (v if v else ""))
            am = st.number_input("Amount", value=q_amt if q_amt else None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("Entry Saved! ✅")
                    st.cache_data.clear()

    # --- 🔍 SEARCH ---
    elif page == "🔍 Search & History":
        st.title("Search History")
        s = st.text_input("Search for items, users, or dates...")
        if df is not None:
            res = df[df['Item'].str.contains(s, case=False, na=False)]
            st.dataframe(res.iloc[::-1], use_container_width=True)

    # --- 📊 ANALYSIS ---
    elif page == "📊 Analysis":
        st.title("Expense Charts")
        if df is not None:
            chart_data = df[df['Debit'] > 0].groupby('Item')['Debit'].sum().reset_index()
            fig = px.bar(chart_data, x='Item', y='Debit', color='Item', title="Spending by Category")
            st.plotly_chart(fig, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
