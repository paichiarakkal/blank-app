import streamlit as st
import yt_dlp

st.set_page_config(page_title="Mobile Video Downloader", page_icon="📲")
st.title("Mobile Video Downloader 🚀")
st.write("ഫോണിൽ ഒട്ടും ക്വാളിറ്റി കുറയാതെ ഓഡിയോയും വീഡിയോയും ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("യൂട്യൂബ് ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Get Video"):
    if url:
        st.info("ഫോണിന് അനുയോജ്യമായ ഏറ്റവും മികച്ച ക്വാളിറ്റി കണ്ടെത്തുന്നു...")
        
        ydl_opts = {
            # ഫോണുകളിൽ കൃത്യമായി പ്ലേ ചെയ്യുന്ന, ശബ്ദവും ചിത്രവും ഒന്നിച്ചുള്ള (Progressive) മികച്ച ഫോർമാറ്റ് എടുക്കുന്നു
            'format': 'best[progressive=true][ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'video')
                
            if video_url:
                st.success(f"വിജയകരമായി ലഭിച്ചു: {title}")
                
                # ഫോൺ സ്ക്രീനിൽ പ്ലേ ചെയ്യാൻ
                st.video(video_url)
                
                # ഫോണിൽ നേരിട്ട് ഡൗൺലോഡ് ചെയ്യാനുള്ള ലളിതമായ ബട്ടൺ
                st.markdown(f'''
                    <a href="{video_url}" download="{title}.mp4" target="_blank" style="text-decoration: none;">
                        <div style="background-color:#00cc66; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:bold; font-size:16px; margin-top:10px;">
                            📲 ഗാലറിയിലേക്ക് ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ ഞെക്കുക
                        </div>
                    </a>
                ''', unsafe_allow_html=True)
                
                st.caption("💡 **ഫോൺ യൂസർമാർ ശ്രദ്ധിക്കാൻ:** മുകളിലെ ബട്ടൺ ഞെക്കുമ്പോൾ വീഡിയോ പ്ലേ ചെയ്യുകയാണെങ്കിൽ, വീഡിയോയുടെ താഴെ വലതുവശത്തുള്ള **3 കുത്തുകളിൽ (Three Dots)** ക്ലിക്ക് ചെയ്ത് **Download** അടിക്കുക.")
            else:
                st.error("വീഡിയോ ലിങ്ക് കണ്ടെത്താൻ സാധിച്ചില്ല.")
                
        except Exception as e:
            st.error(f"എറർ: {e}")
    else:
        st.warning("ദയവായി ലിങ്ക് നൽകുക!")
