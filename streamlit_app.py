import streamlit as st
import yt_dlp
import ffmpeg
import os

# ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Video Pro Hub", layout="wide")

# 1. ലോഗിൻ സിസ്റ്റം
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 ലോഗിൻ ചെയ്യുക")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Faisal" and pwd == "12345": 
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("തെറ്റായ വിവരങ്ങൾ!")
    st.stop()

# 2. മെയിൻ ആപ്പ്
st.title("🎬 ഓൾ-ഇൻ-വൺ വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്")
tab1, tab2, tab3, tab4 = st.tabs(["📥 ഡൗൺലോഡർ", "🔄 കൺവെർട്ടർ", "✂️ എഡിറ്റർ", "ℹ️ വിവരങ്ങൾ"])

# ഡൗൺലോഡർ
with tab1:
    url = st.text_input("YouTube ലിങ്ക് നൽകുക:")
    if st.button("Download"):
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'http_headers': {'User-Agent': 'Mozilla/5.0'}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            st.video(info.get('url'))

# കൺവെർട്ടർ
with tab2:
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="c1")
    fmt = st.selectbox("ഏത് ഫോർമാറ്റിലേക്ക്?", ['mp4', 'avi', 'mov'])
    if file and st.button("Convert"):
        with open("in.mp4", "wb") as f: f.write(file.getbuffer())
        ffmpeg.input("in.mp4").output(f"out.{fmt}").run(overwrite_output=True)
        with open(f"out.{fmt}", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, file_name=f"out.{fmt}")

# എഡിറ്റർ (ട്രിമ്മർ)
with tab3:
    start = st.number_input("തുടങ്ങേണ്ട സമയം (sec)", value=0)
    dur = st.number_input("ദൈർഘ്യം (sec)", value=10)
    file_t = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="t1")
    if file_t and st.button("Trim"):
        with open("in_trim.mp4", "wb") as f: f.write(file_t.getbuffer())
        ffmpeg.input("in_trim.mp4", ss=start, t=dur).output("trimmed.mp4").run(overwrite_output=True)
        with open("trimmed.mp4", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, file_name="trimmed.mp4")

# വിവരങ്ങൾ (മെറ്റാഡാറ്റ)
with tab4:
    meta_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="m1")
    if meta_file:
        st.write(f"ഫയൽ നാമം: {meta_file.name}")
        st.write(f"ഫയൽ സൈസ്: {meta_file.size / (1024*1024):.2f} MB")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
