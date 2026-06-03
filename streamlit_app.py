import streamlit as st
import pandas as pd
from twilio.rest import Client
import requests
import datetime

# ==========================================
# 1. PAGE SETUP & SECURITY
# ==========================================
st.set_page_config(page_title="Paichi Trading Bot", layout="wide")
st.title("📊 Paichi Live Trading Dashboard")

# ⚠️ നിങ്ങളുടെ ഒറിജിനൽ കീകൾ ഇവിടെ സുരക്ഷിതമായി കൊടുക്കുക
UPSTOX_API_KEY = "7d6580c0-40a7-41fc-9eed-019c9424f6c0"
UPSTOX_ACCESS_TOKEN = "12ixcu1q9i"

TWILIO_SID = "YOUR_TWILIO_ACCOUNT_SID"  # നിങ്ങളുടെ Twilio SID ഇവിടെ നൽകുക
TWILIO_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"    # നിങ്ങളുടെ Twilio Token ഇവിടെ നൽകുക
YOUR_PHONE = "whatsapp:+91XXXXXXXXXX"     # നിങ്ങളുടെ വാട്സാപ്പ് നമ്പർ (+91 ചേർക്കണം)

# ==========================================
# 2. UPSTOX LIVE DATA FUNCTION (LTP)
# ==========================================
def get_upstox_ltp(instrument_key):
    """Upstox API വഴി ഒരു ഇൻസ്ട്രുമെന്റിന്റെ ലൈവ് വില (LTP) എടുക്കുന്ന ഫങ്ക്ഷൻ"""
    url = f"https://api.upstox.com/v2/market-quote/ltp?instrument_key={instrument_key}"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {UPSTOX_ACCESS_TOKEN}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # ഡാറ്റയിൽ നിന്ന് വില മാത്രം എടുക്കുന്നു
            ltp = data['data'][instrument_key]['last_price']
            return ltp
        else:
            st.error(f"Upstox API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching Upstox data: {e}")
        return None

# ==========================================
# 3. TWILIO WHATSAPP ALERT FUNCTION
# ==========================================
def send_whatsapp_alert(symbol, signal_type, price):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        icon = "🟢" if signal_type == "BUY" else "🔴"
        
        msg = f"{icon} **NEW TRADING SIGNAL** {icon}\n\nAsset: {symbol}\nSignal: {signal_type}\nPrice: {price}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        message = client.messages.create(
            from_='whatsapp:+14155238886', # Twilio Sandbox Number
            body=msg,
            to=YOUR_PHONE
        )
        return True
    except Exception as e:
        st.error(f"Twilio Error: {e}")
        return False

# ==========================================
# 4. DASHBOARD UI & LOGIC
# ==========================================
st.subheader("Live Market Signals (Upstox API)")

# Crude Oil & Nifty-യുടെ Upstox Instrument Keys (ഉദാഹരണത്തിന്)
# (യഥാർത്ഥ കോൺട്രാക്ട് അനുസരിച്ച് ഈ Keys മാറാം ഭായ്)
instruments = {
    "NSE_INDEX|Nifty 50": "NIFTY 50",
    "MCX_FO|CRUDEOIL26JUNFUT": "CRUDE OIL"  # നിലവിലെ ജൂൺ ഫ്യൂച്ചർ കീ
}

live_data = []

# ഓരോ ഇൻസ്ട്രുമെന്റിന്റെയും ലൈവ് വില എടുക്കുന്നു
for key, symbol in instruments.items():
    price = get_upstox_ltp(key)
    
    if price:
        # തൽക്കാലം ഒരു സൂപ്പർട്രെൻഡ് ലോജിക് മാതൃകയ്ക്ക് വേണ്ടി വെക്കുന്നു
        # വില ഒരു നിശ്ചിത ലെവലിന് മുകളിലാണെങ്കിൽ BUY, താഴെയാണെങ്കിൽ SELL
        mock_supertrend = "BUY" if symbol == "NIFTY 50" else "SELL"
        
        live_data.append({
            "Instrument": symbol,
            "Live Price (LTP)": price,
            "Supertrend Status": mock_supertrend
        })

# ഡാറ്റ ഉണ്ടെങ്കിൽ സ്ക്രീനിൽ കാണിക്കും
if live_data:
    df_signals = pd.DataFrame(live_data)
    st.dataframe(df_signals, use_container_width=True)

st.write("---")
st.subheader("Manual Controls")

if st.button("🚀 Send Live Signal to WhatsApp"):
    if live_data:
        # Crude Oil സിഗ്നൽ ടെസ്റ്റ് ചെയ്യുന്നു
        crude_symbol = live_data[1]["Instrument"]
        crude_price = live_data[1]["Live Price (LTP)"]
        crude_signal = live_data[1]["Supertrend Status"]
        
        with st.spinner("മെസ്സേജ് അയക്കുന്നു..."):
            success = send_whatsapp_alert(crude_symbol, crude_signal, crude_price)
            if success:
                st.success("Upstox ലൈവ് വില വെച്ചുള്ള വാട്സാപ്പ് മെസ്സേജ് പക്കാ ആയി പോയിട്ടുണ്ട് ഭായ്! ✅")
    else:
        st.warning("Upstox-ൽ നിന്ന് ഡാറ്റ ഒന്നും കിട്ടിയിട്ടില്ല ഭായ്. Access Token കാലാവധി കഴിഞ്ഞതാണോ എന്ന് ചെക്ക് ചെയ്യൂ.")
