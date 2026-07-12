import streamlit as st
import yt_dlp
import os

# ആപ്പിന്റെ പേരും പേജ് കോൺഫിഗറേഷനും
st.set_page_config(page_title="Ultra HD Video Downloader", page_icon="🎥", layout="centered")

st.title("Ultra HD Video Downloader 🚀")
st.write("യൂട്യൂബ് വീഡിയോ/ഷോർട്സ് അതിന്റെ പരമാവധി ഒറിജിനൽ ക്വാളിറ്റിയിൽ (1080p, 4K) ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:", placeholder="https://youtube.com/shorts/...")

if st.button("Get Video & Download Link", type="primary"):
    if url:
        st.info("ഏറ്റവും മികച്ച ക്വാളിറ്റിയിലുള്ള വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു. ദയവായി അല്പം കാത്തിരിക്കുക...")
        
        # പുതിയ കോൺഫിഗറേഷൻ: ഏറ്റവും മികച്ച വീഡിയോയും ഓഡിയോയും ലയിപ്പിക്കുന്നു
        ydl_opts = {
            # മികച്ച വീഡിയോയും മികച്ച ഓഡിയോയും എടുത്ത് mp4 ഫയൽ ആക്കുന്നു
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'video')
                thumbnail = info.get('thumbnail')
                
            if video_url:
                st.success(f"വിജയകരമായി കണ്ടെത്തി: {title}")
                
                if thumbnail:
                    st.image(thumbnail, width=300, caption="Video Thumbnail")
                
                # ഉയർന്ന ക്വാളിറ്റി ലിങ്ക് ആയതിനാൽ ചിലപ്പോൾ ബ്രൗസറിന് നേരിട്ട് പ്ലേ ചെയ്യാൻ പറ്റിയില്ലെങ്കിലും ഡൗൺലോഡ് ചെയ്യാം
                st.video(video_url)
                
                # ഡൗൺലോഡ് ബട്ടൺ
                st.markdown(f'''
                    <a href="{video_url}" download="{title}.mp4" target="_blank" style="text-decoration: none;">
                        <div style="background-color:#4CAF50; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold; font-size:18px; margin-top:15px; cursor:pointer;">
                            ⬇️ ഫുൾ ക്ലിയറോടെ ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ ക്ലിക്ക് ചെയ്യുക
                        </div>
                    </a>
                ''', unsafe_allow_html=True)
                
            else:
                st.error("ക്ഷമിക്കണം, ലിങ്ക് കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
