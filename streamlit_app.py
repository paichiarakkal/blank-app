import os
import requests
import streamlit as st
import yt_dlp

# --- പേജ് ക്രമീകരണങ്ങൾ ---
st.set_page_config(
    page_title="Ultimate Link Downloader", page_icon="📥", layout="centered"
)

st.title("📥 All-in-One Link Downloader")
st.write("ഡൗൺലോഡ് ചെയ്യേണ്ട ലിങ്ക് താഴെ നൽകുക:")

# --- ഇൻപുട്ട് ബോക്സ് ---
url = st.text_input(
    "URL ഇവിടെ പേസ്റ്റ് ചെയ്യുക:",
    placeholder="https://www.youtube.com/... അല്ലെങ്കിൽ മറ്റു ലിങ്കുകൾ",
)

if st.button("Download"):
  if url:
    st.info("പ്രോസസ്സിംഗ് ആരംഭിക്കുന്നു...")

    # yt-dlp ക്രമീകരണങ്ങൾ (403 Forbidden, Unsupported URL എററുകൾ തടയാൻ)
    ydl_opts = {
        'outtmpl': 'downloaded_media.%(ext)s',
        'format': 'best',
        'noplaylist': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['dash', 'hls'],
            }
        },
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        },
    }

    # 1. ആദ്യം yt-dlp വഴി വീഡിയോ/മീഡിയ ഡൗൺലോഡ് ചെയ്യാൻ ശ്രമിക്കുന്നു
    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        st.info("മീഡിയ ഫയൽ ഡൗൺലോഡ് ചെയ്യുന്നു...")
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

      st.success("വീഡിയോ/മീഡിയ ഡൗൺലോഡ് പൂർത്തിയായി!")

      with open(filename, 'rb') as file:
        st.download_button(
            label="📁 ഫയൽ ഫോണിലേക്ക് സേവ് ചെയ്യുക (Save File)",
            data=file,
            file_name=os.path.basename(filename),
        )

    except Exception as e:
      st.warning(f"മീഡിയ ഡൗൺലോഡ് പരാജയപ്പെട്ടു: {e}")
      st.info("വെബ് പേജ് ആയി ഡൗൺലോഡ് ചെയ്യാൻ ശ്രമിക്കുന്നു...")

      # 2. ഫെയിൽ ആയാൽ സാധാരണ വെബ് പേജ്/ലേഖനം ആയി ഡൗൺലോഡ് ചെയ്യുന്നു
      try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
          st.success("വെബ് പേജ് വിജയിച്ചു!")
          st.download_button(
              label="📄 HTML പേജ് സേവ് ചെയ്യുക (Save Page)",
              data=response.content,
              file_name="page_content.html",
              mime="text/html",
          )
        else:
          st.error(f"HTTP Error: {response.status_code}")
      except Exception as req_err:
        st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല: {req_err}")
  else:
    st.warning("ദയവായി ഒരു valid URL നൽകുക.")

st.divider()
st.caption(
    "Note: ചില ഫേസ്ബുക്ക്/യൂട്യൂബ് പ്രൈവറ്റ് ലിങ്കുകൾ സെർവർ സുരക്ഷ കാരണം"
    " ബ്ലോക്ക് ആയേക്കാം."
)
