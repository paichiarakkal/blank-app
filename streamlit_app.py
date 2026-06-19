import streamlit as st
import yt_dlp

st.title("YouTube Video Downloader")

url = st.text_input("YouTube ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download"):
    if url:
        try:
            ydl_opts = {'format': 'best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            st.success("ഡൗൺലോഡ് പൂർത്തിയായി!")
        except Exception as e:
            st.error(f"എന്തോ കുഴപ്പമുണ്ട്: {e}")
    else:
        st.warning("ദയവായി ഒരു ലിങ്ക് നൽകുക.")
