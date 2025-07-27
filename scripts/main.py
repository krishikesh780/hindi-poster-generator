import streamlit as st
from PIL import Image
import pandas as pd
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="FutureWay Studio", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f8fafc;
    }
    .header {
        position: fixed;
        top: 0;
        width: 100%;
        background-color: #0f172a;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 15px 30px;
        text-align: center;
        z-index: 1000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
        
    [data-testid="stSidebar"] {
        position: fixed;
        top: 60px;
        left: 0;
        width: 250px;
        height: calc(100% - 60px);
        background-color: #f8fafc;
        padding: 10px;
        overflow-y: auto;
        box-shadow: 2px 0 8px rgba(0,0,0,0.08);
        color: #1e293b;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #0f172a;
    }
    [data-testid="stAppViewContainer"] > .main {
        margin-top: 60px;
        margin-left: 270px;
        padding: 20px;
    }
    .canvas-area {
        background-color: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 10px;
        min-height: 400px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 18px;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 20px;
    }
    .gallery-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 15px;
    }
    .gallery-item {
        width: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .gallery-item:hover {
        transform: scale(1.05);
    }
    h1, h2, h3 {
        color: #0ea5e9;
    }
    .stButton button {
        background-color: #0ea5e9 !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 20px;
    }
    /* Sidebar Radio Button Labels - Dark Color & Bold */
    [role="radiogroup"] label > div {
        color: #0f172a !important;  /* Dark navy color */
        font-weight: 700 !important; /* Bold */
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header">🔥 FutureWay Studio — All Tools in One Dashboard</div>', unsafe_allow_html=True)

# --- SIDEBAR TOOL SELECTION ---
with st.sidebar:
    st.title("🎛️ Select Tool")
    selected_tool = st.radio("", ["📑 Bulk Image to PDF", "💬 Bulk Quote Generator", "📝 Quiz Poster Generator"])

    st.markdown("---")
    st.subheader("🛠️ Tool Settings")

# --- MAIN CONTENT ---
st.title(f"🚀 {selected_tool} — Output & Preview")

# --- TOOL LOGIC ---

# 1️⃣ BULK IMAGE TO PDF
if selected_tool == "📑 Bulk Image to PDF":
    uploaded_images = st.sidebar.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    pdf_button = st.sidebar.button("Generate PDF")
    st.markdown('<div class="canvas-area">Image Upload Preview</div>', unsafe_allow_html=True)

    if uploaded_images:
        cols = st.columns(3)
        image_objects = []
        for idx, uploaded_file in enumerate(uploaded_images):
            img = Image.open(uploaded_file)
            image_objects.append(img.convert("RGB"))
            cols[idx % 3].image(img, caption=f"Image {idx+1}", use_column_width=True)

        if pdf_button and image_objects:
            pdf_buffer = io.BytesIO()
            image_objects[0].save(pdf_buffer, format="PDF", save_all=True, append_images=image_objects[1:])
            st.download_button("⬇️ Download PDF", data=pdf_buffer.getvalue(),
                               file_name="bulk_images.pdf", mime="application/pdf", use_container_width=True)

# 2️⃣ BULK QUOTE GENERATOR
elif selected_tool == "💬 Bulk Quote Generator":
    quotes_text = st.sidebar.text_area("Enter Quotes (one per line):", height=200)
    bg_color = st.sidebar.color_picker("Background Color", "#f8fafc")
    st.markdown(f'<div class="canvas-area" style="background-color:{bg_color};">Generated Quotes Preview</div>', unsafe_allow_html=True)

    if quotes_text.strip():
        st.subheader("📋 Generated Quotes")
        quotes = [q.strip() for q in quotes_text.strip().split("\n") if q.strip()]
        cols = st.columns(2)
        for idx, quote in enumerate(quotes):
            cols[idx % 2].markdown(f"""
                <div style='background-color:{bg_color};padding:15px;border-radius:10px;
                             margin-bottom:15px;box-shadow:0 1px 4px rgba(0,0,0,0.1);
                             color:#1e293b;font-weight:500;'>
                    {quote}
                </div>
            """, unsafe_allow_html=True)



# 3️⃣ QUIZ POSTER GENERATOR (Placeholder)
elif selected_tool == "📝 Quiz Poster Generator":
    sample_quiz_df = pd.DataFrame({
        "Q": ["What is 2+2?", "Capital of India?"],
        "A": ["4", "New Delhi"]
    })

    poster_count = st.sidebar.slider("Number of Posters", 1, 10, 2)
    st.markdown('<div class="canvas-area">Quiz Posters Output Preview</div>', unsafe_allow_html=True)

    st.subheader("🖼️ Generated Quiz Posters (Demo)")

    cols = st.columns(3)
    for i in range(poster_count):
        cols[i % 3].image("https://via.placeholder.com/300x400.png?text=Poster+" + str(i+1),
                          caption=f"Poster {i+1}", use_column_width=True)

# --- FOOTER ---
st.markdown("---")
st.info("FutureWay Studio — All rights reserved © 2025")
