import streamlit as st
import yt_dlp

# ആപ്പിന്റെ ലേഔട്ട്
st.set_page_config(page_title="Universal HD Video Downloader", page_icon="🎥")
st.title("Universal HD Video Downloader 🚀")
st.write("ലിങ്ക് പേസ്റ്റ് ചെയ്ത് മികച്ച ക്വാളിറ്റിയിൽ വീഡിയോ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

# ക്വാളിറ്റി സെലക്ട് ചെയ്യാനുള്ള ഓപ്ഷൻ
quality = st.selectbox(
    "വീഡിയോ ക്വാളിറ്റി തിരഞ്ഞെടുക്കുക:",
    ("Best Quality (1080p/4K/HD)", "720p Quality")
)

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # യൂസർ തിരഞ്ഞെടുത്ത ക്വാളിറ്റി അനുസരിച്ച് format സെറ്റ് ചെയ്യുന്നു
        if quality == "Best Quality (1080p/4K/HD)":
            # ലഭ്യമായതിൽ വെച്ച് ഏറ്റവും മികച്ച വീഡിയോയും ഓഡിയോയും
            video_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        else:
            # നിങ്ങളുടെ പഴയ കോഡിലെ 720p ഫോർമാറ്റ്
            video_format = 'best[height<=720][ext=mp4]/best[ext=mp4]'
            
        ydl_opts = {
            'format': video_format,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
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
                st.video(video_url)
                st.markdown(f'[ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ ഞെക്കുക ⬇️]({video_url})')
            else:
                st.error("ക്ഷമിക്കണം, ഈ വീഡിയോയുടെ ഡൗൺലോഡ് ലിങ്ക് കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
