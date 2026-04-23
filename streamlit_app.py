import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import time # സമയം നിയന്ത്രിക്കാൻ ഇത് ആവശ്യമാണ്

# --- CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# --- WHATSAPP NOTIFY ---
def send_wa_notify(item, amount, balance):
    api_key = "7463030" 
    phone = "971551347989"
    msg = f"📝 *Item:* {item}\n💰 *Amount:* {amount}\n\n💳 *Total Balance:* ₹{balance:,.2f}"
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(msg)}&apikey={api_key}"
    try: requests.get(url)
    except: pass

# --- GET BALANCE ---
def get_total_balance():
    try:
        # Cache ഒഴിവാക്കാൻ ഒരു റാൻഡം നമ്പർ കൂടി ചേർക്കുന്നു
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except: return 0.0

# --- ADD ENTRY PAGE LOGIC ---
# (മറ്റ് കോഡുകൾക്ക് ശേഷം Add Entry ഭാഗത്ത് ഈ മാറ്റം വരുത്തുക)

if st.form_submit_button("SAVE DATA"):
    if it and am > 0:
        d, c = (am, 0) if ty == "Debit" else (0, am)
        full_desc = f"[{st.session_state.user.capitalize()}] {cat}: {it}"
        
        # 1. ഡാറ്റ അയക്കുന്നു
        requests.post(FORM_API, data={
            "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
            "entry.2013476337": full_desc, 
            "entry.1460982454": d, 
            "entry.1221658767": c
        })
        
        # 2. ഗൂഗിൾ ഷീറ്റ് അപ്ഡേറ്റ് ആകാൻ 2 സെക്കൻഡ് കാത്തുനിൽക്കുന്നു
        with st.spinner('Updating Balance...'):
            time.sleep(2) 
        
        # 3. പുതിയ ബാലൻസ് എടുക്കുന്നു
        new_balance = get_total_balance()
        
        # 4. വാട്സാപ്പിൽ അയക്കുന്നു
        send_wa_notify(it, am, new_balance)
        
        st.success(f"Saved! Updated Balance: ₹{new_balance:,.2f} ✅")
        st.rerun()
