import streamlit as st
import yt_dlp
import os

st.title("Link Downloader App")
st.write("ഡൗൺലോഡ് ചെയ്യേണ്ട ലിങ്ക് താഴെ നൽകുക:")

# User input for URL
url = st.text_input("URL ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download"):
    if url:
        st.info("ഡൗൺലോഡിംഗ് ആരംഭിക്കുന്നു...")
        
        # Options for yt-dlp
        ydl_opts = {
            'outtmpl': 'downloaded_file.%(ext)s',
            'format': 'best',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            st.success("ഡൗൺലോഡ് പൂർത്തിയായി!")
            
            # Read file and create download button in Streamlit
            with open(filename, "rb") as file:
                btn = st.download_button(
                    label="ഫയൽ സേവ് ചെയ്യുക (Save File)",
                    data=file,
                    file_name=os.path.basename(filename)
                )
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("ദയവായി ഒരു valid URL നൽകുക.")
