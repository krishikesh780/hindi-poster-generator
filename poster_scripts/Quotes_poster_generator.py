import os
import random
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageColor
import streamlit as st
import io
import zipfile
import cv2
from itertools import cycle, islice

# --- CONFIGURATION ---
st.set_page_config(page_title="🔥 Pro Poster Generator", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, '..', 'fonts')
WALLPAPER_FOLDER = os.path.join(BASE_DIR, '..', 'input', 'wallpapers')

FONT_OPTIONS = {
    "NotoSerifDevanagari": os.path.join(FONTS_DIR, "NotoSerifDevanagari-Regular.ttf"),
    "Baloo2-Regular": os.path.join(FONTS_DIR, "Baloo2-Regular.ttf"),
    "Hind-Regular": os.path.join(FONTS_DIR, "Hind-Regular.ttf"),
    "Mukta-Regular": os.path.join(FONTS_DIR, "Mukta-Regular.ttf"),
}

PLATFORM_DIMENSIONS = {
    "Facebook": (1200, 630),
    "Instagram": (1080, 1080),
    "WhatsApp Story": (1080, 1920),
    "YouTube Shorts": (1080, 1920)
}

# --- FUNCTIONS ---
def wrap_text(text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        test_line = line + word + " "
        if font.getlength(test_line) <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    if line:
        lines.append(line.strip())
    return lines

def draw_centered_text(draw_obj, lines, font, image_width, y_pos, text_color, bg_color, side_margin=60, line_padding=20, box_padding=20):
    for line in lines:
        text_width = font.getlength(line)
        text_height = font.getbbox(line)[3]
        x_pos = (image_width - text_width) / 2

        if bg_color:
            draw_obj.rectangle(
                [x_pos - box_padding, y_pos - box_padding / 2,
                 x_pos + text_width + box_padding,
                 y_pos + text_height + box_padding / 2],
                fill=bg_color
            )

        draw_obj.text((x_pos, y_pos), line, font=font, fill=text_color)
        y_pos += text_height + line_padding
    return y_pos

def add_watermark(image, text, font_path, font_size, color, rotation_angle, opacity_percent):
    watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    font = ImageFont.truetype(font_path, font_size)
    opacity = int(255 * (opacity_percent / 100))
    fill_color = ImageColor.getrgb(color) + (opacity,)
    text_width = font.getlength(text)
    text_height = font.getbbox(text)[3]
    spacing_x = int(text_width * 1.5)
    spacing_y = int(text_height * 2)

    for y in range(0, image.height, spacing_y):
        for x in range(0, image.width, spacing_x):
            draw.text((x, y), text, font=font, fill=fill_color)

    rotated = watermark.rotate(rotation_angle, expand=True)
    left = (rotated.width - image.width) // 2
    top = (rotated.height - image.height) // 2
    cropped = rotated.crop((left, top, left + image.width, top + image.height))
    return Image.alpha_composite(image.convert("RGBA"), cropped).convert("RGB")

def load_wallpapers_from_category(category_path):
    images = []
    files = [f for f in os.listdir(category_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for filename in files:
        image_path = os.path.join(category_path, filename)
        image_cv = cv2.imread(image_path)
        if image_cv is None:
            continue
        height, width = image_cv.shape[:2]
        crop_height = int(height * 0.95)
        cropped_image_cv = image_cv[0:crop_height, 0:width]
        cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image_cv, cv2.COLOR_BGR2RGB))
        images.append(cropped_image_pil)
    return images

def create_poster(image, main_text, author_name, font_path, font_size, author_font_size,
                  text_color, text_bg_color, author_color, author_bg_color, canvas_size,
                  watermark_text, watermark_font_size, watermark_color, rotation_angle, opacity_percent):

    image = image.convert("RGBA").resize(canvas_size)
    draw = ImageDraw.Draw(image)

    font_main = ImageFont.truetype(font_path, font_size)
    font_author = ImageFont.truetype(font_path, author_font_size)

    wrapped_lines = wrap_text(main_text, font_main, image.width - 120)
    total_text_height = sum([font_main.getbbox(line)[3] + 20 for line in wrapped_lines])
    total_text_height += font_author.getbbox(author_name)[3] + 30

    text_start_y = (image.height - total_text_height) / 2

    end_y = draw_centered_text(draw, wrapped_lines, font_main, image.width, text_start_y,
                               text_color, text_bg_color)
    draw_centered_text(draw, [author_name], font_author, image.width, end_y + 10,
                       author_color, author_bg_color)

    image = add_watermark(image, watermark_text, font_path, watermark_font_size,
                          watermark_color, rotation_angle, opacity_percent)
    return image.convert("RGB")

# --- LOAD DATA ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRkk7bFTbhrGOQzgCGjpe1Wn2hQVGgNEf7csf_uF-oOwdbvo6r6lU5tWZmXcYcaO9vC9WohilukPndv/pub?output=csv"
df_quotes = pd.read_csv(CSV_URL)
df_quotes = df_quotes[df_quotes['Status'].str.lower() == 'active']

# --- WALLPAPER SELECTION ---
wallpaper_categories = [name for name in os.listdir(WALLPAPER_FOLDER)
                        if os.path.isdir(os.path.join(WALLPAPER_FOLDER, name))]
selected_wallpaper_category = st.sidebar.selectbox("📂 Wallpaper Category", wallpaper_categories)
selected_wallpaper_category_path = os.path.join(WALLPAPER_FOLDER, selected_wallpaper_category)
wallpaper_images = load_wallpapers_from_category(selected_wallpaper_category_path)
random.shuffle(wallpaper_images)

# --- SIDEBAR SETTINGS ---
selected_platform = st.sidebar.selectbox("📱 Platform", list(PLATFORM_DIMENSIONS.keys()))
canvas_size = PLATFORM_DIMENSIONS[selected_platform]
selected_language = st.sidebar.radio("🌐 Language", ["Quotes-Hindi", "Quotes-English"])
selected_quote_category = st.sidebar.selectbox("📂 Quotes Category", df_quotes['Category'].unique())

filtered_df = df_quotes[(df_quotes['Category'] == selected_quote_category) & (df_quotes[selected_language].notnull())]
quotes_list = filtered_df[selected_language].tolist()

selected_font_path = FONT_OPTIONS[st.sidebar.selectbox("Font", list(FONT_OPTIONS.keys()))]
font_size = st.sidebar.slider("Font Size", 20, 100, 40)
author_font_size = st.sidebar.slider("Brand Font Size", 10, 60, 20)
text_color = st.sidebar.color_picker("Quotes Text Color", "#FFFFFF")
text_bg_color = None if st.sidebar.checkbox("Quotes BG Transparent", value=True) else st.sidebar.color_picker("Quotes BG Color", "#000000")
author_color = st.sidebar.color_picker("Author Text Color", "#FFFF00")
author_bg_color = None if st.sidebar.checkbox("Author BG Transparent", value=True) else st.sidebar.color_picker("Author BG Color", "#000000")
author_name = st.sidebar.text_input("Brand Name", "-By FutureWay Education")
poster_count = st.sidebar.slider("Number of Posters", 1, max(len(quotes_list), 1), 5)

with st.sidebar.expander("💧 Watermark Settings", expanded=False):
    watermark_text = st.text_area("Watermark Text", "Created by FutureWay")
    rotation_angle = st.slider("Rotation", 0, 180, 45)
    watermark_font_size = st.slider("Font Size", 10, 50, 20)
    watermark_color = st.color_picker("Color", "#CCCCCC")
    opacity_percent = st.slider("Opacity (%)", 5, 50, 15)

output_format = st.sidebar.radio("Output Format", ["JPEG", "PNG"])

# --- SESSION STATE ---
if 'gallery' not in st.session_state:
    st.session_state.gallery = []

# --- MAIN PAGE ---
st.title("🔥 Pro Poster Generator")

if st.button("🚀 Generate Posters", use_container_width=True):
    st.session_state.gallery = []
    zip_buffer = io.BytesIO()
    pdf_buffer = io.BytesIO()
    pdf_images = []
    progress = st.progress(0)

    wallpaper_cycle = cycle(wallpaper_images)
    wallpapers_to_use = list(islice(wallpaper_cycle, poster_count))
    quotes_sample = random.sample(quotes_list, poster_count)

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
        for idx, (quote, wallpaper) in enumerate(zip(quotes_sample, wallpapers_to_use), start=1):
            poster_img = create_poster(
                wallpaper.copy(),
                quote.strip(),
                author_name,
                selected_font_path,
                font_size,
                author_font_size,
                text_color,
                text_bg_color,
                author_color,
                author_bg_color,
                canvas_size,
                watermark_text,
                watermark_font_size,
                watermark_color,
                rotation_angle,
                opacity_percent
            )
            img_buffer = io.BytesIO()
            ext = "PNG" if output_format == "PNG" else "JPEG"
            poster_img.save(img_buffer, format=ext)
            zipf.writestr(f"{selected_quote_category}_poster_{idx}.{ext.lower()}", img_buffer.getvalue())
            st.session_state.gallery.append(poster_img)
            pdf_images.append(poster_img.convert("RGB"))
            progress.progress(idx / poster_count)

    if pdf_images:
        pdf_images[0].save(pdf_buffer, format="PDF", save_all=True, append_images=pdf_images[1:])

    st.download_button("⬇️ Download Posters (ZIP)", data=zip_buffer.getvalue(),
                       file_name=f"{selected_quote_category}_Posters.zip", mime="application/zip",
                       use_container_width=True)

    st.download_button("⬇️ Download All Posters (PDF)", data=pdf_buffer.getvalue(),
                       file_name=f"{selected_quote_category}_Posters.pdf", mime="application/pdf",
                       use_container_width=True)

    # --- 💧 Download Only Wallpapers with Watermark (No Quotes, No Author Name) ---
# --- 💧 Download Wallpapers with Only Watermark (No Quotes, No Brand) ---
if st.button("💧 Download Wallpapers with Watermark Only", use_container_width=True):
    zip_wallpaper_buffer = io.BytesIO()
    watermarked_gallery = []

    # Select N wallpapers regardless of quote category
    wallpapers_sample = list(islice(cycle(wallpaper_images), poster_count))

    with zipfile.ZipFile(zip_wallpaper_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
        for idx, wallpaper in enumerate(wallpapers_sample, start=1):
            # Only apply watermark (No quote, No brand)
            watermarked_img = add_watermark(
                wallpaper.copy(),
                watermark_text.strip(),             # User-entered watermark
                selected_font_path,
                watermark_font_size,
                watermark_color,
                rotation_angle,
                opacity_percent
            )

            img_buffer = io.BytesIO()
            ext = "PNG" if output_format == "PNG" else "JPEG"
            watermarked_img.save(img_buffer, format=ext)
            zipf.writestr(f"{selected_wallpaper_category}_wallpaper_{idx}.{ext.lower()}", img_buffer.getvalue())

            watermarked_gallery.append(watermarked_img)

    st.download_button("⬇️ Download Watermarked Wallpapers (ZIP)",
                       data=zip_wallpaper_buffer.getvalue(),
                       file_name=f"{selected_wallpaper_category}_Watermarked_Wallpapers.zip",
                       mime="application/zip",
                       use_container_width=True)

    st.subheader("🌄 Watermarked Wallpapers Preview")
    cols = st.columns(3)
    for idx, img in enumerate(watermarked_gallery):
        cols[idx % 3].image(img, caption=f"Wallpaper {idx+1}", use_container_width=True)


# --- GALLERY ---
st.subheader("🖼️ Generated Posters Gallery")
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, img in enumerate(st.session_state.gallery):
        cols[idx % 3].image(img, caption=f"Poster {idx+1}", use_container_width=True)
else:
    st.info("Please generate posters to see the gallery here.")
