import streamlit as st
import yt_dlp

st.set_page_config(page_title="Ultimate HD Downloader", page_icon="🎥")
st.title("Ultimate HD Video Downloader 🚀")
st.write("യൂട്യൂബ് വീഡിയോ/ഷോർട്സ് ഏറ്റവും ഉയർന്ന ഒറിജിനൽ ക്വാളിറ്റിയിൽ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Get High Quality Links"):
    if url:
        st.info("മികച്ച ഡൗൺലോഡ് ലിങ്കുകൾ കണ്ടെത്തുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # YouTube ബ്ലോക്ക് ചെയ്യാതിരിക്കാനുള്ള കൃത്യമായ ഓപ്ഷനുകൾ
        ydl_opts = {
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web', 'ios']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                title = info.get('title', 'video')
                thumbnail = info.get('thumbnail')
                
            if formats:
                st.success(f"വിജയകരമായി കണ്ടെത്തി: {title}")
                if thumbnail:
                    st.image(thumbnail, width=250)
                
                # --- ഇവിടെ നമ്മൾ ക്വാളിറ്റി തിരിച്ചു ലിങ്കുകൾ കാണിക്കുന്നു ---
                st.markdown("### 📥 ഡൗൺലോഡ് ഓപ്ഷനുകൾ:")
                
                # 1. ചിത്രവും ശബ്ദവും ഒന്നിച്ചുള്ള മികച്ച ഫോർമാറ്റ് (ഫോണിൽ നേരിട്ട് കാണാൻ)
                # സാധാരണയായി ഇത് 720p ആയിരിക്കും
                progressive_url = None
                for f in reversed(formats):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                        progressive_url = f.get('url')
                        break
                
                if progressive_url:
                    st.video(progressive_url)
                    st.markdown(f'👉 [**720p HD (ശബ്ദത്തോടെ നേരിട്ട് ഡൗൺലോഡ് ചെയ്യാൻ) ⬇️**]({progressive_url})')
                
                st.write("---")
                st.subheader("🔥 1080p / 4K ഫുൾ ക്ലിയറിറ്റി വേണമെങ്കിൽ:")
                st.caption("ശ്രദ്ധിക്കുക: YouTube ഉയർന്ന ക്വാളിറ്റിയിൽ ചിത്രവും ശബ്ദവും വെവ്വേറെയാണ് നൽകുന്നത്. അതിനാൽ താഴെയുള്ള ലിങ്കുകൾ പ്രത്യേകം ഉപയോഗിക്കാം.")
                
                # 2. ഏറ്റവും ഉയർന്ന ക്വാളിറ്റി വീഡിയോ ലിങ്ക് (ചിത്രം മാത്രം - 1080p/4K)
                best_video_url = None
                video_resolution = "Full HD/4K"
                for f in reversed(formats):
                    if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('ext') == 'mp4':
                        best_video_url = f.get('url')
                        video_resolution = f.get('resolution', 'High Quality')
                        break
                        
                # 3. ഏറ്റവും മികച്ച ഓഡിയോ ലിങ്ക് (ശബ്ദം മാത്രം)
                best_audio_url = None
                for f in reversed(formats):
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                        best_audio_url = f.get('url')
                        break
                
                if best_video_url:
                    st.markdown(f'🎬 [**ഫുൾ ക്ലിയർ വീഡിയോ മാത്രം ഡൗൺലോഡ് ചെയ്യാൻ ({video_resolution}) ⬇️**]({best_video_url})')
                if best_audio_url:
                    st.markdown(f'🎵 [**ഉയർന്ന ക്വാളിറ്റി ഓഡിയോ മാത്രം ഡൗൺലോഡ് ചെയ്യാൻ ⬇️**]({best_audio_url})')
                    
            else:
                st.error("ക്ഷമിക്കണം, ഈ വീഡിയോയുടെ ലിങ്കുകൾ കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
