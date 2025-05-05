import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

### SCRAPING FUNCTION ###
def scrape_detik_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1', class_='detail__title').get_text(strip=True)

        content = '\n'.join(
            p.get_text(" ", strip=True)
            for p in soup.select('div.detail__body-text.itp_bodycontent > p')
            if not p.find('i')
        )

        return {'title': title, 'content': content}
    except Exception as e:
        print(f"[Detik] Error: {e}")
        return None

def scrape_kompas_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title
        title_tag = soup.find('h1', class_='read__title')
        title = title_tag.get_text(strip=True) if title_tag else 'Judul tidak ditemukan'

        # Extract all <p> tags within the div with class 'read__content'
        content_div = soup.find('div', class_='read__content')
        if content_div:
            # Handle the last <i> tag in the content
            last_i = content_div.find_all('i')[-1] if content_div.find_all('i') else None
            if last_i:
                last_i.decompose()

            # Extract and combine all <p> tags into a single string
            paragraphs = content_div.find_all('p')
            content = '\n'.join(p.get_text(strip=True) for p in paragraphs)
        else:
            content = 'Konten tidak ditemukan'

        return {'title': title, 'content': content}
    except Exception as e:
        print(f"[Kompas] Error: {e}")
        return None

def scrape_suara_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        info_div = soup.find('div', class_='info')
        title = info_div.find('h1').get_text(strip=True) if info_div and info_div.find('h1') else 'Judul tidak ditemukan'

        article = soup.select_one('article.detail-content.detail-berita.live-report2')
        if article:
            first_p = article.find('p')
            if first_p and first_p.contents and getattr(first_p.contents[0], 'name', None) == 'strong':
                first_p.contents[0].decompose()

            paragraphs = article.find_all('p')
            if paragraphs and paragraphs[-1].find('i'):
                paragraphs.pop()

            content = '\n'.join(p.get_text(strip=True) for p in paragraphs)
        else:
            content = 'Konten tidak ditemukan'

        return {'title': title, 'content': content}
    except Exception as e:
        print(f"[Suara] Error: {e}")
        return None

def scrape_news_auto(url):
    domain = urlparse(url).netloc

    if "suara.com" in domain:
        # Tambahkan ?page=all jika belum ada
        if "page=all" not in url:
            if "?" in url:
                url += "&page=all"
            else:
                url += "?page=all"
        return scrape_suara_news(url)

    elif "detik.com" in domain:
        if "page=all" not in url:
            if "?" in url:
                url += "&page=all"
            else:
                url += "?page=all"
        return scrape_detik_news(url)

    elif "kompas.com" in domain:
        if "page=all" not in url:
            if "?" in url:
                url += "&page=all"
            else:
                url += "?page=all"
        return scrape_kompas_news(url)

    else:
        return None

### STREAMLIT PAGE SETUP ###
st.set_page_config(
    page_title= "Klasifikasi Judul dan Berita Online",
    page_icon= "📰",
    initial_sidebar_state="collapsed",
)

st.markdown(
    "<h1 style='text-align: center;'>KLASIFIKASI<br>JUDUL DAN BERITA ONLINE</h1>",
    unsafe_allow_html=True,
)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Link:</h4>", unsafe_allow_html=True)

result = None

scrape_failed = False
# Provide a non-empty label and hide it
user_url = st.text_input(
    label="Masukkan URL berita dari Detik/Kompas/Suara:",  # Non-empty label for accessibility
    placeholder="Link support portal berita detik.com, kompas.com dan suara.com",
    label_visibility="visible",
).strip()

if user_url:
    #st.write(f"Scraping: {user_url}") # Test buat liat link bisa
    result = scrape_news_auto(user_url)
    if result:
        #st.write("Hasil Scraping:")
        #st.write(result)
        st.markdown(
            "<p style='color: white;'>URL valid tekan proses untuk melakukan klasifikasi.</p>",
            unsafe_allow_html=True,
        )
    else:
        scrape_failed = True
        st.markdown(
            "<p style='color: red;'>Gagal melakukan scraping. Pastikan URL valid dan didukung.</p>",
            unsafe_allow_html=True,
        )

# Add spacing for better UI appearance
st.markdown("<br><br>", unsafe_allow_html=True)

pages = {
    "✍️ Proses": "./pages/result.py",
    "🔗 Input dengan Konten": "./pages/content.py"
}

# Button for "Proses"
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Proses", use_container_width=True):
        if result:
            st.session_state.title = result["title"]
            st.session_state.content = result["content"]
            st.switch_page(pages["✍️ Proses"])
        elif not scrape_failed:
            st.markdown(
                "<p style='color: red;'>Data belum tersedia untuk diproses.</p>",
                unsafe_allow_html=True,
            )


# Add spacing between buttons
st.markdown("<br>", unsafe_allow_html=True)

# Button for "Input Using Judul dan Konten"
col4, col5, col6 = st.columns([1, 2, 1])
with col5:
    if st.button("Input Using Judul dan Konten", use_container_width=True):
        st.switch_page(pages["🔗 Input dengan Konten"])
