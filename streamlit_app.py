import streamlit as st
import yt_dlp
import ffmpeg
import os

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Video Hub", layout="wide")

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

# 2. പ്രധാന മെനു
st.title("🎬 വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്")
menu = ["📥 ഡൗൺലോഡർ", "🔄 കൺവെർട്ടർ", "✂️ വീഡിയോ ട്രിമ്മർ", "ℹ️ മെറ്റാഡാറ്റ"]
choice = st.sidebar.selectbox("മെനു തിരഞ്ഞെടുക്കുക", menu)

# 3. ഫീച്ചറുകൾ
if choice == "📥 ഡൗൺലോഡർ":
    url = st.text_input("YouTube ലിങ്ക്:")
    if st.button("Download"):
        ydl_opts = {'format': 'best', 'http_headers': {'User-Agent': 'Mozilla/5.0'}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            st.video(info.get('url'))

elif choice == "🔄 കൺവെർട്ടർ":
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4', 'mkv'], key="conv")
    fmt = st.selectbox("ഫോർമാറ്റ്:", ['mp4', 'avi', 'mov'])
    if file and st.button("Convert"):
        with open("in.mp4", "wb") as f: f.write(file.getbuffer())
        ffmpeg.input("in.mp4").output(f"out.{fmt}").run(overwrite_output=True)
        with open(f"out.{fmt}", "rb") as f:
            st.download_button("ഡൗൺലോഡ്", f, file_name=f"out.{fmt}")

elif choice == "✂️ വീഡിയോ ട്രിമ്മർ":
    start = st.number_input("തുടങ്ങേണ്ട സമയം (sec)", value=0)
    dur = st.number_input("ദൈർഘ്യം (sec)", value=10)
    file_t = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="trim")
    if file_t and st.button("Trim"):
        with open("in_trim.mp4", "wb") as f: f.write(file_t.getbuffer())
        ffmpeg.input("in_trim.mp4", ss=start, t=dur).output("trimmed.mp4").run(overwrite_output=True)
        with open("trimmed.mp4", "rb") as f:
            st.download_button("ഡൗൺലോഡ്", f, file_name="trimmed.mp4")

elif choice == "ℹ️ മെറ്റാഡാറ്റ":
    meta_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="meta")
    if meta_file:
        st.write(f"ഫയൽ നാമം: {meta_file.name}")
        st.write(f"ഫയൽ സൈസ്: {meta_file.size / (1024*1024):.2f} MB")

# ലോഗൗട്ട് ബട്ടൺ
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
