import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI GOLD v4.6", layout="wide")

# --- 2. SMART VOICE LOGIC ---
def process_voice(text):
    if not text: return "Others", 0.0, ""
    raw_text = text.lower().replace('.', '').replace(',', '')
    
    # നമ്പറുകൾ കണ്ടെത്തുന്നു
    nums = re.findall(r'\d+', raw_text)
    amount = float(nums[0]) if nums else 0.0
    
    # ഡിസ്ക്രിപ്ഷനിൽ നിന്ന് നമ്പറുകൾ മാറ്റുന്നു (ഉദാ: ചായ 10 -> ചായ)
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    
    # കാറ്റഗറി മാപ്പിംഗ്
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "ചായ"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട", "dress"]): category = "Shop"
    
    return category, amount, clean_desc

# --- 3. APP UI ---
st.title("💰 PAICHI SMART ENTRY")

# ബാലൻസ് ഡിസ്‌പ്ലേ
try:
    df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
    total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
    total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
    st.metric("Current Balance", f"₹{total_in - total_out:,.2f}")
except:
    st.write("Loading Balance...")

# വോയ്‌സ് ഇൻപുട്ട്
v_raw = speech_to_text(language='ml', key='voice_v4_6')
v_cat, v_amt, v_desc = process_voice(v_raw)

if v_raw:
    st.info(f"തിരിച്ചറിഞ്ഞത്: {v_desc} - ₹{v_amt}")

with st.form("entry_form", clear_on_submit=True):
    it = st.text_input("Item Description", value=v_desc if v_desc else "")
    am = st.number_input("Amount", min_value=0.0, value=v_amt)
    cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
    cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
    ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
    
    if st.form_submit_button("SAVE DATA"):
        if it and am > 0:
            d, c = (am, 0) if ty == "Debit" else (0, am)
            requests.post(FORM_API, data={
                "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                "entry.2013476337": f"{cat}: {it}",
                "entry.1460982454": d,
                "entry.1221658767": c
            })
            
            # 🔔 ഇവിടെയാണ് സ്പെഷ്യൽ നോട്ടിഫിക്കേഷൻ
            st.toast(f'✅ {it} saved successfully!', icon='💰')
            st.success(f"സേവ് ആയിട്ടുണ്ട്: {it} - ₹{am}")
            st.rerun()
