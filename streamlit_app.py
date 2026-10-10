import os
import requests
import streamlit as st
import yt_dlp

# --- പേജ് സെറ്റിംഗ്സ് (Page Settings) ---
st.set_page_config(
    page_title="Ultimate Link Downloader",
    page_icon="📥",
    layout="centered"
)

# --- ടൈറ്റിലും വിവരങ്ങളും (Title & Info) ---
st.title("📥 Ultimate Link Downloader App")
st.write("ഡൗൺലോഡ് ചെയ്യേണ്ട ലിങ്ക് താഴെ നൽകുക:")

# --- ഇൻപുട്ട് ബോക്സ് (Input Box) ---
url = st.text_input("URL ഇവിടെ പേസ്റ്റ് ചെയ്യുക:", placeholder="https://...")

# --- ഡൗൺലോഡ് പ്രോസസ്സ് (Download Process) ---
if st.button("Download"):
    if url:
        st.info("ഡൗൺലോഡിംഗ് ആരംഭിക്കുന്നു...")
        
        # താൽക്കാലികമായി ഫയൽ സേവ് ചെയ്യാനുള്ള പേര്
        temp_filename = "downloaded_media"

        # 1. First attempt downloading using yt-dlp (for videos/media)
        # യൂട്യൂബിന്റെ ബ്ലോക്കുകൾ ഒഴിവാക്കാനുള്ള അത്യാവശ്യ ഓപ്ഷനുകൾ ഇവിടെ ചേർത്തിട്ടുണ്ട്.
        ydl_opts = {
            'outtmpl': f'{temp_filename}.%(ext)s',
            'format': 'best',
            # യൂട്യൂബിനെ പറ്റിക്കാൻ ബ്രൗസറിൽ നിന്നാണെന്ന് തോന്നിപ്പിക്കുന്നു
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # എറർ വന്നാൽ പെട്ടെന്ന് നിർത്താതിരിക്കാൻ
            'ignoreerrors': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                st.info("മീഡിയ വിവരങ്ങൾ ശേഖരിക്കുന്നു...")
                # വീഡിയോ ആണോ എന്ന് ഉറപ്പുവരുത്താൻ
                info = ydl.extract_info(url, download=True)
                
                # ഡൗൺലോഡ് ചെയ്ത ഫയലിന്റെ യഥാർത്ഥ പേര് കണ്ടുപിടിക്കുന്നു
                filename = ydl.prepare_filename(info)
                
            st.success("മീഡിയ ഡൗൺലോഡ് പൂർത്തിയായി!")
            
            # ഡൗൺലോഡ് ബട്ടൺ കാണിക്കുന്നു
            with open(filename, "rb") as file:
                st.download_button(
                    label="ഫയൽ സേവ് ചെയ്യുക (Save File)",
                    data=file,
                    file_name=os.path.basename(filename)
                )
                
            # താൽക്കാലിക ഫയലുകൾ ഡിലീറ്റ് ചെയ്യുക (സെർവർ സ്റ്റോറേജ് ലാഭിക്കാൻ)
            # st.download_button ഉപയോഗിക്കുമ്പോൾ ഫയൽ പെട്ടെന്ന് ഡിലീറ്റ് ചെയ്യാൻ പാടില്ല,
            # അതിനാൽ ഇത് പിന്നീട് ഒരു ക്ലീനപ്പ് ടാസ്ക് ആയി ചെയ്യുന്നതാണ് നല്ലത്.
            
        except Exception as e:
            st.warning(f"yt-dlp വഴി ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല: {e}")
            st.info("സാധാരണ വെബ് പേജ് ആയി ഡൗൺലോഡ് ചെയ്യാൻ ശ്രമിക്കുന്നു...")
            
            # 2. Fallback to normal HTTP download for web pages/articles/files
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    st.success("വെബ് പേജ് വിജയകരമായി ഡൗൺലോഡ് ചെയ്തു!")
                    # HTML ആയി സേവ് ചെയ്യുന്നു
                    st.download_button(
                        label="HTML/പേജ് സേവ് ചെയ്യുക (Save Page)",
                        data=response.content,
                        file_name="page_content.html",
                        mime="text/html"
                    )
                else:
                    st.error(f"HTTP Error: {response.status_code}")
            except Exception as req_err:
                st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ പൂർണ്ണമായും സാധിച്ചില്ല. പ്രശ്നം ഇതാണ്: {req_err}")
    else:
        st.warning("ദയവായി ഒരു valid URL നൽകുക.")

# --- ഫൂട്ടർ (Footer) ---
st.divider()
st.caption("ശ്രദ്ധിക്കുക: ചില സുരക്ഷാ ക്രമീകരണങ്ങളുള്ള വെബ്സൈറ്റുകളിൽ നിന്ന് ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചേക്കില്ല.")
