import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
from PIL import Image
import easyocr
import numpy as np
import re

# ലേറ്റസ്റ്റ് കോഡ് ഇവിടെ നൽകുന്നു
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en'])

reader = get_ocr_reader()

# --- മറ്റ് കോഡുകൾക്ക് ശേഷം Scan Bill ഭാഗത്ത് ഇത് ചേർക്കുക ---
if "Scan Bill" in st.session_state.page:
    st.title("📸 Scan Bill")
    file = st.file_uploader("Upload Bill", type=['jpg','png','jpeg'])
    if file:
        img = Image.open(file)
        st.image(img, width=300)
        with st.spinner('Reading Bill...'):
            img_array = np.array(img)
            res_ocr = reader.readtext(img_array, detail=0)
            full_text = " ".join(res_ocr)
            
            # തുക കണ്ടെത്താനുള്ള ലോജിക്
            amounts = re.findall(r'(?:₹|Rs|Total|Paid)\s*[:]*\s*([\d,]+\.?\d*)', full_text, re.IGNORECASE)
            suggested_am = 0.0
            if amounts:
                # ട്രാൻസാക്ഷൻ ഐഡി പോലുള്ള വലിയ നമ്പറുകൾ ഒഴിവാക്കാൻ
                valid_nums = [float(a.replace(',', '')) for a in amounts if float(a.replace(',', '')) < 100000]
                if valid_nums: suggested_am = max(valid_nums)
            
            # പേര് കണ്ടെത്താൻ
            suggested_it = "Bill Entry"
            for k, text in enumerate(res_ocr):
                if any(x in text for x in ["To", "Paid to"]):
                    if k + 1 < len(res_ocr): suggested_it = res_ocr[k+1]; break

        with st.form("ocr_save"):
            it = st.text_input("Item Name", value=suggested_it)
            am = st.number_input("Amount", value=float(suggested_am))
            if st.form_submit_button("CONFIRM & SAVE"):
                # സേവ് ചെയ്യാനുള്ള ലിങ്ക് ഇവിടെ നൽകുക
                st.success("Successfully Saved! ✅")
