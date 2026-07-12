import streamlit as st
import yt_dlp
import os
import imageio_ffmpeg

st.set_page_config(page_title="True HD Downloader", page_icon="🎥")
st.title("True HD Video Downloader 🚀")
st.write("യൂട്യൂബിലുള്ള അതേ ഒറിജിനൽ HD/4K ക്വാളിറ്റിയിൽ (ശബ്ദത്തോടെ) ഫോണിൽ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("യൂട്യൂബ് ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download High Quality Video"):
    if url:
        st.info("ഏറ്റവും മികച്ച ചിത്രവും ശബ്ദവും ക്ലൗഡ് സെർവറിൽ ഒന്നിപ്പിക്കുന്നു. ദയവായി അല്പം കാത്തിരിക്കുക...")
        
        output_file = "premium_hd_video.mp4"
        
        if os.path.exists(output_file):
            os.remove(output_file)
            
        # ക്ലൗഡ് സെർവറിന് അനുയോജ്യമായ രീതിയിൽ ffmpeg എക്സിക്യൂട്ടബിൾ കണ്ടെത്തുന്നു
        try:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except:
            ffmpeg_path = "ffmpeg" # സെർവറിൽ ഡിഫോൾട്ട് ആയി ഉണ്ടെങ്കിൽ
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'outtmpl': output_file,
            'ffmpeg_location': ffmpeg_path, 
            'nocheckcertificate': True,
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            with open(output_file, "rb") as file:
                video_bytes = file.read()
                
            st.success("വിജയകരമായി പ്രോസസ്സ് ചെയ്തു!")
            
            # സൂപ്പർ ക്ലിയർ വീഡിയോ പ്ലെയർ
            st.video(video_bytes)
            
            # ഗാലറിയിലേക്ക് ഡൗൺലോഡ് ചെയ്യാനുള്ള ബട്ടൺ
            st.download_button(
                label="📲 ഗാലറിയിലേക്ക് സേവ് ചെയ്യുക (Full HD)",
                data=video_bytes,
                file_name="HD_Video.mp4",
                mime="video/mp4"
            )
            
            if os.path.exists(output_file):
                os.remove(output_file)
                
        except Exception as e:
            st.error(f"എറർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ലിങ്ക് നൽകുക!")
