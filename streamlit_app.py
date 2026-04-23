import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import time

# --- ഗൂഗിൾ ലിങ്കുകൾ ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# --- ബാലൻസ് എടുക്കാനുള്ള ഫങ്ക്ഷൻ (ഇതാണ് പ്രധാനം) ---
def get_live_balance():
    # ലിങ്കിന്റെ അവസാനം ഒരു റാൻഡം നമ്പർ ചേർക്കുന്നത് വഴി ഗൂഗിൾ എപ്പോഴും പുതിയ ബാലൻസ് തരും
    fresh_url = f"{CSV_URL}&cache_buster={random.randint(1, 999999)}"
    try:
        df = pd.read_csv(fresh_url)
        df.columns = df.columns.str.strip()
        credit = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        debit = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return credit - debit
    except:
        return 0.0

# --- വാട്സാപ്പ് അയക്കാൻ ---
def send_wa(item, amount, balance):
    msg = f"📝 *Item:* {item}\n💰 *Amount:* {amount}\n💳 *Balance:* ₹{balance:,.2f}"
    url = f"https://api.callmebot.com/whatsapp.php?phone=971551347989&text={requests.utils.quote(msg)}&apikey=7463030"
    try: requests.get(url, timeout=10)
    except: pass

# --- ആപ്പ് ഡിസൈൻ ---
st.set_page_config(page_title="PAICHI FINANCE")
st.markdown("<style>.stApp { background: #2D0844; color: white; }</style>", unsafe_allow_html=True)

st.title("💰 Add Entry")

# ലളിതമായ ഫോം
with st.form("my_form", clear_on_submit=True):
    item = st.text_input("Item Name")
    amount = st.number_input("Amount", min_value=0.0)
    type_entry = st.radio("Type", ["Debit", "Credit"], horizontal=True)
    
    if st.form_submit_button("SAVE & UPDATE"):
        if item and amount > 0:
            # 1. സേവ് ചെയ്യുന്നു
            d, c = (amount, 0) if type_entry == "Debit" else (0, amount)
            data = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": item, "entry.1460982454": d, "entry.1221658767": c}
            requests.post(FORM_API, data=data)
            
            # 2. ചെറിയൊരു വെയ്റ്റിംഗ് (ഷീറ്റ് അപ്ഡേറ്റ് ആകാൻ)
            with st.spinner('Updating Balance...'):
                time.sleep(3)
            
            # 3. പുതിയ ബാലൻസ് എടുക്കുന്നു
            current_bal = get_live_balance()
            
            # 4. വാട്സാപ്പ് അയക്കുന്നു
            send_wa(item, amount, current_bal)
            
            st.success(f"സേവ് ആയി! പുതിയ ബാലൻസ്: ₹{current_bal:,.2f}")
            st.rerun()

# ഡാഷ്ബോർഡിൽ ബാലൻസ് കാണിക്കാൻ
st.divider()
balance_now = get_live_balance()
st.metric("കയ്യിലുള്ള തുക", f"₹{balance_now:,.2f}")
