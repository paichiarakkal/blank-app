import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
    .stMetric { background: rgba(0,0,0,0.1); padding: 10px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 15 സെക്കൻഡിൽ ആപ്പ് ഓട്ടോ റിഫ്രഷ് ആകും
st_autorefresh(interval=15000, key="faisal_v3_ultimate")

FILE_NAME = 'trade_history_v2.csv'
EXPENSE_FILE = 'home_expenses.csv'

# --- ഫംഗ്ഷനുകൾ ---

def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.80

def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil,Gold&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        full_news = "  |  ".join(news_list)
        return translate(full_news, "ml", "en")
    except: return "വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു..."

def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "ai": ai_p}
    except: return None

# --- 1. മലയാളം ലൈവ് വാർത്തകൾ (TOP) ---
news_mal = get_live_news_malayalam()
st.markdown(f"""
    <div class="news-box">
        <h4 style="color: #BF953F; margin: 0; font-size: 16px; text-align: center;">📰 മലയാളം ലൈവ് വാർത്തകൾ</h4>
        <marquee scrollamount="5" style="color: #FFF; font-size: 18px; font-weight: bold; padding-top: 5px;">
            📢 {news_mal}
        </marquee>
    </div>
""", unsafe_allow_html=True)

# --- 2. സൈഡ് ബാർ മെനു ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    live_aed = get_live_aed_rate()
    st.success(f"💰 1 AED = ₹{live_aed:.2f}")
    
    st.divider()
    option = st.radio("Choose Section", 
        ["📈 Trading AI", "📊 Journal & Dashboard", "💰 Home Expenses", "📚 Student Corner", "📸 Family Gallery"])
    st.divider()

st.markdown(f'<p class="main-title">🚀 Paichi Family Hub</p>', unsafe_allow_html=True)

# --- സെക്ഷൻ ലോജിക് ---

if option == "📈 Trading AI":
    st.header("🎯 Market Analysis")
    symbol = st.selectbox("Select Item", ["CL=F", "^NSEI", "^NSEBANK", "GC=F"], 
                          format_func=lambda x: "Crude Oil" if x=="CL=F" else ("Nifty 50" if x=="^NSEI" else ("Bank Nifty" if x=="^NSEBANK" else "Gold")))
    
    data = get_analysis(symbol)
    if data:
        multi = 93.5 if symbol=="CL=F" else 1
        live_p, ai_p = data['p'] * multi, data['ai'] * multi
        c1, c2 = st.columns(2)
        c1.metric("Live Price", f"₹{live_p:.2f}")
        c2.metric("AI Prediction", f"₹{ai_p:.2f}")
        st.line_chart(pd.DataFrame({"Market Trend": [live_p-2, live_p-1, live_p, ai_p]}))

elif option == "📊 Journal & Dashboard":
    st.header("📝 Trading Journal")
    st.info("നിന്റെ ട്രേഡുകൾ ഇവിടെ രേഖപ്പെടുത്താം.")
    # (Journal code remains here)

elif option == "💰 Home Expenses":
    st.header("🏠 മാസിക ചെലവുകൾ")
    with st.expander("ചെലവ് ആഡ് ചെയ്യുക"):
        date = st.date_input("തിയതി")
        item = st.text_input("സാധനം/വിശദീകരണം")
        amt = st.number_input("തുക (₹)", min_value=0.0)
        if st.button("Save Expense"):
            st.success("സേവ് ചെയ്തു!")

elif option == "📚 Student Corner":
    st.header("👨‍🎓 Study Materials")
    std = st.selectbox("ക്ലാസ്സ് തിരഞ്ഞെടുക്കുക", ["SSLC", "+1", "+2"])
    st.write(f"{std} വിദ്യാർത്ഥികൾക്ക് വേണ്ടിയുള്ള നോട്സുകളും ലിങ്കുകളും ഇവിടെ ലഭ്യമാകും.")

elif option == "📸 Family Gallery":
    st.header("🖼️ ഓർമ്മകൾ")
    st.write("നിന്റെ കുടുംബത്തിലെ പ്രധാന ഫോട്ടോകൾ ഇവിടെ ഗാലറിയായി കാണാം.")

st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
