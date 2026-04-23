import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import re
import base64

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI GOLD v4.5", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🔊 BEEP SOUND ENGINE ---
def play_beep():
    """സേവ് ചെയ്യുമ്പോൾ ബീപ്പ് ശബ്ദം കേൾപ്പിക്കാൻ"""
    beep_html = """
        <audio autoplay>
            <source src="https://www.soundjay.com/button/beep-07.wav" type="audio/wav">
        </audio>
    """
    st.markdown(beep_html, unsafe_allow_html=True)

# --- 3. 📊 SMART VOICE ENGINE ---
def process_voice(text):
    if not text: return "Others", 0.0, ""
    raw_text = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw_text)
    amount = float(nums[0]) if nums else 0.0
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "ചായ"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട", "ഡ്രസ്സ്"]): category = "Shop"
    elif any(x in raw_text for x in ["travel", "യാത്ര", "ബസ്"]): category = "Travel"
    return category, amount, clean_desc

# --- 4. APP LOGIC ---
st.title("💰 PAICHI SMART ENTRY")

# ബാലൻസ് ഡിസ്‌പ്ലേ
try:
    df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
    total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
    total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
    balance = total_in - total_out
    st.markdown(f"### Current Balance: ₹{balance:,.2f}")
except:
    st.write("Loading Balance...")

# വോയ്‌സ് ഇൻപുട്ട്
v_raw = speech_to_text(language='ml', key='voice_beep_v1')
v_cat, v_amt, v_desc = process_voice(v_raw)

if v_raw: st.info(f"Detected: {v_cat} | Amount: {v_amt}")

with st.form("entry_form", clear_on_submit=True):
    it = st.text_input("Item Description", value=v_desc if v_desc else "")
    am = st.number_input("Amount", min_value=0.0, value=v_amt)
    cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
    cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
    ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
    
    if st.form_submit_button("SAVE DATA"):
        if it and am > 0:
            d, c = (am, 0) if ty == "Debit" else (0, am)
            # ഗൂഗിൾ ഫോം വഴി സേവ് ചെയ്യുന്നു
            requests.post(FORM_API, data={
                "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                "entry.2013476337": f"{cat}: {it}",
                "entry.1460982454": d,
                "entry.1221658767": c
            })
            
            # നോട്ടിഫിക്കേഷൻ സൗണ്ട് പ്ലേ ചെയ്യുന്നു
            play_beep()
            st.success("Saved with Sound! ✅")
            st.rerun()
