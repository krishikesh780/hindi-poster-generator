import streamlit as st
from PIL import Image
import io

st.title("📄 Bulk Image to PDF Converter")

uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    images = []
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file).convert('RGB')
        images.append(image)

    if st.button("🛠️ Convert to PDF"):
        if images:
            pdf_buffer = io.BytesIO()
            images[0].save(pdf_buffer, format="PDF", save_all=True, append_images=images[1:])
            st.download_button("⬇️ Download PDF", data=pdf_buffer.getvalue(),
                               file_name="bulk_images.pdf", mime="application/pdf")
            st.success("✅ PDF created successfully!")
        else:
            st.error("Please upload at least one image.")
else:
    st.info("Please upload some images to start.")
