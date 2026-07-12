import streamlit as st
import yt_dlp
import os
import imageio_ffmpeg

# ആപ്പിന്റെ ലേഔട്ട്
st.set_page_config(page_title="High Quality Video Downloader", page_icon="🎥")
st.title("High Quality Video Downloader 🚀")
st.write("ലിങ്ക് പേസ്റ്റ് ചെയ്ത് മികച്ച ക്വാളിറ്റിയിൽ (ശബ്ദത്തോടെ) വീഡിയോ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # താൽക്കാലികമായി സെർവറിൽ ഫയൽ സൂക്ഷിക്കാനുള്ള പേര്
        output_filename = "downloaded_hq_video.mp4"
        
        # പഴയ ഫയലുകൾ ഉണ്ടെങ്കിൽ ഡിലീറ്റ് ചെയ്യുന്നു
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
        # imageio-ffmpeg പാത്ത് കണ്ടെത്തുന്നു
        try:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except:
            ffmpeg_path = "ffmpeg"
        
        # മികച്ച വീഡിയോയും ഓഡിയോയും ലയിപ്പിക്കാനുള്ള ഓപ്ഷനുകൾ
        ydl_opts = {
            # 1080p/720p/4K ലഭ്യമായതിൽ വെച്ച് ഏറ്റവും മികച്ച വീഡിയോയും ഓഡിയോയും എടുക്കുന്നു
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'outtmpl': output_filename,
            'ffmpeg_location': ffmpeg_path,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            # യൂട്യൂബിന്റെ ബ്ലോക്കിംഗ് ഒഴിവാക്കാനുള്ള ക്ലയന്റ് ഐഡന്റിറ്റി
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # സെർവറിലേക്ക് ആദ്യം വീഡിയോ ഡൗൺലോഡ് ചെയ്ത് മേർജ് ചെയ്യുന്നു
                ydl.download([url])
                
            # മേർജ് ചെയ്ത ഫയൽ ബൈറ്റ്സ് ആയി റീഡ് ചെയ്യുന്നു
            if os.path.exists(output_filename):
                with open(output_filename, "rb") as file:
                    video_bytes = file.read()
                    
                st.success("വീഡിയോ വിജയകരമായി പ്രോസസ്സ് ചെയ്തു!")
                
                # ഫുൾ ക്ലിയറിലുള്ള വീഡിയോ പ്ലെയർ
                st.video(video_bytes)
                
                # ഗാലറിയിലേക്ക് നേരിട്ട് സേവ് ചെയ്യാനുള്ള ഔദ്യോഗിക ബട്ടൺ
                st.download_button(
                    label="⬇️ ഗാലറിയിലേക്ക് ഡൗൺലോഡ് ചെയ്യുക (Full HD)",
                    data=video_bytes,
                    file_name="Premium_HD_Video.mp4",
                    mime="video/mp4"
                )
                
                # ഉപയോഗത്തിന് ശേഷം സെർവറിലെ ഫയൽ ഡിലീറ്റ് ചെയ്ത് മെമ്മറി ഫ്രീ ആക്കുന്നു
                os.remove(output_filename)
            else:
                st.error("ക്ഷമിക്കണം, വീഡിയോ പ്രോസസ്സ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
