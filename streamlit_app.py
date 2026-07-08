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
            st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു...")
            ydl_opts = {
                'format': 'best[height<=720][ext=mp4]/best[ext=mp4]',
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
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
    uploaded_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4', 'mkv', 'avi'])
    format_option = st.selectbox("ഏത് ഫോർമാറ്റിലേക്ക് മാറ്റണം?", ['mp4', 'avi', 'mov'])
    
    if uploaded_file and st.button("കൺവെർട്ട് ചെയ്യുക"):
        input_file = "input_temp.mp4"
        output_file = f"output.{format_option}"
        
        with open(input_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            ffmpeg.input(input_file).output(output_file).run(overwrite_output=True)
            with open(output_file, "rb") as f:
                st.download_button("ഡൗൺലോഡ് ചെയ്യുക", f, file_name=output_file)
            st.success("കൺവേർഷൻ പൂർത്തിയായി!")
            
            # വൃത്തിയാക്കൽ
            if os.path.exists(input_file): os.remove(input_file)
        except Exception as e:
            st.error(f"FFmpeg എറർ: {e}")

# 3. മെറ്റാഡാറ്റ
with tab3:
    st.header("മെറ്റാഡാറ്റ പരിശോധന")
    meta_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4', 'mkv'])
    if meta_file:
        st.write(f"ഫയൽ നാമം: {meta_file.name}")
        st.write(f"ഫയൽ സൈസ്: {meta_file.size / (1024*1024):.2f} MB")
        st.info("വിവരങ്ങൾ വിജയകരമായി ലഭ്യമാക്കി.")
