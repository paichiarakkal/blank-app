import io
import streamlit as st
import yt_dlp

st.set_page_config(
    page_title='Video Downloader', page_icon='🚀', layout='centered'
)

st.title('All-in-One Video Downloader 🚀')
st.write('YouTube ഉൾപ്പെടെയുള്ള ഏത് വീഡിയോ ലിങ്കും താഴെ നൽകി ഡൗൺലോഡ് ചെയ്യാം.')

url = st.text_input('വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:')

if st.button('Fetch Video'):
  if url:
    st.info('വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...')

    # YouTube Bot Detection മറികടക്കാനുള്ള കോൺഫിഗറേഷൻ
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': ['player_client=android,web']},
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # വീഡിയോയുടെ വിവരങ്ങൾ എടുക്കുന്നു
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'video')

        # ഫയൽ നെയിം ശരിയാക്കുന്നു
        clean_title = ''.join(
            [c for c in title if c.isalnum() or c in (' ', '_', '-')]
        ).strip()
        filename = f'{clean_title}.mp4'

        st.success(f'**വീഡിയോ കണ്ടെത്തി:** {title}')

        # Direct Video URL കാണിക്കുന്നു
        video_url = info.get('url')

        if video_url:
          st.video(video_url)

          # ഡൗൺലോഡ് ചെയ്യാനുള്ള ലിങ്ക്
          st.markdown(
              f'<a href="{video_url}" target="_blank" download="{filename}">'
              '<button style="background-color:#4CAF50; color:white; padding:10px'
              ' 20px; border:none; border-radius:5px; cursor:pointer;">'
              '⬇️ ഫോണിലേക്ക് / കമ്പ്യൂട്ടറിലേക്ക് ഡൗൺലോഡ് ചെയ്യുക</button>a>',
              unsafe_allow_html=True,
          )

    except Exception as e:
      st.error(
          'YouTube സുരക്ഷാ കാരണങ്ങളാൽ ഈ ലിങ്ക് ബ്ലോക്ക് ചെയ്തിരിക്കുകയാണ്.'
      )
      st.warning(
          'ശ്രദ്ധിക്കുക: Instagram, Facebook, TikTok തുടങ്ങിയ ലിങ്കുകൾ ഇതിൽ'
          ' സുഗമമായി വർക്ക് ചെയ്യും.'
      )
      st.code(str(e))
  else:
    st.warning('ദയവായി ഒരു ലിങ്ക് നൽകുക!')
