import streamlit as st
import plotly.graph_objects as go
from streamlit_extras.switch_page_button import switch_page
import pandas as pd

# Set Page Configuration
st.set_page_config(
    page_title="Landing Page - Klasifikasi Berita",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Title and Description
st.title("Klasifikasi Berita 📰")
st.write(
    """
    Selamat datang di aplikasi Klasifikasi Berita! 
    Aplikasi ini dirancang untuk membantu Anda menganalisis dan mengklasifikasikan berita berdasarkan kategori tertentu.
    Gunakan sidebar untuk mengunggah data atau memilih opsi yang tersedia.
    """
)

# Read data from CSV files
df1 = pd.read_csv('data/detik.csv')
df2 = pd.read_csv('data/kapanlagi.csv')
df3 = pd.read_csv('data/kompas.csv')
df4 = pd.read_csv('data/suara.csv')

# Extract labels and values from each dataset
labels1 = df1['Label'].value_counts().index.tolist()
values1 = df1['Label'].value_counts().values.tolist()
labels2 = df2['Label'].value_counts().index.tolist()
values2 = df2['Label'].value_counts().values.tolist()
labels3 = df3['Label'].value_counts().index.tolist()
values3 = df3['Label'].value_counts().values.tolist()
labels4 = df4['Label'].value_counts().index.tolist()
values4 = df4['Label'].value_counts().values.tolist()

# Define colors for the labels
color_map = {
    "nonrelevan": "#FF5733",
    "berlebihan": "#33FF57",
    "relevan": "#3357FF"
}

# Create pie charts with consistent colors
fig1 = go.Figure(data=[go.Pie(labels=labels1, values=values1, hole=0.3, marker=dict(colors=[color_map[label] for label in labels1]))])
fig2 = go.Figure(data=[go.Pie(labels=labels2, values=values2, hole=0.3, marker=dict(colors=[color_map[label] for label in labels2]))])
fig3 = go.Figure(data=[go.Pie(labels=labels3, values=values3, hole=0.3, marker=dict(colors=[color_map[label] for label in labels3]))])
fig4 = go.Figure(data=[go.Pie(labels=labels4, values=values4, hole=0.3, marker=dict(colors=[color_map[label] for label in labels4]))])

# Set transparent background for charts
for fig in [fig1, fig2, fig3, fig4]:
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=0, l=0, r=0)
    )

# Display the charts side by side with titles
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("Distribusi Label - Portal Detik")
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.write("Distribusi Label - Portal Kapanlagi")
    st.plotly_chart(fig2, use_container_width=True)
with col3:
    st.write("Distribusi Label - Portal Kompas")
    st.plotly_chart(fig3, use_container_width=True)
with col4:
    st.write("Distribusi Label - Portal Suara")
    st.plotly_chart(fig4, use_container_width=True)

# Create buttons for page navigation
col1, col2, col3 = st.columns([2, 1, 2])  # Center buttons
with col2:
    btn1 = st.button("Input dengan Link", use_container_width=True)
    btn2 = st.button("Input dengan Konten", use_container_width=True)

    if btn1:
        switch_page("link")
    if btn2:
        switch_page("content")
