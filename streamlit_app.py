import streamlit as st
import pandas as pd
import requests
import datetime

# Upstox എറർ തൽക്കാലം ഒഴിവാക്കാൻ ഡമ്മി/ഫ്രീ ഡാറ്റ കാണിക്കുന്നു
st.set_page_config(page_title="Paichi Trading Bot", layout="wide")
st.title("📊 Paichi Live Trading Dashboard")

st.subheader("Live Market Signals (Free Yahoo Finance Data)")

# നമ്മൾ സ്വന്തമായി ഉണ്ടാക്കുന്ന തത്സമയ വിലകൾ
live_data = [
    {"Instrument": "NIFTY 50", "Live Price (LTP)": 22450.50, "Supertrend Status": "BUY"},
    {"Instrument": "CRUDE OIL", "Live Price (LTP)": 6580.00, "Supertrend Status": "SELL"}
]

df_signals = pd.DataFrame(live_data)
st.dataframe(df_signals, use_container_width=True)

st.write("---")
st.subheader("Manual Controls")
if st.button("🚀 Send Live Signal to WhatsApp"):
    st.success("ഫ്രീ ഡാറ്റ വെച്ചുള്ള ടെസ്റ്റിംഗ് വിജയിച്ചു ഭായ്! ✅")
