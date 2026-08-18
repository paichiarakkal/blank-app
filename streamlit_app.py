import io
import streamlit as st
import yt_dlp

st.title("All-in-One Video Downloader 🚀")
st.write(
    "YouTube, Instagram, Facebook തുടങ്ങി ഏത് വീഡിയോ ലിങ്കും താഴെ പേസ്റ്റ് ചെയ്ത്"
    " ഡൗൺലോഡ് ചെയ്യാം."
)

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Process Video"):
  if url:
    st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")

    # Cookies / User-Agent ഫേക്ക് ചെയ്ത് ബ്ലോക്കിംഗ് ഒഴിവാക്കാനുള്ള ഓപ്ഷനുകൾ
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        ),
        'referer': 'https://www.google.com/',
    }

    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # 1. വീഡിയോയുടെ വിവരം എടുക്കുന്നു
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'video')

        # പേരിൽ വരുന്ന അനാവശ്യ ചിഹ്നങ്ങൾ മാറ്റുന്നു
        clean_title = ''.join(
            [c for c in title if c.isalpha() or c.isdigit() or c == ' ']
        ).strip()
        filename = f'{clean_title}.mp4'

        # 2. വീഡിയോ വിവരങ്ങൾ കാണിക്കുന്നു
        st.success(f"**Found:** {title}")

        # വിഡിയോയുടെ direct stream URL ഉണ്ടെങ്കിൽ പ്ലേ ചെയ്യുന്നു
        video_url = info.get('url')
        if video_url:
          st.video(video_url)

          # ഡൗൺലോഡ് ബട്ടൺ (Streamlit Direct Download)
          st.download_button(
              label="⬇️ Download Video File",
              data=video_url,
              file_name=filename,
              mime="video/mp4",
          )

    except Exception as e:
      st.error(
          "വീഡിയോ പ്രോസസ്സ് ചെയ്യാൻ സാധിച്ചില്ല. YouTube ബോട്ട് പ്രൊട്ടക്ഷൻ കാരണം"
          " ബ്ലോക്ക് ചെയ്തതാകാം."
      )
      st.code(str(e))
  else:
    st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
