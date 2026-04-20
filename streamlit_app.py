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

st.set_page_config(page_title="PAICHI v22.0", layout="wide")
st_autorefresh(interval=60000, key="refresh")

# --- 2. THEME ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1A0521, #001F3F); color: #fff; }
    .purple-box { background: rgba(255,255,255,0.08); padding: 15px; border-radius: 12px; border: 1px solid #00D4FF; margin-bottom: 10px; }
    h1, h2, h3 { color: #00D4FF !important; }
</style>""", unsafe_allow_html=True)

# --- 3. DATA ENGINE (SUPER RELIABLE) ---
def load_data():
    try:
        # നേരിട്ട് ഷീറ്റിൽ നിന്ന് ലേറ്റസ്റ്റ് ഡാറ്റ എടുക്കുന്നു
        df = pd.read_csv(f"{CSV_URL}&r={datetime.now().second}")
        df.columns = df.columns.str.strip() # സ്പേസ് ഒഴിവാക്കാൻ
        
        # തീയതി ഫോർമാറ്റ് ശരിയാക്കുന്നു (D/M/Y)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        
        # നമ്പറുകൾ ശരിയാക്കുന്നു
        for col in ['Debit', 'Credit', 'Amount']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return None

def get_market_signals():
    out = []
    for n, s in {"Nifty": "^NSEI", "BankNifty": "^NSEBANK", "Crude": "CL=F"}.items():
        try:
            d = yf.Ticker(s).history(period="2d", interval="5m")
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
    page = st.sidebar.radio("Menu", ["🔍 History", "🏠 Dashboard", "📊 Advisor", "💰 Add Entry", "🐍 Learn Python"])
    df = load_data()

    if page == "🔍 History":
        st.title("Transaction History")
        if df is not None:
            # ഡാറ്റ ഉണ്ടോ എന്ന് നോക്കി മാത്രം ഡിസ്പ്ലേ ചെയ്യുന്നു
            st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
        else:
            st.error("ഷീറ്റിൽ നിന്ന് ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

    elif page == "🏠 Dashboard":
        st.title("Profit & Loss Analysis")
        if df is not None and not df.empty:
            df['Net'] = df['Credit'] - df['Debit']
            daily = df.groupby('Date')['Net'].sum().reset_index()
            st.plotly_chart(px.line(daily, x='Date', y='Net', title="Daily Performance", markers=True), use_container_width=True)
            
            # Category Pie Chart
            df['Cat'] = df['Item'].str.extract(r'\[(.*?)\]').fillna("Other")
            pie_data = df[df['Debit'] > 0].groupby('Cat')['Debit'].sum().reset_index()
            if not pie_data.empty:
                st.plotly_chart(px.pie(pie_data, values='Debit', names='Cat', hole=.4, title="Spending"), use_container_width=True)

    elif page == "📊 Advisor":
        st.title("Market Prices")
        for m in get_market_signals():
            st.markdown(f'<div class="purple-box"><h3>{m["n"]}</h3><h2>₹{m["p"]:,.2f}</h2></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("New Transaction")
        bal = (df['Credit'].sum() - df['Debit'].sum()) if df is not None else 0
        st.markdown(f'<div class="purple-box"><h2>Balance: ₹{bal:,.0f}</h2></div>', unsafe_allow_html=True)
        v = speech_to_text(language='ml', key='v')
        with st.form("entry_form"):
            it, am = st.text_input("Item", v if v else ""), st.number_input("Amount", min_value=1)
            cat = st.selectbox("Category", ["Food", "Trading", "Rent", "Salary", "Other"])
            if st.form_submit_button("SAVE"):
                if it and am:
                    ty = "Credit" if cat == "Salary" else "Debit"
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%d/%m/%Y"),
                        "entry.2013476337": f"[{cat}] {it}",
                        "entry.1460982454": am if ty=="Debit" else 0,
                        "entry.1221658767": am if ty=="Credit" else 0
                    })
                    st.success("സേവ് ചെയ്തു! റീഫ്രഷ് ചെയ്യൂ."); st.rerun()

    elif page == "🐍 Learn Python":
        st.title("Python Lab")
        st.info("നമുക്ക് കോഡിംഗ് പഠിക്കാം! പൈത്തണിലെ ലിസ്റ്റുകളും ഡിക്ഷണറികളും അടുത്ത പാഠത്തിൽ വരുന്നു.")

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
