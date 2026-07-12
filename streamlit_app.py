import streamlit as st
import yt_dlp

# 1. ആപ്പിന്റെ പേരും പേജ് കോൺഫിഗറേഷനും
st.set_page_config(page_title="High Quality Video Downloader", page_icon="🎥", layout="centered")

st.title("High Quality Video Downloader 🚀")
st.write("യൂട്യൂബ് വീഡിയോ/ഷോർട്സ് ലിങ്ക് പേസ്റ്റ് ചെയ്ത് മികച്ച ക്വാളിറ്റിയിൽ ഡൗൺലോഡ് ചെയ്യാം.")

# 2. യൂസർ ഇൻപുട്ട് വാങ്ങുന്ന ഭാഗം
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:", placeholder="https://youtube.com/shorts/...")

if st.button("Get Video & Download Link", type="primary"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # 3. yt-dlp കോൺഫിഗറേഷൻ (ഏറ്റവും നല്ല ക്വാളിറ്റിയും ഓഡിയോയും ഉറപ്പാക്കുന്നു)
        ydl_opts = {
            # ഓഡിയോയും വീഡിയോയും ഒരുമിച്ചുള്ള ലഭ്യമായതിൽ ഏറ്റവും മികച്ച mp4 ഫോർമാറ്റ് തിരഞ്ഞെടുക്കുന്നു
            'format': 'best[ext=mp4]/best', 
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            # യൂട്യൂബ് ബ്ലോക്ക് ചെയ്യുന്നത് ഒഴിവാക്കാനുള്ള ക്ലയന്റ് ഐഡന്റിറ്റി
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        try:
            # 4. വീഡിയോ വിവരങ്ങൾ എടുക്കുന്നു
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'video')
                thumbnail = info.get('thumbnail')
                
            if video_url:
                st.success(f"വിജയകരമായി കണ്ടെത്തി: {title}")
                
                # വീഡിയോയുടെ തംബ്‌നെയിൽ കാണിക്കാൻ
                if thumbnail:
                    st.image(thumbnail, width=300)
                
                # Streamlit പ്ലെയറിൽ വീഡിയോ കാണിക്കാൻ
                st.video(video_url)
                
                # 5. നേരിട്ട് ഡൗൺലോഡ് ചെയ്യാനുള്ള പച്ച നിറത്തിലുള്ള ബട്ടൺ (HTML)
                st.markdown(f'''
                    <a href="{video_url}" download="{title}.mp4" target="_blank" style="text-decoration: none;">
                        <div style="background-color:#4CAF50; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold; font-size:18px; margin-top:15px; cursor:pointer;">
                            ⬇️ വീഡിയോ ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ ക്ലിക്ക് ചെയ്യുക
                        </div>
                    </a>
                ''', unsafe_allow_html=True)
                
                st.caption("ശ്രദ്ധിക്കുക: മുകളിലെ ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ പുതിയ ടാബിൽ വീഡിയോ ഓപ്പൺ ആവുകയാണെങ്കിൽ, അവിടെയുള്ള 3 ഡോട്ട്സിൽ (Three dots) ക്ലിക്ക് ചെയ്ത് 'Download' കൊടുക്കാവുന്നതാണ്.")
            else:
                st.error("ക്ഷമിക്കണം, ഈ വീഡിയോയുടെ ഡൗൺലോഡ് ലിങ്ക് കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
