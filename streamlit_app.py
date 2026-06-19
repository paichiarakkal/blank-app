import streamlit as st
import yt_dlp

st.title("YouTube Video Downloader")

# User Agent നൽകുന്നത് വഴി 403 Forbidden എറർ ഒഴിവാക്കാൻ സാധിക്കും
ydl_opts = {
    'format': 'best',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = st.text_input("YouTube ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download"):
    if url:
        try:
            st.info("ഡൗൺലോഡ് ആകുന്നു, ദയവായി കാത്തിരിക്കുക...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            st.success("ഡൗൺലോഡ് പൂർത്തിയായി!")
        except Exception as e:
            st.error(f"എന്തോ കുഴപ്പമുണ്ട്: {e}")
    else:
        st.warning("ദയവായി ഒരു ലിങ്ക് നൽകുക.")
