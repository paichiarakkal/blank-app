import streamlit as st
import yt_dlp
import os

# ആപ്പിന്റെ ലേഔട്ട്
st.set_page_config(page_title="Universal HD Video Downloader", page_icon="🎥")
st.title("Universal HD Video Downloader 🚀")
st.write("ലിങ്ക് പേസ്റ്റ് ചെയ്ത് മികച്ച ക്വാളിറ്റിൽ വീഡിയോ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

quality = st.selectbox(
    "വീഡിയോ ക്വാളിറ്റി തിരഞ്ഞെടുക്കുക:",
    ("Best Quality (1080p/4K/HD)", "720p Quality")
)

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # യൂസർ സെലക്ട് ചെയ്യുന്നതിന് അനുസരിച്ച് ഫോർമാറ്റ് മാറ്റുന്നു
        if quality == "Best Quality (1080p/4K/HD)":
            video_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        else:
            video_format = 'best[height<=720][ext=mp4]/best[ext=mp4]'
            
        # വീഡിയോ ലോക്കലായി ഡൗൺലോഡ് ചെയ്യാനുള്ള ഓപ്ഷൻസ്
        ydl_opts = {
            'format': video_format,
            'outtmpl': 'downloads/%(title)s.%(ext)s', # downloads ഫോൾഡറിലേക്ക് സേവ് ചെയ്യും
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ഇവിടെ download=True നൽകി വീഡിയോ താല്കാലികമായി സെർവറിലേക്ക് ഡൗൺലോഡ് ചെയ്യുന്നു
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'video')
                
            if os.path.exists(filename):
                st.success(f"വിജയകരമായി ലഭിച്ചു: {title}")
                
                # ഫയൽ ബൈനറിയായി റീഡ് ചെയ്യുന്നു
                with open(filename, "rb") as file:
                    video_bytes = file.read()
                
                # Streamlit-ന്റെ ഒഫീഷ്യൽ ഡൗൺലോഡ് ബട്ടൺ
                st.download_button(
                    label="ഫോണിലേക്ക്/സിസ്റ്റത്തിലേക്ക് ഡൗൺലോഡ് ചെയ്യുക ⬇️",
                    data=video_bytes,
                    file_name=os.path.basename(filename),
                    mime="video/mp4"
                )
                
                # ഡൗൺലോഡ് കഴിഞ്ഞ ശേഷം സെർവറിലെ ഫയൽ ഡിലീറ്റ് ചെയ്യുക (സ്പേസ് കളയാതിരിക്കാൻ)
                os.remove(filename)
            else:
                st.error("ക്ഷമിക്കണം, ഈ വീഡിയോയുടെ ഡൗൺലോഡ് ലിങ്ക് കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
