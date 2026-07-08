import streamlit as st
import yt_dlp
import ffmpeg
import os

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 ഡൗൺലോഡർ", "🔄 കൺവെർട്ടർ", "✂️ ട്രിമ്മർ", "🔗 മെർജിംഗ്", "🔊 അഡ്വാൻസ്ഡ്"])

with tab1: # ഡൗൺലോഡർ
    url = st.text_input("YouTube ലിങ്ക്:")
    if st.button("Download"):
        with yt_dlp.YoutubeDL({'format': 'best', 'http_headers': {'User-Agent': 'Mozilla/5.0'}}) as ydl:
            info = ydl.extract_info(url, download=False)
            st.video(info.get('url'))

with tab2: # കൺവെർട്ടർ
    file = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="c1")
    fmt = st.selectbox("ഫോർമാറ്റ്:", ['mp4', 'avi', 'mov'])
    if file and st.button("Convert"):
        with open("in.mp4", "wb") as f: f.write(file.getbuffer())
        ffmpeg.input("in.mp4").output(f"out.{fmt}").run(overwrite_output=True)
        with open(f"out.{fmt}", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, file_name=f"out.{fmt}")

with tab3: # ട്രിമ്മർ
    start = st.number_input("തുടങ്ങേണ്ട സമയം (sec)", value=0)
    dur = st.number_input("ദൈർഘ്യം (sec)", value=10)
    file_t = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="t1")
    if file_t and st.button("Trim"):
        with open("in_trim.mp4", "wb") as f: f.write(file_t.getbuffer())
        ffmpeg.input("in_trim.mp4", ss=start, t=dur).output("trimmed.mp4").run(overwrite_output=True)
        with open("trimmed.mp4", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, file_name="trimmed.mp4")

with tab4: # മെർജിംഗ്
    files = st.file_uploader("വീഡിയോകൾ അപ്‌ലോഡ് ചെയ്യുക", type=['mp4'], accept_multiple_files=True, key="m1")
    if files and st.button("Merge Now"):
        file_list = []
        for i, f in enumerate(files):
            with open(f"f{i}.mp4", "wb") as wf: wf.write(f.getbuffer())
            file_list.append(ffmpeg.input(f"f{i}.mp4"))
        ffmpeg.concat(*file_list).output("merged.mp4").run(overwrite_output=True)
        with open("merged.mp4", "rb") as f: st.download_button("ഡൗൺലോഡ് മെർജ് ചെയ്ത വീഡിയോ", f, "merged.mp4")

with tab5: # മ്യൂട്ട് & സ്പീഡ്
    file_a = st.file_uploader("വീഡിയോ അപ്‌ലോഡ്", type=['mp4'], key="a1")
    act = st.selectbox("ഓപ്ഷൻ:", ["മ്യൂട്ട് ചെയ്യുക", "വേഗത കൂട്ടുക (2x)"])
    if file_a and st.button("Apply"):
        with open("adv.mp4", "wb") as f: f.write(file_a.getbuffer())
        if act == "മ്യൂട്ട് ചെയ്യുക":
            ffmpeg.input("adv.mp4").output("out_adv.mp4", an=None).run(overwrite_output=True)
        else:
            ffmpeg.input("adv.mp4").output("out_adv.mp4", filter_complex="setpts=0.5*PTS").run(overwrite_output=True)
        with open("out_adv.mp4", "rb") as f: st.download_button("ഡൗൺലോഡ്", f, "output.mp4")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
