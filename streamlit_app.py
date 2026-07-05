import streamlit as st
import yt_dlp

# ആപ്പിന്റെ ലേഔട്ട് സെറ്റ് ചെയ്യുന്നു
st.set_page_config(page_title="All-in-One Video Downloader", page_icon="🚀")
st.title("All-in-One Video Downloader 🚀")
st.write("YouTube, Instagram, Facebook തുടങ്ങിയ പ്ലാറ്റ്‌ഫോമുകളിൽ നിന്നുള്ള വീഡിയോകൾ ഇവിടെ ഡൗൺലോഡ് ചെയ്യാം.")

# ലിങ്ക് വാങ്ങാനുള്ള ബോക്സ്
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

# വീഡിയോ ക്വാളിറ്റി തിരഞ്ഞെടുക്കാനുള്ള ഓപ്ഷനുകൾ
quality = st.selectbox("വീഡിയോ ക്വാളിറ്റി തിരഞ്ഞെടുക്കുക:", ("Best", "720p", "480p", "360p"))

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # ക്വാളിറ്റിക്ക് അനുസരിച്ചുള്ള കോൺഫിഗറേഷൻ
        if quality == "Best":
            format_opt = 'best[ext=mp4]/best'
        elif quality == "720p":
            format_opt = 'best[height<=720][ext=mp4]/best[height<=720]'
        elif quality == "480p":
            format_opt = 'best[height<=480][ext=mp4]/best[height<=480]'
        else:
            format_opt = 'best[height<=360][ext=mp4]/best[height<=360]'

        ydl_opts = {
            'format': format_opt,
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
                st.success(f"വീഡിയോ റെഡിയായിട്ടുണ്ട്: {title}")
                st.video(video_url)
                st.markdown(f'[ഫോണിലേക്ക് ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ ഞെക്കുക ⬇️]({video_url})')
            else:
                st.error("വീഡിയോ യുആർഎൽ കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ലിങ്ക് കൃത്യമാണോ എന്ന് പരിശോധിക്കുക. എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
