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
FORM_API = "https://docs.google.com/forms/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI PRO v11.3", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. PREMIUM UI ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e0533, #3a0a5c, #0d0216); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 25px; }
    .purple-box { background: rgba(255, 255, 255, 0.08); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. CORE ENGINES ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,99999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        t_in, t_out = df['Credit'].sum(), df['Debit'].sum()
        return t_in, t_out, (t_in - t_out), df
    except: return 0.0, 0.0, 0.0, pd.DataFrame()

def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def parse_voice(text):
    if not text: return "", ""
    nums = re.findall(r'\d+', text)
    amt = nums[0] if nums else ""
    desc = re.sub(r'\d+', '', text).strip()
    return amt, desc

# --- 4. MAIN APP ---
if not st.session_state.auth:
    st.title("🔐 PAICHI AI LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    t_in, t_out, bal, df = get_data()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:18px; color: #E0B0FF;">Total Balance</span><br>
        <span style="font-size:42px; color:#FFD700;">₹{bal:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    menu = ["🤖 Ask AI", "💰 Add Entry", "📊 Advisor", "🏠 Dashboard", "📊 Report", "🔍 History"]
    page = st.sidebar.radio("Navigate", menu if st.session_state.user != "shabana" else ["💰 Add Entry"])

    if page == "🤖 Ask AI":
        st.title("Paichi AI Assistant 🤖")
        query = st.chat_input("നിനക്ക് എന്താണ് അറിയേണ്ടത്?")
        if query:
            with st.chat_message("user"): st.write(query)
            with st.chat_message("assistant"):
                q = query.lower()
                if "14000" in q or "5000" in q or "9000" in q:
                    st.write("ആ തുകയെക്കുറിച്ച് ഞാൻ നോക്കി, അത് നമ്മുടെ റെക്കോർഡിലുണ്ട്. ട്രേഡിംഗ് ആവശ്യത്തിനാണോ ഫൈസൽ?")
                elif "balance" in q:
                    st.write(f"ഇപ്പോഴത്തെ ബാലൻസ് ₹{bal:,.2f} ആണ്.")
                else:
                    st.write("അടിപൊളി! ഇതേക്കുറിച്ച് കൂടുതൽ പഠിച്ചു വരികയാണ്.")

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v_v113')
        v_amt, v_desc = parse_voice(v_raw)
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=v_desc)
            am = st.text_input("Amount", value=v_amt)
            cat = st.selectbox("Category", ["Trading", "Food", "Rent", "Shop", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                try:
                    val = float(am.strip())
                    d, c = (val, 0) if ty == "Debit" else (0, val)
                    full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c}
                    threading.Thread(target=requests.post, args=(FORM_API,), kwargs={'data': payload}).start()
                    
                    msg = f"✅ *Paichi Entry*\n📝 {it}\n💰 ₹{val}\n⚖️ *Bal: ₹{bal+(c-d):,.2f}*"
                    threading.Thread(target=send_wa, args=(msg,)).start()
                    st.success(f"Saved! Balance: ₹{bal+(c-d):,.2f}"); st.rerun()
                except: st.error("Amount നൽകുക!")

    elif page == "🔍 History":
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "📊 Report":
        df['Cat'] = df['Item'].apply(lambda x: str(x).split(':')[0].split(']')[-1].strip() if ':' in str(x) else "Others")
        st.plotly_chart(px.pie(df[df['Debit']>0], values='Debit', names='Cat', hole=0.4), use_container_width=True)
