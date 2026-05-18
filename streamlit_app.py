import streamlit as st
import pandas as pd
from datetime import datetime

# ആപ്പിന്റെ തലക്കെട്ട്
st.set_page_config(page_title="Expense Tracker 2026", page_icon="💰", layout="centered")
st.title("💰 പുതിയ എക്സ്പെൻസ് ട്രാക്കർ")
st.write("നിന്റെ ദിവസേനയുള്ള ചിലവുകൾ കൃത്യമായി ട്രാക്ക് ചെയ്യാം.")

# ഒരു താല്ക്കാലിക ഡാറ്റാബേസ് സെറ്റ് ചെയ്യുന്നു (സെഷൻ സ്റ്റേറ്റ്)
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# ഫോം ഡിസൈൻ
with st.form(key="expense_form", clear_on_submit=True):
    st.subheader("പുതിയ ചിലവ് ചേർക്കുക")
    
    # ഇൻപുട്ടുകൾ
    date = st.date_input("തീയതി (Date)", datetime.now())
    amount = st.number_input("തുക (Amount - ₹)", min_value=0.0, step=10.0)
    category = st.selectbox("ഇനം (Category)", ["ഭക്ഷണം (Food)", "യാത്ര (Travel)", "ഷോപ്പിംഗ് (Shopping)", "റൂം/വാടക", "മറ്റുള്ളവ"])
    description = st.text_input("വിവരണം (Description)")
    
    # സബ്മിറ്റ് ബട്ടൺ
    submit_button = st.form_submit_button(label="Save Expense")

# ബട്ടൺ ഞെക്കുമ്പോൾ സംഭവിക്കേണ്ടത്
if submit_button:
    if amount > 0 and description:
        # ഡാറ്റ ലിസ്റ്റിലേക്ക് ചേർക്കുന്നു
        new_data = {
            "Date": date.strftime("%Y-%m-%d"),
            "Amount": amount,
            "Category": category,
            "Description": description
        }
        st.session_state.expenses.append(new_data)
        st.success(f"✔️ ₹{amount} വിജയകരമായി ചേർത്തു!")
    else:
        st.error("⚠️ ദയവായി തുകയും വിവരങ്ങളും കൃത്യമായി ടൈപ്പ് ചെയ്യുക!")

# ചേർത്ത ചിലവുകൾ താഴെ ഒരു ടേബിൾ ആയി കാണിക്കാൻ
if st.session_state.expenses:
    st.write("---")
    st.subheader("📋 ചേർത്ത ചിലവുകളുടെ ലിസ്റ്റ്")
    df = pd.DataFrame(st.session_state.expenses)
    st.dataframe(df, use_container_width=True)
    
    # ആകെ ചിലവായ തുക കണക്കാക്കാൻ
    total = df["Amount"].sum()
    st.metric(label="ആകെ ചിലവ് (Total Expense)", value=f"₹{total}")
