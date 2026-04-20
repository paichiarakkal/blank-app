import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI v14.0 - PRO TRACKER", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; backdrop-filter: blur(10px); }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 20px; border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center; margin-bottom: 15px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. DATA ENGINE ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        # ഷീറ്റിലെ തീയതി കോളം ഫോർമാറ്റ് ചെയ്യുന്നു
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        # നിന്റെ ഷീറ്റിലെ 'Debit', 'Credit' കോളങ്ങൾ നമ്പർ ആക്കുന്നു
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower(); p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    if curr_user == "shabana": page = "💰 Add Entry"
    else:
        st.sidebar.title(f"👤 {curr_user.capitalize()}")
        page = st.sidebar.radio("Menu", ["🏠 Dashboard", "📊 Advisor", "💰 Add Entry", "🔍 History"])

    df = get_data()

    if page == "💰 Add Entry":
        st.title("Add Transaction")
        bal = (df['Credit'].sum() - df['Debit'].sum()) if df is not None else 0
        st.markdown(f'<div class="purple-box" style="border-color:#FFD700;"><h3>Balance</h3><h1 style="color:#FFD700;">₹{bal:,.0f}</h1></div>', unsafe_allow_html=True)
        
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form_v14", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            am = st.number_input("Amount", min_value=1, value=None, placeholder="Enter amount")
            cat = st.selectbox("Category", ["Trading", "Food", "Rent", "Salary", "Shopping", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE TO SHEET"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    # നിന്റെ ഷീറ്റിലെ കോളങ്ങളിലേക്ക് ഡാറ്റ അയക്കുന്നു
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%d/%m/%Y"), # തീയതി
                        "entry.2013476337": f"[{cat}] {it}", # ഐറ്റം വിവരങ്ങൾ
                        "entry.1460982454": d, # Debit
                        "entry.1221658767": c  # Credit
                    })
                    st.success("വിജയകരമായി സേവ് ചെയ്തു! ✅")
                    st.rerun()

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("📈 Performance Tracker")
        if df is not None:
            # 1. Net Profit/Loss Chart
            df['Net'] = df['Credit'] - df['Debit']
            # തീയതി അനുസരിച്ച് ഗ്രൂപ്പ് ചെയ്യുന്നു
            daily_df = df.groupby('Date')['Net'].sum().reset_index().sort_values('Date')
            
            fig = px.line(daily_df, x='Date', y='Net', title="Daily Profit/Loss Trend", markers=True)
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)

            # 2. Category Wise Splitting
            st.subheader("Expense Distribution")
            df['Cat'] = df['Item'].str.extract(r'\[(.*?)\]').fillna("Others")
            cat_df = df[df['Debit'] > 0].groupby('Cat')['Debit'].sum().reset_index()
            if not cat_df.empty:
                fig_pie = px.pie(cat_df, values='Debit', names='Cat', hole=.4)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_pie, use_container_width=True)

    elif page == "🔍 History":
        st.title("History")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()
