import streamlit as st
import yt_dlp
import ffmpeg
import os

# പേജ് കോൺഫിഗറേഷൻ
st.set_page_config(page_title="വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്", layout="wide")
st.title("🎬 വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്")

tab1, tab2, tab3 = st.tabs(["📥 വീഡിയോ ഡൗൺലോഡർ", "🔄 ഫോർമാറ്റ് കൺവെർട്ടർ", "ℹ️ മെറ്റാഡാറ്റ"])

# 1. വീഡിയോ ഡൗൺലോഡർ
with tab1:
    st.header("വീഡിയോ ഡൗൺലോഡ് ചെയ്യുക")
    url = st.text_input("YouTube ലിങ്ക് ഇവിടെ നൽകുക:")
    if st.button("ഡൗൺലോഡ്"):
        if url:
            try:
                ydl_opts = {'format': 'best'}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                st.success("ഡൗൺലോഡ് പൂർത്തിയായി!")
            except Exception as e:
                st.error(f"പിശക് സംഭവിച്ചു: {e}")

# 2. ഫോർമാറ്റ് കൺവെർട്ടർ
with tab2:
    st.header("ഫോർമാറ്റ് മാറ്റുക")
    uploaded_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4', 'mkv', 'avi'])
    format_option = st.selectbox("ഏത് ഫോർമാറ്റിലേക്ക് മാറ്റണം?", ['mp4', 'avi', 'mov'])
    
    if uploaded_file and st.button("കൺവെർട്ട് ചെയ്യുക"):
        with open("temp_input.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        output_file = f"output.{format_option}"
        try:
            (
                ffmpeg
                .input("temp_input.mp4")
                .output(output_file)
                .run()
            )
            with open(output_file, "rb") as f:
                st.download_button("ഡൗൺലോഡ് ചെയ്ത ഫയൽ", f, file_name=output_file)
        except Exception as e:
            st.error(f"കൺവെർട്ടിംഗിൽ പിശക്: {e}")

# 3. മെറ്റാഡാറ്റ എഡിറ്റർ
with tab3:
    st.header("മെറ്റാഡാറ്റ കാണുക")
    meta_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്ത് മെറ്റാഡാറ്റ കാണാം", type=['mp4'])
    if meta_file:
        st.write("ഫയൽ വിവരങ്ങൾ ലഭ്യമാണ് (Metadata Processing Ready)")
