import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import re
from transformers import AutoTokenizer, AutoModel, AutoConfig
from summarizer import Summarizer
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from huggingface_hub import hf_hub_download
import torch.nn.functional as F
import os

# Load tokenizer, config, dan model
custom_config = AutoConfig.from_pretrained("indobenchmark/indobert-base-p1")
custom_config.output_hidden_states = True

custom_tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
custom_model = AutoModel.from_pretrained("indobenchmark/indobert-base-p1", config=custom_config)

# Gunakan tokenizer dan model khusus untuk embedding
embedding_tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1", use_fast=True)
embedding_model = AutoModel.from_pretrained("indobenchmark/indobert-base-p1")

tokenizer = BertTokenizer.from_pretrained("indobenchmark/indobert-base-p2")

# Memuat model BERT untuk klasifikasi dengan jumlah label yang disesuaikan
model = BertForSequenceClassification.from_pretrained("indobenchmark/indobert-base-p2", num_labels=3)

# Menyesuaikan ukuran embedding model agar sesuai dengan ukuran kosakata checkpoint
model.resize_token_embeddings(50000)

# Memuat bobot model yang telah disimpan
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
token = os.environ.get("HF_TOKEN")
model_path = hf_hub_download(
    repo_id="picessakresna/model_relevansi_berita",
    filename="model_relevansi_berita_3.pth",
    use_auth_token=token
)
model.load_state_dict(torch.load(model_path, map_location=device), strict=False)
model.to(device)

# Inisialisasi model summarizer
summarizer_model = Summarizer(custom_model=custom_model, custom_tokenizer=custom_tokenizer)

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Klasifikasi Judul dan Berita Online",
    page_icon="📰",
    initial_sidebar_state="collapsed",
)

# Judul aplikasi
st.markdown(
    "<h1 style='text-align: center;'>KLASIFIKASI<br>JUDUL DAN BERITA ONLINE</h1>",
    unsafe_allow_html=True,
)

# Ambil data dari session state
title = st.session_state.get("title", "Judul belum tersedia")
content = st.session_state.get("content", "Konten belum tersedia")
source = st.session_state.get("source", "suara")

# Fungsi preprocessing
def remove_opening_sentences(text, source):
    if not isinstance(text, str):
        return text
    if source == "kompas":
        text = re.sub(r'^[A-Z\s]+,\s*KOMPAS\.com\s*[-–]?\s*', '', text)
        text = re.sub(r'KOMPAS\.com\s*[-–]?\s*', '', text)
    elif source == "suara":
        text = re.sub(r'Suara\.com\s*[-–]?\s*', '', text)
    return text

def format_date(text):
    if not isinstance(text, str):
        return text

    def replace_date(match):
        day, month, year = match.group(1), match.group(2), match.group(3) if match.lastindex == 3 else None
        month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                       "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        month_index = int(month) - 1
        if 0 <= month_index < len(month_names):
            return f"{day} {month_names[month_index]} {year}" if year else f"{day} {month_names[month_index]}"
        return match.group(0)

    text = re.sub(r'\((\d{1,2})/(\d{1,2})/(\d{4})\)', replace_date, text)
    text = re.sub(r'\((\d{1,2})/(\d{1,2})\)', replace_date, text)
    return text

def clean_text(text):
    if not isinstance(text, str):
        return text
    text = re.sub(r'Baca juga:.*?(?=\n|$)', '', text)
    text = re.sub(r'\nBaca Juga:.*?(\n|$)', '', text)
    text = re.sub(r'ADVERTISEMENT\s+.*?SCROLL TO CONTINUE WITH CONTENT', '', text, flags=re.DOTALL)
    text = re.sub(r'\[Gambas:.*?\]', '', text)
    text = re.sub(r"Lihat juga Video.*?:\s*.*?(\n|$)", '', text, flags=re.DOTALL)
    text = re.sub(r"[^a-zA-Z0-9\s.,\"'/?!]", "", text)
    text = re.sub(r'\n', ' ', text)
    return text

def preprocess_text(text):
    return text.strip()

# Preprocess judul dan konten
processed_title = clean_text(format_date(remove_opening_sentences(title, source)))
processed_content = clean_text(format_date(remove_opening_sentences(content, source)))

# Ringkasan
def summarize_article(title, content):
    preprocessed_title = preprocess_text(title)
    preprocessed_content = preprocess_text(content)
    combined_text = f"{preprocessed_title}. {preprocessed_content}"
    summary = summarizer_model(combined_text, ratio=0.5)
    summary_lines = summary.strip().split('. ')
    summary_title = summary_lines[0] if summary_lines else ""
    summary_content = '. '.join(summary_lines[1:]) if len(summary_lines) > 1 else ""
    return summary_title.strip(), summary_content.strip()

summary_title, summary_content = summarize_article(processed_title, processed_content)

# Ambil embedding untuk similarity
def get_embedding(text):
    tokens = embedding_tokenizer(text, padding='max_length', max_length=256, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = embedding_model(input_ids=tokens['input_ids'])
    embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding.squeeze().numpy()

title_embedding = get_embedding(summary_title)
content_embedding = get_embedding(summary_content)
similarity = cosine_similarity([title_embedding], [content_embedding])[0][0]

def classify_title_content(title, content):
    # Menggabungkan judul dan konten
    combined_text = f"{title} [SEP] {content}"
    
    # Melakukan tokenisasi input
    inputs = tokenizer(combined_text, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Melakukan inferensi
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = F.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = torch.max(probabilities).item()
    
    # Menentukan label berdasarkan prediksi
    labels = {0: "berlebihan", 1: "nonrelevan", 2: "relevan"}
    predicted_label = labels[predicted_class]
    
    return predicted_label, confidence

label, confidence = classify_title_content(summary_title, summary_content)

# Tampilkan hasil ke halaman
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Hasil Klasifikasi</h4>", unsafe_allow_html=True)
st.markdown(f"<h5 style='text-align: center;'>{label}</h5>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Tingkat Confidence</h4>", unsafe_allow_html=True)
st.markdown(f"<h5 style='text-align: center;'>{confidence:.3f}</h5>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Judul Berita</h4>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align: justify;'>{summary_title}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Isi Ringkasan</h4>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align: center;'>{summary_content}</div>", unsafe_allow_html=True)


pages = {
    "🔗 Input dengan Link": "./pages/link.py",
    "✍️ Input dengan Konten": "./pages/content.py"
}

# Tombol untuk pindah halaman
colA, colB, colC = st.columns([2, 1, 2])
with colB:
    if st.button("🔗 Input dengan Link", use_container_width=True):
        st.switch_page(pages["🔗 Input dengan Link"])
    if st.button("✍️ Input dengan Konten", use_container_width=True):
        st.switch_page(pages["✍️ Input dengan Konten"])