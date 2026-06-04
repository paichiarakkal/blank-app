import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import urllib.parse
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD TRADING v8.0", layout="wide")
# 1 മിനിറ്റിൽ ആപ്പ് ഓട്ടോമാറ്റിക് ആയി റിഫ്രഷ് ആയി ലൈവ് വിലകൾ അപ്‌ഡേറ്റ് ചെയ്യും
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DARK & PURPLE DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; height: 50px; font-size: 18px; }
    .terminal-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 🚀 CALLMEBOT WHATSAPP ENGINE ---
def send_callmebot_whatsapp(message_text):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message_text)}&apikey={WA_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except:
        return False

# --- 4. 📈 TRIPLE ADVISOR ENGINE (YAHOO FINANCE) ---
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
            
            # സൂപ്പർട്രെൻഡ് & RSI ലോജിക്
            if last_p > pivot and rsi > 55: signal, color, icon = "🚀 BUY", "#00FF00", "🟢"
            elif last_p < pivot and rsi < 45: signal, color, icon = "📉 SELL", "#FF3131", "🔴"
            else: signal, color, icon = "⚖️ WAIT", "#FFFF00", "🟡"
            
            # ക്രൂഡ് ഓയിൽ കറൻസി കൺവേർഷൻ ഇന്ത്യൻ രൂപയിലേക്ക്
            if name == "Crude Fut": 
                last_p = last_p * 83.5 * 1.15
                
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": rsi, "color": color, "icon": icon})
        return results
    except:
        return None

# --- 5. APP MAIN APP ---
if not st.session_state.auth:
    st.markdown('<div style="text-align:center; padding-top:50px;"><h1>🔐 PAICHI TRADING BOT LOGIN</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN TO TERMINAL"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: 
                st.error("Access Denied! Wrong Credentials.")
else:
    curr_user = st.session_state.user
    
    st.markdown(f'''<div class="terminal-banner">
        <span style="font-size:24px; color: #FFD700; font-weight:bold;">🚀 PAICHI LIVE TRADING TERMINAL v8.0</span><br>
        <span style="font-size:14px; color:#E0B0FF;">Welcome back, {curr_user.capitalize()} | Market auto-refreshes every 60s</span>
    </div>''', unsafe_allow_html=True)

    # സൈഡ്ബാറിൽ ലോഗ്ഔട്ട് മാത്രം
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- 📊 LIVE TRADING DISPLAY ---
    st.subheader("Live Market Signals & Pivot Advisor")
    markets = get_triple_advisor()
    
    if markets:
        # മൂന്ന് മാർക്കറ്റുകൾക്കും വേണ്ടി മൂന്ന് കോളങ്ങൾ
        cols = st.columns(3)
        for i, m in enumerate(markets):
            with cols[i]:
                st.markdown(f"""<div class="purple-box" style="border-color: {m['color']} !important;">
                    <h2 style="color:#E0B0FF !important; margin-bottom:5px;">{m["name"]}</h2>
                    <h1 style="color:{m["color"]} !important; font-size:48px; margin:10px 0;">{m["signal"]}</h1>
                    <h1 style="color:#FFD700 !important; font-size:38px; margin-bottom:5px;">₹{m["price"]:,.2f}</h1>
                    <span style="color:#aaa; font-size:14px;">RSI (14): {m["rsi"]:.2f}</span>
                </div>""", unsafe_allow_html=True)
    else:
        st.warning("Fetching Live Market Data... Please wait.")

    st.write("---")
    
    # --- 📲 MANUAL WHATSAPP ALERTS ---
    st.subheader("Send Signal Manually To WhatsApp")
    
    if markets:
        # വാട്സാപ്പിലേക്ക് അയക്കേണ്ട ഇൻസ്ട്രുമെന്റ് സെലക്ട് ചെയ്യാം
        selected_market = st.selectbox("Select Asset to Send Alert", [m["name"] for m in markets])
        
        # സെലക്ട് ചെയ്ത അസ്സറ്റിന്റെ ഡാറ്റ എടുക്കുന്നു
        market_data = next(item for item in markets if item["name"] == selected_market)
        
        if st.button(f"🚀 Send {market_data['name']} Signal to WhatsApp"):
            with st.spinner("CallMeBot വഴി വാട്സാപ്പിലേക്ക് അലേർട്ട് അയക്കുന്നു..."):
                now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # ഭംഗിയുള്ള വാട്സാപ്പ് മെസ്സേജ് ഫോർമാറ്റ്
                wa_msg = (
                    f"{market_data['icon']} *NEW TRADING SIGNAL* {market_data['icon']}\n\n"
                    f"📦 *Asset:* {market_data['name']}\n"
                    f"🚦 *Signal:* {market_data['signal']}\n"
                    f"💰 *Live Price:* ₹{market_data['price']:,.2f}\n"
                    f"📊 *RSI:* {market_data['rsi']:.2f}\n"
                    f"⏰ *Time:* {now_time}\n\n"
                    f"👤 *Sent By:* Paichi Bot ({curr_user.capitalize()})"
                )
                
                success = send_callmebot_whatsapp(wa_msg)
                if success:
                    st.success(f"✅ {market_data['name']} സിഗ്നൽ വിജയകരമായി നിങ്ങളുടെ വാട്സാപ്പിലേക്ക് അയച്ചിട്ടുണ്ട് ഭായ്!")
                else:
                    st.error("❌ മെസ്സേജ് അയക്കാൻ പറ്റിയില്ല. CallMeBot API കീ ഒന്നുകൂടി ചെക്ക് ചെയ്യൂ.")
