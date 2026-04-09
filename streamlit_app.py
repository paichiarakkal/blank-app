import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .stMetric { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 15px; border: 2px solid #000; }
    .ai-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #FFD700; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=15000, key="paichi_ai_v10")

# --- AI പ്രെഡിക്ഷൻ ഫംഗ്ഷൻ ---
def get_ai_prediction(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        current_price = data['meta']['regularMarketPrice']
        
        # അവസാന 10 മിനിറ്റിലെ വില എടുക്കുന്നു
        close_prices = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        if len(close_prices) > 10:
            y = np.array(close_prices[-10:]).reshape(-1, 1)
            x = np.arange(10).reshape(-1, 1)
            model = LinearRegression().fit(x, y)
            next_price = model.predict([[10]])[0][0]
            return round(current_price, 2), round(next_price, 2), close_prices[-20:]
        return current_price, current_price, close_prices
    except: return None, None, []

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    mode = st.radio("മെനു:", ["📈 AI MARKET", "📝 JOURNAL"])

st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "📈 AI MARKET":
    asset = st.selectbox("Select Asset", ["CL=F", "^NSEI", "^NSEBANK"], 
                         format_func=lambda x: "CRUDE OIL" if x=="CL=F" else ("NIFTY 50" if x=="^NSEI" else "BANK NIFTY"))
    
    curr, pred, history = get_ai_prediction(asset)
    
    if curr:
        multi = 93.5 if asset=="CL=F" else 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("നിലവിലെ വില", f"₹{curr*multi:.2f}")
        
        with col2:
            diff = (pred - curr) * multi
            st.metric("AI പ്രവചനം (Next)", f"₹{pred*multi:.2f}", delta=f"{diff:.2f}")

        # AI ചാർട്ട്
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[p*multi for p in history], mode='lines', name='Actual', line=dict(color='black', width=3)))
        fig.add_trace(go.Scatter(x=[len(history)], y=[pred*multi], mode='markers', name='AI Target', marker=dict(color='red', size=12)))
        
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # AI സിഗ്നൽ ബോക്സ്
        if pred > curr:
            st.markdown('<div class="ai-box"><h3>🚀 AI SIGNAL: BULLISH (BUY)</h3><p>അടുത്ത മിനിറ്റുകളിൽ വില കൂടാൻ സാധ്യതയുണ്ട്.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ai-box"><h3>📉 AI SIGNAL: BEARISH (SELL)</h3><p>അടുത്ത മിനിറ്റുകളിൽ വില കുറയാൻ സാധ്യതയുണ്ട്.</p></div>', unsafe_allow_html=True)

st.sidebar.write("Created with ❤️ by Faisal")
