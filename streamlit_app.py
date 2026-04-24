import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import re
import urllib.parse
import threading

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI SMART v11.1", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. PREMIUM UI ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e0533, #3a0a5c, #0d0216); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 25px; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'currency' not in st.session_state: st.session_state.currency = "INR"

# --- 3. CORE ENGINES ---

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,99999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        t_in = df['Credit'].sum()
        t_out = df['Debit'].sum()
        return t_in, t_out, (t_in - t_out), df
    except: return 0.0, 0.0, 0.0, pd.DataFrame()

# --- 4. MAIN LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI AI LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    t_in, t_out, bal_inr, main_df = get_data()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:18px; color: #E0B0FF;">Total Balance</span><br>
        <span style="font-size:42px; color:#FFD700;">₹{bal_inr:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    menu = ["💰 Add Entry"] if st.session_state.user == "shabana" else ["🤖 Ask Paichi AI", "📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History"]
    page = st.sidebar.radio("Navigate", menu)

    if page == "🤖 Ask Paichi AI":
        st.title("Paichi AI Assistant 🤖")
        user_query = st.chat_input("Ask me anything...")
        
        if user_query:
            with st.chat_message("user"): st.write(user_query)
            with st.chat_message("assistant"):
                q = user_query.lower()
                # സ്മാർട്ട് ഡാറ്റ ചെക്കിംഗ് ലോജിക്
                if "rent" in q or "വാടക" in q:
                    rent_amt = main_df[main_df['Item'].str.contains("Rent", case=False, na=False)]['Debit'].sum()
                    st.write(f"ഫൈസൽ, നിന്റെ റെന്റ് ഇനം ചെലവ് ഇതുവരെ ₹{rent_amt:,.2f} ആണ്.")
                elif "food" in q or "ഭക്ഷണം" in q:
                    food_amt = main_df[main_df['Item'].str.contains("Food", case=False, na=False)]['Debit'].sum()
                    st.write(f"ഭക്ഷണത്തിനായി നീ ഇതുവരെ ₹{food_amt:,.2f} ചെലവാക്കിയിട്ടുണ്ട്.")
                elif "ചെലവ്" in q or "expense" in q:
                    st.write(f"നിന്റെ മൊത്തം ചെലവ് ₹{t_out:,.2f} ആണ്.")
                elif "balance" in q or "ബാലൻസ്" in q:
                    st.write(f"കയ്യിലുള്ള ബാലൻസ് ₹{bal_inr:,.2f} ആണ്.")
                else:
                    st.write("അടിപൊളി! ഇതേക്കുറിച്ച് കൂടുതൽ വിവരങ്ങൾ ഞാൻ ശേഖരിച്ചു വരികയാണ്. വേറെ എന്തെങ്കിലും അറിയണോ?")

    elif page == "💰 Add Entry":
        st.title("Add Transaction")
        v_raw = speech_to_text(language='ml', key='v111')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_raw if v_raw else "")
            am = st.text_input("Amount")
            cat = st.selectbox("Category", ["Food", "Shop", "Rent", "Trading", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                try:
                    val = float(am)
                    d, c = (val, 0) if ty == "Debit" else (0, val)
                    full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c}
                    threading.Thread(target=requests.post, args=(FORM_API,), kwargs={'data': payload}).start()
                    st.success("Saved!"); st.rerun()
                except: st.error("Amount നൽകുക!")

    elif page == "📊 Report":
        st.title("Expense Analysis")
        # കാറ്റഗറി റിപ്പോർട്ട് ശരിയാക്കിയത്
        main_df['Cat_Only'] = main_df['Item'].apply(lambda x: str(x).split(':')[0].split(']')[-1].strip() if ':' in str(x) else "Others")
        rdf = main_df[main_df['Debit'] > 0].groupby('Cat_Only')['Debit'].sum().reset_index()
        if not rdf.empty:
            st.plotly_chart(px.pie(rdf, values='Debit', names='Cat_Only', hole=0.4), use_container_width=True)

    elif page == "🔍 History":
        st.dataframe(main_df.iloc[::-1], use_container_width=True)
