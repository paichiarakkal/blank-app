import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ആപ്പ് പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Expense Tracker 2026", page_icon="💰")
st.title("💰 ഗൂഗിൾ ഷീറ്റ് എക്സ്പെൻസ് ട്രാക്കർ")

# ഗൂഗിൾ ഷീറ്റുമായി കണക്ട് ചെയ്യുന്നു
# (നിന്റെ ഗൂഗിൾ ഷീറ്റിന്റെ ലിങ്ക് താഴെ നൽകുക)
url ="https://docs.google.com/spreadsheets/d/1GTeGR2P15HNmSQCb4Z4l7pCmHd3H-jyqQXtXlOL-5Fg/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ഷീറ്റിലെ നിലവിലുള്ള ഡാറ്റ വായിക്കുന്നു
    existing_data = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3])
    existing_data = existing_data.dropna(how="all")
except Exception as e:
    st.error("ഗൂഗിൾ ഷീറ്റുമായി കണക്ട് ചെയ്യാൻ പറ്റിയില്ല. ലിങ്ക് ശരിയാണോ എന്ന് നോക്കൂ!")
    existing_data = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

# ഇൻപുട്ട് ഫോം
with tf_form := st.form(key="expense_form", clear_on_submit=True):
    st.subheader("പുതിയ ചിലവ് ചേർക്കുക")
    
    date = st.date_input("തീയതി", datetime.now())
    amount = st.number_input("തുക (₹)", min_value=0.0, step=10.0)
    category = st.selectbox("ഇനം (Category)", ["ഭക്ഷണം (Food)", "യാത്ര (Travel)", "ഷോപ്പിംഗ് (Shopping)", "റൂം/വാടക", "മറ്റുള്ളവ"])
    description = st.text_input("വിവരണം (Description)")
    
    submit_button = st.form_submit_button(label="Save to Google Sheet")

# ബട്ടൺ അമർത്തുമ്പോൾ സംഭവിക്കേണ്ടത്
if submit_button:
    if amount > 0 and description:
        # പുതിയ ഡാറ്റ ഒരു റോ (Row) ആയി ഉണ്ടാക്കുന്നു
        new_row = pd.DataFrame([{
            "Date": date.strftime("%Y-%m-%d"),
            "Amount": amount,
            "Category": category,
            "Description": description
        }])
        
        # പഴയ ഡാറ്റയോടൊപ്പം പുതിയതും ചേർക്കുന്നു
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        
        # ഗൂഗിൾ ഷീറ്റിലേക്ക് അപ്ഡേറ്റ് ചെയ്ത് വിടുന്നു
        conn.update(spreadsheet=url, data=updated_df)
        st.success(f"✔️ ₹{amount} ഗൂഗിൾ ഷീറ്റിലേക്ക് മാറ്റി!")
        
        # പേജ് റീഫ്രഷ് ചെയ്യാൻ
        st.rerun()
    else:
        st.error("⚠️ ദയവായി വിവരങ്ങൾ കൃത്യമായി നൽകുക!")

# നിലവിൽ ഷീറ്റിലുള്ള ഡാറ്റ താഴെ കാണിക്കാൻ
st.write("---")
st.subheader("📊 ഗൂഗിൾ ഷീറ്റിലെ വിവരങ്ങൾ")
if not existing_data.empty:
    st.dataframe(existing_data, use_container_width=True)
    
    # ആകെ തുക കണക്കാക്കാൻ
    total = pd.to_numeric(existing_data["Amount"]).sum()
    st.metric(label="ആകെ ചിലവ് (Total)", value=f"₹{total}")
else:
    st.info("ഷീറ്റിൽ നിലവിൽ വിവരങ്ങൾ ഒന്നും തന്നെയില്ല.")
