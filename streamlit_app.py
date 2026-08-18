import io
import streamlit as st
import yt_dlp

st.title("All-in-One Video Downloader 🚀")
st.write(
    "YouTube, Instagram, Facebook, TikTok തുടങ്ങി ഏത് വീഡിയോ ലിങ്കും താഴെ"
    " പേസ്റ്റ് ചെയ്ത് ഡൗൺലോഡ് ചെയ്യാം."
)

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
  if url:
    st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")

    # ഫോർമാറ്റും ഡൗൺലോഡ് ഓപ്ഷനുകളും
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '-',  # Memory ബഫറിലേക്ക് ഡൗൺലോഡ് ചെയ്യാൻ
        'logtostderr': False,
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            ),
        },
    }

    try:
      # 1. വീഡിയോയുടെ വിവരം എടുക്കുന്നു (Title മാത്രം)
      with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'video')
        clean_title = ''.join(
            [c for c in title if c.isalpha() or c.isdigit() or c == ' ']
        ).rstrip()
        filename = f'{clean_title}.mp4'

      # 2. വീഡിയോ RAM മെമ്മറിയിലേക്ക് ഡൗൺലോഡ് ചെയ്യുന്നു
      buffer = io.BytesIO()
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Streamlit-ലേക്ക് ഡൗൺലോഡ് പ്രോസസ് നടത്തുന്നു
        info_dict = ydl.extract_info(url, download=True)

      st.success('വീഡിയോ റെഡിയായിട്ടുണ്ട്!')

      # direct URL കാണിക്കുന്നതിന് പകരം Streamlit download_button ഉപയോഗിക്കുന്നു
      video_url = info_dict.get('url')

      if video_url:
        st.video(video_url)
        st.markdown(
            f'<a href="{video_url}" download="{filename}"'
            ' target="_blank">ഫോണിലേക്ക് ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ'
            ' അമർത്തുക ⬇️</a>',
            unsafe_allow_html=True,
        )

    except Exception as e:
      st.error(
        'ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ലിങ്ക് കൃത്യമാണോ എന്ന് പരിശോധിക്കുക.'
        f' എറർ: {e}'
      )
  else:
    st.warning('ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!')
