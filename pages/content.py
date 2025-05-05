import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title= "Klasifikasi Judul dan Berita Online",
    page_icon= "📰",
    initial_sidebar_state="collapsed",
)

# Title of the web app
st.markdown(
    "<h1 style='text-align: center;'>KLASIFIKASI<br>JUDUL DAN BERITA ONLINE</h1>",
    unsafe_allow_html=True,
)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Judul:</h4>", unsafe_allow_html=True)

# Input judul
user_input_title = st.text_input(
    label="Judul Input",
    placeholder="Judul",
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Konten:</h4>", unsafe_allow_html=True)

# Input konten
user_input_content = st.text_area(
    label="Konten Input",
    placeholder="Konten",
    label_visibility="collapsed",
)

# Add spacing for better UI appearance
st.markdown("<br><br>", unsafe_allow_html=True)


pages = {
    "✍️ Proses": "./pages/result.py",
    "🔗 Input dengan Link": "./pages/link.py"
}

# Tombol Proses
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Proses", use_container_width=True):
        if not user_input_title or not user_input_content:
            st.markdown(
                "<p style='color: red;'>Data belum tersedia untuk diproses</p>",
                unsafe_allow_html=True,
            )
        else:
            # Simpan judul dan konten ke session_state
            st.session_state.title = user_input_title
            st.session_state.content = user_input_content

            # Pindah ke halaman result
            st.switch_page(pages["✍️ Proses"])
    

# Add spacing between buttons
st.markdown("<br>", unsafe_allow_html=True)

# Tombol untuk kembali ke input via link
col4, col5, col6 = st.columns([1, 2, 1])
with col5:
    if st.button("Input Using Link", use_container_width=True):
        st.switch_page(pages["🔗 Input dengan Link"])


