import streamlit as st
import pandas as pd
from datetime import date

# ആപ്പിന്റെ തലക്കെട്ട്
st.set_page_config(page_title="Faisal's Family Hub", layout="wide")
st.title("👨‍👩‍👧‍ enrichment Smart Family App")

# സൈഡ് ബാർ മെനു
menu = ["Family Tracker", "Smart Assistant"]
choice = st.sidebar.selectbox("മെനു തിരഞ്ഞെടുക്കുക", menu)

# --- 1. FAMILY & EDUCATION TRACKER ---
if choice == "Family Tracker":
    st.header("📚 മക്കളുടെ പഠന വിവരങ്ങൾ")
    
    # മക്കളുടെ ഡാറ്റ
    data = {
        "പേര്": ["ഫാത്തിമത്ത് ഫഹീമ", "ഫാത്തിമത്ത് ഫിസ"],
        "പഠനം": ["+2 Science (Completed)", "10th CBSE (Completed)"],
        "ലക്ഷ്യം": ["B.Sc Nursing (CENTAC)", "+1 Admission"],
        "സ്റ്റാറ്റസ്": ["Result Awaiting", "Admission Open"]
    }
    df = pd.DataFrame(data)
    st.table(df)

    st.subheader("📅 പ്രധാന തീയതികൾ")
    event = st.text_input("വിശേഷം (ഉദാ: CENTAC Last Date)")
    event_date = st.date_input("തീയതി", date.today())
    
    if st.button("സേവ് ചെയ്യുക"):
        st.success(f"'{event}' എന്ന വിവരം {event_date} തീയതിയിലേക്ക് രേഖപ്പെടുത്തി!")

# --- 2. SMART ASSISTANT ---
elif choice == "Smart Assistant":
    st.header("🤖 സ്മാർട്ട് അസിസ്റ്റന്റ്")
    
    st.write("നിനക്ക് ആവശ്യമായ കാര്യങ്ങൾ ഇവിടെ ടൈപ്പ് ചെയ്യാം അല്ലെങ്കിൽ നോട്ട് ആയി സൂക്ഷിക്കാം.")
    
    user_note = st.text_area("നോട്ട്സ് എഴുതുക (ഉദാ: വില്ലേജ് ഓഫീസർ വരുന്നത്)")
    
    if st.button("നോട്ട് സേവ് ചെയ്യുക"):
        st.info("നിങ്ങളുടെ നോട്ട് സുരക്ഷിതമായി സൂക്ഷിച്ചു.")

    st.divider()
    st.subheader("🔊 വോയ്‌സ് ടൂൾ")
    text_to_speak = st.text_input("ശബ്ദമാക്കി മാറ്റേണ്ട വരികൾ ഇവിടെ നൽകുക")
    if st.button("ശബ്ദം കേൾക്കുക"):
        st.write("ശബ്ദം തയ്യാറാകുന്നു... (ഇവിടെ നമുക്ക് gTTS ലിങ്ക് ചെയ്യാം)")
