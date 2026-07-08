import streamlit as st
import yt_dlp
import ffmpeg
import os

# പേജ് കോൺഫിഗറേഷൻ
st.set_page_config(page_title="Video Hub", layout="wide")
st.title("🎬 വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്")

# ടാബുകൾ
tab1, tab2, tab3 = st.tabs(["📥 ഡൗൺലോഡർ", "🔄 കൺവെർട്ടർ", "ℹ️ മെറ്റാഡാറ്റ"])

# 1. വീഡിയോ ഡൗൺലോഡർ
with tab1:
    st.header("വീഡിയോ ഡൗൺലോഡ് ചെയ്യുക")
    url = st.text_input("യൂട്യൂബ് ലിങ്ക് ഇവിടെ നൽകുക:")
    if st.button("Download 720p Video"):
        if url:
            ydl_opts = {
                'format': 'best[height<=720][ext=mp4]/best[ext=mp4]',
                'http_headers': {'User-Agent': 'Mozilla/5.0'}
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_url = info.get('url')
                    st.video(video_url)
                    st.success("വീഡിയോ റെഡി!")
            except Exception as e:
                st.error(f"എറർ: {e}")

# 2. ഫോർമാറ്റ് കൺവെർട്ടർ
with tab2:
    st.header("ഫോർമാറ്റ് മാറ്റുക")
    uploaded_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4', 'mkv'])
    format_option = st.selectbox("ഏത് ഫോർമാറ്റിലേക്ക് മാറ്റണം?", ['mp4', 'avi', 'mov'])
    
    if uploaded_file and st.button("കൺവെർട്ട് ചെയ്യുക"):
        with open("input.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        output_file = f"output.{format_option}"
        try:
            ffmpeg.input("input.mp4").output(output_file).run()
            with open(output_file, "rb") as f:
                st.download_button("ഡൗൺലോഡ് ചെയ്യുക", f, file_name=output_file)
            st.success("കൺവേർഷൻ പൂർത്തിയായി!")
        except Exception as e:
            st.error(f"പിശക്: {e}")

# 3. മെറ്റാഡാറ്റ
with tab3:
    st.header("മെറ്റാഡാറ്റ പരിശോധന")
    meta_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4'])
    if meta_file:
        st.write("ഫയൽ നാമം:", meta_file.name)
        st.write("ഫയൽ സൈസ്:", f"{meta_file.size / 1024:.2f} KB")
        st.info("മെറ്റാഡാറ്റ വിശകലനം പൂർത്തിയായി.")
