import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re
import urllib.parse

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# 🟢 നിന്റെ വാട്സാപ്പ് നമ്പർ ഇവിടെ നൽകുക (91 ചേർത്ത്)
MY_PHONE = "918714752210" 

st.set_page_config(page_title="PAICHI GOLD v4.8", layout="wide")

# --- 2. SMART VOICE LOGIC ---
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

# --- 3. APP UI ---
st.title("💰 PAICHI SMART ENTRY")

# വോയ്‌സ് ഇൻപുട്ട്
v_raw = speech_to_text(language='ml', key='voice_v4_8')
v_cat, v_amt, v_desc = process_voice(v_raw)

with st.form("entry_form", clear_on_submit=True):
    it = st.text_input("Item Description", value=v_desc if v_desc else "")
    am = st.number_input("Amount", min_value=0.0, value=v_amt)
    cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
    cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
    ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
    
    if st.form_submit_button("SAVE & NOTIFY"):
        if it and am > 0:
            # 1. ഗൂഗിൾ ഫോമിലേക്ക് സേവ് ചെയ്യുന്നു
            d, c = (am, 0) if ty == "Debit" else (0, am)
            requests.post(FORM_API, data={
                "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                "entry.2013476337": f"{cat}: {it}",
                "entry.1460982454": d,
                "entry.1221658767": c
            })

            # 2. വാട്സാപ്പ് മെസ്സേജ് തയ്യാറാക്കുന്നു
            msg = f"✅ *Paichi Entry Saved!*\n\n📝 Item: {it}\n💰 Amount: ₹{am}\n📂 Category: {cat}\n📊 Type: {ty}\n📅 Date: {datetime.now().strftime('%d-%m-%Y')}"
            encoded_msg = urllib.parse.quote(msg)
            wa_url = f"https://wa.me/{MY_PHONE}?text={encoded_msg}"

            # 3. വാട്സാപ്പ് ഓപ്പൺ ചെയ്യാനുള്ള ബട്ടൺ കാണിക്കുന്നു
            st.success("Data Saved! Click below to send WhatsApp notification.")
            st.markdown(f'''
                <a href="{wa_url}" target="_blank">
                    <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; font-weight: bold; width: 100%;">
                        🚀 SEND WHATSAPP NOW
                    </button>
                </a>
            ''', unsafe_allow_html=True)
