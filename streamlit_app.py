import streamlit as st
import yt_dlp
import requests
import os

st.title("Link Downloader App")
st.write("ഡൗൺലോഡ് ചെയ്യേണ്ട ലിങ്ക് താഴെ നൽകുക:")

url = st.text_input("URL ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download"):
    if url:
        st.info("ഡൗൺലോഡിംഗ് ആരംഭിക്കുന്നു...")
        
        # 1. First attempt downloading using yt-dlp (for videos/media)
        ydl_opts = {
            'outtmpl': 'downloaded_file.%(ext)s',
            'format': 'best',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            st.success("വീഡിയോ/മീഡിയ ഡൗൺലോഡ് പൂർത്തിയായി!")
            with open(filename, "rb") as file:
                st.download_button(
                    label="ഫയൽ സേവ് ചെയ്യുക (Save File)",
                    data=file,
                    file_name=os.path.basename(filename)
                )
        except Exception as e:
            # 2. Fallback to normal HTTP download for web pages/articles/files
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    st.success("വെബ് പേജ് വിജയകരമായി ഡൗൺലോഡ് ചെയ്തു!")
                    st.download_button(
                        label="HTML/പേജ് സേവ് ചെയ്യുക (Save Page)",
                        data=response.content,
                        file_name="page_content.html",
                        mime="text/html"
                    )
                else:
                    st.error(f"HTTP Error: {response.status_code}")
            except Exception as req_err:
                st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല: {req_err}")
    else:
        st.warning("ദയവായി ഒരു valid URL നൽകുക.")
