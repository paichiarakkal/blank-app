import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ലോഗിൻ വിവരങ്ങൾ (ഇവിടെ പുതിയ മെമ്പർമാരെ ആഡ് ചെയ്യാം)
USERS = {
    "faisal": {"pw": "faisal123", "role": "admin"},
    "shabana": {"pw": "shabana123", "role": "user"},
    "admin": {"pw": "paichi786", "role": "admin"}
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Finance", layout="wide")

# സെഷൻ സ്റ്റേറ്റ്
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 🎨 THEME CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN ---
if not st.session_state.auth:
    st.title("🔐 FAMILY LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u in USERS and USERS[u]["pw"] == p:
            st.session_state.auth = True
            st.session_state.user = u.capitalize()
            st.session_state.role = USERS[u]["role"]
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
    st.sidebar.title(f"👤 {st.session_state.user} ({st.session_state.role})")
    
    # റോൾ അനുസരിച്ചുള്ള മെനു
    menu_options = ["💰 Add Entry"]
    if st.session_state.role == "admin":
        menu_options = ["🏠 Home Dashboard", "💰 Add Entry", "🔍 Search & View", "📊 Expense Report"]
    
    page = st.sidebar.radio("Menu", menu_options)
    
    if st.sidebar.button("Log Out"): 
        st.session_state.auth = False
        st.rerun()

    # --- 🏠 HOME DASHBOARD (Admin Only) ---
    if page == "🏠 Home Dashboard":
        st.title("Financial Overview")
        if df is not None:
            bal = df['Credit'].sum() - df['Debit'].sum()
            st.markdown(f'<div class="balance-box">Total Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            st.subheader("Recent Activity")
            st.dataframe(df.iloc[::-1].head(10), use_container_width=True)

    # --- 💰 ADD ENTRY (Everyone) ---
    elif page == "💰 Add Entry":
        st.title("Add New Expense/Income")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    # ആര് ആഡ് ചെയ്തു എന്ന് മനസ്സിലാക്കാൻ പേര് ചേർക്കുന്നു
                    user_tag = f"[{st.session_state.user}] {it}"
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": user_tag, 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    }
                    requests.post(FORM_API, data=payload)
                    st.success(f"Saved by {st.session_state.user}! ✅")
                    st.cache_data.clear()

    # --- 🔍 SEARCH (Admin Only) ---
    elif page == "🔍 Search & View":
        st.title("Search Records")
        search = st.text_input("Search Item or User")
        if df is not None:
            filtered = df[df['Item'].str.contains(search, case=False, na=False)]
            st.dataframe(filtered.iloc[::-1], use_container_width=True)

    # --- 📊 REPORTS (Admin Only) ---
    elif page == "📊 Expense Report":
        st.title("Spending Analysis")
        if df is not None:
            sdf = df[df['Debit'] > 0].groupby('Item')['Debit'].sum().reset_index()
            fig = px.pie(sdf, values='Debit', names='Item', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
