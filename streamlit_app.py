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
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("തെറ്റായ വിവരങ്ങൾ!")
    st.stop()

# പ്രധാന ആപ്പ് ഭാഗം
st.title("🎬 വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്")
tab1, tab2, tab3, tab4 = st.tabs(["📥 ഡൗൺലോഡർ", "🔄 കൺവെർട്ടർ", "✂️ എഡിറ്റർ (ട്രിമ്മിംഗ്)", "ℹ️ മെറ്റാഡാറ്റ"])

# 1. ഡൗൺലോഡർ
with tab1:
    url = st.text_input("YouTube ലിങ്ക്:")
    if st.button("Download 720p"):
        try:
            with yt_dlp.YoutubeDL({'format': 'best[height<=720]'}) as ydl:
                info = ydl.extract_info(url, download=False)
                st.video(info.get('url'))
        except Exception as e: st.error(e)

# 2. കൺവെർട്ടർ
with tab2:
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4', 'mkv'])
    fmt = st.selectbox("ഏത് ഫോർമാറ്റിലേക്ക്?", ['mp4', 'avi', 'mov'])
    if file and st.button("കൺവെർട്ട്"):
        with open("in.mp4", "wb") as f: f.write(file.getbuffer())
        ffmpeg.input("in.mp4").output(f"out.{fmt}").run(overwrite_output=True)
        st.download_button("ഡൗൺലോഡ്", open(f"out.{fmt}", "rb"), file_name=f"out.{fmt}")

# 3. എഡിറ്റർ (ട്രിമ്മിംഗ്)
with tab3:
    st.write("വീഡിയോ ട്രിം ചെയ്യാൻ സമയം (സെക്കൻഡിൽ) നൽകുക:")
    start = st.number_input("തുടങ്ങേണ്ട സമയം", value=0)
    duration = st.number_input("ദൈർഘ്യം", value=10)
    file_t = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'])
    if file_t and st.button("ട്രിം ചെയ്യുക"):
        with open("in_trim.mp4", "wb") as f: f.write(file_t.getbuffer())
        ffmpeg.input("in_trim.mp4", ss=start, t=duration).output("trimmed.mp4").run(overwrite_output=True)
        st.download_button("ട്രിം ചെയ്ത വീഡിയോ ഡൗൺലോഡ്", open("trimmed.mp4", "rb"), file_name="trimmed.mp4")

# 4. മെറ്റാഡാറ്റ
with tab4:
    meta_file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'])
    if meta_file:
        st.write(f"ഫയൽ നാമം: {meta_file.name}")
        st.write(f"ഫയൽ സൈസ്: {meta_file.size / (1024*1024):.2f} MB")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
