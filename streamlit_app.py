import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. കോൺഫിഗറേഷൻ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}
HOUSE_GOAL = 5000000  # പുതിയ വീടിനായുള്ള ഏകദേശ ലക്ഷ്യം (നിങ്ങൾക്ക് മാറ്റാം)

st.set_page_config(page_title="PAICHI Finance Pro", layout="wide")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'auth' not in st.session_state: st.session_state.auth = False
if 'theme' not in st.session_state: st.session_state.theme = "Gold"

# --- 🎨 THEME SELECTOR & CSS ---
theme_choice = st.sidebar.selectbox("Choose Theme", ["Gold", "Dark", "Professional"])

if theme_choice == "Gold":
    bg, text, box = "linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C)", "#000", "rgba(0,0,0,0.85)"
elif theme_choice == "Dark":
    bg, text, box = "#121212", "#FFF", "#1E1E1E"
else:
    bg, text, box = "#f0f2f6", "#333", "#FFF"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: {text}; }}
    .balance-box {{ background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
    .goal-box {{ background: {box}; padding: 20px; border-radius: 15px; border: 1px solid #FFD700; margin-top: 10px; color: {text}; }}
    h1, h2, h3, label, p {{ color: {text} !important; }}
    .stDataFrame {{ background: white; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
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
    page = st.sidebar.radio("Menu", ["🏠 Home & Goals", "💰 Add Entry", "🔍 Search & Filter", "🤝 Debt Tracker", "📊 Expense Report"])
    
    if st.sidebar.button("Log Out"): 
        st.session_state.auth = False
        st.rerun()

    # --- 🏠 HOME & GOALS ---
    if page == "🏠 Home & Goals":
        st.title("Financial Dashboard")
        if df is not None:
            bal = df['Credit'].sum() - df['Debit'].sum()
            st.markdown(f'<div class="balance-box">കൈവശമുള്ള തുക: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            # 🏠 HOUSE GOAL TRACKER
            st.subheader("🏗️ New House Goal")
            saved_for_house = bal # തൽക്കാലം കൈവശമുള്ള തുക വീടിനായി കരുതുന്നു
            progress = min(saved_for_house / HOUSE_GOAL, 1.0)
            
            st.markdown('<div class="goal-box">', unsafe_allow_html=True)
            st.write(f"ലക്ഷ്യം: ₹{HOUSE_GOAL:,.2f}")
            st.progress(progress)
            st.write(f"പൂർത്തിയായത്: {progress*100:.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- 💰 ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("New Entry")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("Saved! ✅")
                    st.cache_data.clear()

    # --- 🔍 SEARCH & FILTER ---
    elif page == "🔍 Search & Filter":
        st.title("Find Records")
        search = st.text_input("Search (പേര് അല്ലെങ്കിൽ സാധനം സന്ദർശിക്കുക)")
        if df is not None:
            filtered_df = df[df['Item'].str.contains(search, case=False, na=False)]
            st.dataframe(filtered_df.iloc[::-1], use_container_width=True)
            st.write(f"ആകെ ചിലവ് (ഈ സെർച്ച്): ₹{filtered_df['Debit'].sum():,.2f}")

    # --- 📊 EXPENSE REPORT ---
    elif page == "📊 Expense Report":
        st.title("Analysis")
        if df is not None:
            sdf = df[df['Debit'] > 0].groupby('Item')['Debit'].sum().reset_index()
            fig = px.pie(sdf, values='Debit', names='Item', hole=0.4, title="Expense Distribution")
            st.plotly_chart(fig, use_container_width=True)
