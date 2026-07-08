import streamlit as st
import yt_dlp
import ffmpeg
import os

st.set_page_config(page_title="Video Hub", layout="wide")

# ലോഗിൻ സിസ്റ്റം
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 ലോഗിൻ ചെയ്യുക")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        # ഇവിടെ നിങ്ങളുടെ യൂസർനെയിമും പാസ്‌വേഡും നൽകുക
        if user == "Faisal" and pwd == "12345": 
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("തെറ്റായ വിവരങ്ങൾ!")
    st.stop()

# പ്രധാന ആപ്പ് ഭാഗം
st.title("🎬 വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്")
tab1, tab2, tab3, tab4 = st.tabs(["📥 ഡൗൺലോഡർ", "🔄 കൺവെർട്ടർ", "✂️ എഡിറ്റർ", "ℹ️ മെറ്റാഡാറ്റ"])

# 1. ഡൗൺലോഡർ
with tab1:
    url = st.text_input("YouTube ലിങ്ക് നൽകുക:")
    if st.button("Download 720p"):
        if url:
            try:
                ydl_opts = {
                    'format': 'best[height<=720][ext=mp4]',
                    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    st.video(info.get('url'))
            except Exception as e: st.error(e)

# 2. കൺവെർട്ടർ
with tab2:
    # key ഉപയോഗിച്ചത് Duplicate ID എറർ ഒഴിവാക്കാൻ
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4', 'mkv'], key="conv")
    fmt = st.selectbox("ഏത് ഫോർമാറ്റിലേക്ക്?", ['mp4', 'avi', 'mov'])
    if file and st.button("കൺവെർട്ട് ചെയ്യുക"):
        with open("in.mp4", "wb") as f: f.write(file.getbuffer())
        ffmpeg.input("in.mp4").output(f"out.{fmt}", vcodec='libx264').run(overwrite_output=True)
        with open(f"out.{fmt}", "rb") as f:
            st.download_button("ഡൗൺലോഡ്", f, file_name=f"out.{fmt}")

# 3. എഡിറ്റർ
with tab3:
    start = st.number_input("തുടങ്ങേണ്ട സമയം (സെക്കൻഡ്)", value=0)
    dur = st.number_input("ദൈർഘ്യം (സെക്കൻഡ്)", value=10)
    file_t = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="trim")
    if file_t and st.button("ട്രിം ചെയ്യുക"):
        with open("in_trim.mp4", "wb") as f: f.write(file_t.getbuffer())
        ffmpeg.input("in_trim.mp4", ss=start, t=dur).output("trimmed.mp4").run(overwrite_output=True)
        with open("trimmed.mp4", "rb") as f:
            st.download_button("ട്രിം ചെയ്ത വീഡിയോ ഡൗൺലോഡ്", f, file_name="trimmed.mp4")

# 4. മെറ്റാഡാറ്റ
with tab4:
    meta_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="meta")
    if meta_file:
        st.write(f"ഫയൽ നാമം: {meta_file.name}")
        st.write(f"ഫയൽ സൈസ്: {meta_file.size / (1024*1024):.2f} MB")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
