import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import urllib.parse
import os
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD TRADING v8.6", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 💾 PERMANENT FILE MEMORY FUNCTION ---
def get_stored_signal(asset_name):
    filename = f"sig_{asset_name.replace(' ', '_')}.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read().strip()
    return ""

def save_signal_to_file(asset_name, signal_text):
    filename = f"sig_{asset_name.replace(' ', '_')}.txt"
    with open(filename, "w") as f:
        f.write(signal_text)

# --- 3. 🎨 PREMIUM DESIGN ---
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

# --- 4. 🚀 CALLMEBOT ENGINE ---
def send_callmebot_whatsapp(message_text):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message_text)}&apikey={WA_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except:
        return False

# --- 5. 📈 TRIPLE ADVISOR ENGINE WITH TARGET & SL ---
def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            
            # Pivot, Resistance, and Support Calculations
            pivot = (h + l + c) / 3
            r1 = (2 * pivot) - l
            s1 = (2 * pivot) - h
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            # കറൻസി കൺവേർഷൻ ഫോർ ക്രൂഡ് ഓയിൽ
            if name == "Crude Fut": 
                last_p = last_p * 83.5 * 1.15
                pivot = pivot * 83.5 * 1.15
                r1 = r1 * 83.5 * 1.15
                s1 = s1 * 83.5 * 1.15
            
            # Target & SL ലോജിക് സെറ്റ് ചെയ്യുന്നു
            if last_p > pivot and rsi > 55: 
                signal, color, icon = "🚀 BUY", "#00FF00", "🟢"
                target = r1
                stoploss = pivot
            elif last_p < pivot and rsi < 45: 
                signal, color, icon = "📉 SELL", "#FF3131", "🔴"
                target = s1
                stoploss = pivot
            else: 
                signal, color, icon = "⚖️ WAIT", "#FFFF00", "🟡"
                target = last_p
                stoploss = last_p
                
            results.append({
                "name": name, "price": last_p, "signal": signal, 
                "rsi": rsi, "color": color, "icon": icon,
                "target": target, "stoploss": stoploss
            })
        return results
    except:
        return None

# --- 6. MAIN APP ---
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
            else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    st.markdown(f'''<div class="terminal-banner">
        <span style="font-size:24px; color: #FFD700; font-weight:bold;">🚀 PAICHI AUTOMATIC TRADING TERMINAL v8.6</span><br>
        <span style="font-size:14px; color:#E0B0FF;">Welcome, {curr_user.capitalize()} | 🎯 Target & SL Engine Active</span>
    </div>''', unsafe_allow_html=True)

    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    markets = get_triple_advisor()
    
    # --- 🤖 AUTOMATIC ALERT CHECKER WITH TGT & SL ---
    if markets:
        for m in markets:
            asset_name = m["name"]
            current_signal = m["signal"]
            paya_signal = get_stored_signal(asset_name)
            
            if paya_signal != current_signal:
                now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # വാട്സാപ്പ് അലേർട്ടിൽ Target, SL വിവരങ്ങൾ ചേർക്കുന്നു
                tgt_sl_text = ""
                if current_signal != "⚖️ WAIT":
                    tgt_sl_text = f"🎯 *Target:* ₹{m['target']:,.2f}\n🛡️ *Stoploss (SL):* ₹{m['stoploss']:,.2f}\n\n"
                
                auto_msg = (
                    f"{m['icon']} *AUTOMATIC SIGNAL ALERT* {m['icon']}\n\n"
                    f"📦 *Asset:* {asset_name}\n"
                    f"🚦 *New Signal:* {current_signal}\n"
                    f"💰 *Entry Price:* ₹{m['price']:,.2f}\n"
                    f"{tgt_sl_text}"
                    f"📊 *RSI:* {m['rsi']:.2f}\n"
                    f"⏰ *Time:* {now_time}\n\n"
                    f"🤖 _Paichi Target & SL Engine_"
                )
                
                send_callmebot_whatsapp(auto_msg)
                save_signal_to_file(asset_name, current_signal)

    # --- LIVE DISPLAY ---
    st.subheader("Live Market Signals (Target & SL Included)")
    if markets:
        cols = st.columns(3)
        for i, m in enumerate(markets):
            with cols[i]:
                st.markdown(f"""<div class="purple-box" style="border-color: {m['color']} !important;">
                    <h2 style="color:#E0B0FF !important;">{m["name"]}</h2>
                    <h1 style="color:{m["color"]} !important; font-size:48px;">{m["signal"]}</h1>
                    <h1 style="color:#FFD700 !important; font-size:35px;">₹{m["price"]:,.2f}</h1>
                    {"<p style='color:#00FF00 !important; margin:0;'>TGT: ₹"+f"{m['target']:,.2f}"+"</p><p style='color:#FF3131 !important; margin:0;'>SL: ₹"+f"{m['stoploss']:,.2f}"+"</p>" if m["signal"] != "⚖️ WAIT" else ""}
                    <span style="color:#aaa; font-size:12px;">RSI: {m["rsi"]:.2f}</span>
                </div>""", unsafe_allow_html=True)
    else:
        st.warning("Fetching Market Data...")

    st.write("---")
    st.subheader("Manual Backup Controls")
    if markets:
        selected_market = st.selectbox("Select Asset for Manual Alert", [m["name"] for m in markets])
        market_data = next(item for item in markets if item["name"] == selected_market)
        
        if st.button(f"🚀 Force Send {market_data['name']} Signal"):
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tgt_sl_manual = ""
            if market_data['signal'] != "⚖️ WAIT":
                tgt_sl_manual = f"\n🎯 Target: ₹{market_data['target']:,.2f}\n🛡️ SL: ₹{market_data['stoploss']:,.2f}\n"
                
            wa_msg = f"{market_data['icon']} *MANUAL SIGNAL* {market_data['icon']}\n\nAsset: {market_data['name']}\nSignal: {market_data['signal']}\nPrice: ₹{market_data['price']:,.2f}{tgt_sl_manual}\nTime: {now_time}"
            if send_callmebot_whatsapp(wa_msg):
                st.success("Manual Alert Sent! ✅")
