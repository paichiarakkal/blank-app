import streamlit as st
import yt_dlp
import io

# ആപ്പിന്റെ ലേഔട്ട്
st.set_page_config(page_title="720p Video Downloader", page_icon="🎥")
st.title("720p Video Downloader 🚀")
st.write("ലിങ്ക് പേസ്റ്റ് ചെയ്ത് 720p ക്വാളിറ്റിയിൽ വീഡിയോ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Get Download Link"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # ഓഡിയോയും വീഡിയോയും ഒരുമിച്ചുള്ള (progressive) 720p ഫോർമാറ്റ് സെലക്ട് ചെയ്യുന്നു
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best', 
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}, # ios client കൂടുതൽ സ്റ്റേബിൾ ആണ്
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'video')
                
            if video_url:
                st.success(f"വിജയകരമായി ലഭിച്ചു: {title}")
                
                # Streamlit പ്ലെയറിൽ കാണിക്കാൻ
                st.video(video_url)
                
                # നേരിട്ട് ഡൗൺലോഡ് ചെയ്യാനുള്ള ബട്ടൺ
                st.markdown(f'''
                    <a href="{video_url}" download="{title}.mp4" target="_blank">
                        <button style="background-color:#4CAF50; color:white; padding:10px 24px; border:none; border-radius:4px; cursor:pointer; font-size:16px;">
                            ⬇️ വീഡിയോ ഡൗൺലോഡ് ചെയ്യുക
                        </button>
                    </a>
                ''', unsafe_allow_html=True)
                
            else:
                st.error("ക്ഷമിക്കണം, ഈ വീഡിയോയുടെ ലിങ്ക് കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
