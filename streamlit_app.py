import streamlit as st
import yt_dlp
import ffmpeg
import os

# പേജ് കോൺഫിഗറേഷൻ
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

# 2. മെയിൻ ആപ്പ് ഇന്റർഫേസ്
st.title("🎬 ഓൾ-ഇൻ-വൺ വീഡിയോ പ്രോസസ്സിംഗ് ഹബ്ബ്")
menu = ["📥 ഡൗൺലോഡർ", "🔄 കൺവെർട്ടർ", "✂️ ട്രിമ്മർ", "🔗 മെർജർ", "🔊 അഡ്വാൻസ്ഡ്"]
choice = st.sidebar.selectbox("മെനു തിരഞ്ഞെടുക്കുക", menu)

# ഫംഗ്ഷൻ: വീഡിയോ ഡൗൺലോഡ്
def get_video_url(url):
    ydl_opts = {'format': 'best', 'http_headers': {'User-Agent': 'Mozilla/5.0'}}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('url')

# 3. ടാബുകൾ അനുസരിച്ചുള്ള പ്രവർത്തനങ്ങൾ
if choice == "📥 ഡൗൺലോഡർ":
    url = st.text_input("വീഡിയോ ലിങ്ക്:")
    if st.button("Download"):
        try:
            v_url = get_video_url(url)
            st.video(v_url)
            st.success("വീഡിയോ റെഡിയാണ്!")
        except: st.error("വീഡിയോ ഡൗൺലോഡ് പരാജയപ്പെട്ടു!")

elif choice == "🔄 കൺവെർട്ടർ":
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4', 'mkv', 'avi'], key="c")
    fmt = st.selectbox("ഏത് ഫോർമാറ്റിലേക്ക്?", ['mp4', 'avi', 'mov'])
    if file and st.button("Convert"):
        with open("in.mp4", "wb") as f: f.write(file.getbuffer())
        ffmpeg.input("in.mp4").output(f"out.{fmt}").run(overwrite_output=True)
        with open(f"out.{fmt}", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, file_name=f"out.{fmt}")

elif choice == "✂️ ട്രിമ്മർ":
    s = st.number_input("തുടങ്ങേണ്ട സമയം (sec)", value=0)
    d = st.number_input("ദൈർഘ്യം (sec)", value=10)
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="t")
    if file and st.button("Trim"):
        with open("in_trim.mp4", "wb") as f: f.write(file.getbuffer())
        ffmpeg.input("in_trim.mp4", ss=s, t=d).output("trimmed.mp4").run(overwrite_output=True)
        with open("trimmed.mp4", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, "trimmed.mp4")

elif choice == "🔗 മെർജർ":
    files = st.file_uploader("വീഡിയോകൾ അപ്‌ലോഡ്", type=['mp4'], accept_multiple_files=True, key="m")
    if files and st.button("Merge"):
        file_list = []
        for i, f in enumerate(files):
            with open(f"f{i}.mp4", "wb") as wf: wf.write(f.getbuffer())
            file_list.append(ffmpeg.input(f"f{i}.mp4"))
        ffmpeg.concat(*file_list).output("merged.mp4").run(overwrite_output=True)
        with open("merged.mp4", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, "merged.mp4")

elif choice == "🔊 അഡ്വാൻസ്ഡ്":
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="a")
    act = st.selectbox("പ്രവർത്തനം:", ["മ്യൂട്ട് ചെയ്യുക", "വേഗത കൂട്ടുക (2x)"])
    if file and st.button("Apply"):
        with open("adv.mp4", "wb") as f: f.write(file.getbuffer())
        if act == "മ്യൂട്ട് ചെയ്യുക": ffmpeg.input("adv.mp4").output("out_adv.mp4", an=None).run(overwrite_output=True)
        else: ffmpeg.input("adv.mp4").output("out_adv.mp4", filter_complex="setpts=0.5*PTS").run(overwrite_output=True)
        with open("out_adv.mp4", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, "output.mp4")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
