import os
import random
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import io
import zipfile

# ---------- CONFIGURATION ----------
st.set_page_config(page_title="Pro Poster Generator", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, '..', 'fonts')
WALLPAPER_FOLDER = os.path.join(BASE_DIR, '..', 'input' , 'wallpapers-bg')
DEFAULT_BG_PATH = os.path.join(BASE_DIR, 'default.jpeg')

FONT_OPTIONS = {
    "Baloo2-Regular": os.path.join(FONTS_DIR, "Baloo2-Regular.ttf"),
    "Baloo2-Bold": os.path.join(FONTS_DIR, "Baloo2-Bold.ttf"),
    "Hind-Regular": os.path.join(FONTS_DIR, "Hind-Regular.ttf"),
    "Hind-Bold": os.path.join(FONTS_DIR, "Hind-Bold.ttf"),
    "Mukta-Regular": os.path.join(FONTS_DIR, "Mukta-Regular.ttf"),
    "Mukta-Bold": os.path.join(FONTS_DIR, "Mukta-SemiBold.ttf"),
}

PLATFORM_DIMENSIONS = {
    "Facebook": (1200, 630),
    "Instagram": (1080, 1080),
    "WhatsApp Story": (1080, 1920),
    "YouTube Shorts": (1080, 1920)
}

# ---------- HELPER FUNCTIONS ----------
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

def draw_centered_text(draw_obj, lines, font, image_width, y_pos, color):
    for line in lines:
        text_width = font.getlength(line)
        text_height = font.getbbox(line)[3]
        x_pos = (image_width - text_width) / 2
        draw_obj.text((x_pos, y_pos), line, font=font, fill=color)
        y_pos += text_height + 10
    return y_pos

def apply_brand_logo(image, logo_image, position_choice):
    if logo_image is None:
        return image

    logo = Image.open(logo_image).convert("RGBA")
    wm_width = int(image.width * 0.1)
    wm_height = int(logo.height * (wm_width / logo.width))
    logo = logo.resize((wm_width, wm_height), Image.LANCZOS)

    # Position logic
    positions = {
        "Top-Left": (20, 20),
        "Top-Right": (image.width - wm_width - 20, 20),
        "Bottom-Left": (20, image.height - wm_height - 20),
        "Bottom-Right": (image.width - wm_width - 20, image.height - wm_height - 20),
    }
    position = positions.get(position_choice, positions["Bottom-Right"])

    image.paste(logo, position, mask=logo)
    return image

def create_poster(image, main_text, author_name, font_path, font_size, author_font_size, text_color, author_color, canvas_size, brand_logo_file, logo_position):
    image = image.convert("RGBA").resize(canvas_size)
    draw = ImageDraw.Draw(image)
    font_main = ImageFont.truetype(font_path, font_size)
    font_author = ImageFont.truetype(font_path, author_font_size)
    max_text_width = image.width - 100
    wrapped_lines = wrap_text(main_text, font_main, max_text_width)
    total_text_height = sum([font_main.getbbox(line)[3] + 10 for line in wrapped_lines])
    total_text_height += font_author.getbbox(author_name)[3] + 20
    text_start_y = (image.height - total_text_height) / 2
    end_y = draw_centered_text(draw, wrapped_lines, font_main, image.width, text_start_y, text_color)
    author_x = (image.width - font_author.getlength(author_name)) / 2
    draw.text((author_x, end_y + 10), author_name, font=font_author, fill=author_color)

    # Apply uploaded brand/logo image
    image = apply_brand_logo(image, brand_logo_file, logo_position)

    return image.convert("RGB")

# ---------- LOAD DATA ----------
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRkk7bFTbhrGOQzgCGjpe1Wn2hQVGgNEf7csf_uF-oOwdbvo6r6lU5tWZmXcYcaO9vC9WohilukPndv/pub?output=csv"
df_quotes = pd.read_csv(CSV_URL)
df_quotes = df_quotes[df_quotes['Status'].str.lower() == 'active']

wallpaper_images = [os.path.join(WALLPAPER_FOLDER, f)
                    for f in os.listdir(WALLPAPER_FOLDER)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))]

# ---------- SIDEBAR (Sticky Control Panel) ----------
st.sidebar.title("🎛️ Poster Design Settings")

selected_platform = st.sidebar.selectbox("📱 Social Network", list(PLATFORM_DIMENSIONS.keys()))
canvas_size = PLATFORM_DIMENSIONS[selected_platform]

selected_language = st.sidebar.radio("🌐 Language", ["Quotes-Hindi", "Quotes-English"])
selected_category = st.sidebar.selectbox("📂 Quote Category", df_quotes['Category'].unique())

filtered_df = df_quotes[(df_quotes['Category'] == selected_category) & (df_quotes[selected_language].notnull())]
quotes_list = filtered_df[selected_language].tolist()
total_quotes = len(quotes_list)
poster_count = st.sidebar.number_input(f"How many posters? (Max: {total_quotes})", 1, total_quotes, min(10, total_quotes))

st.sidebar.markdown(f"**📝 Total Active Quotes:** {total_quotes}")

# Upload brand/logo image
brand_logo_file = st.sidebar.file_uploader("📥 Upload Brand/Logo Image (PNG recommended)")

# Logo position choice
logo_position = st.sidebar.selectbox("🖼️ Logo Position", ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"])

with st.sidebar.expander("🎨 Advanced Styling"):
    selected_font_name = st.selectbox("Font", list(FONT_OPTIONS.keys()))
    selected_font_path = FONT_OPTIONS[selected_font_name]
    font_size = st.slider("Font Size", 20, 150, 50)
    author_font_size = st.slider("Brand Size", 10, 80, 25)
    text_color = st.color_picker("Text Color", "#FFFFFF")
    author_color = st.color_picker("Brand Color", "#FFFF00")
    author_name = st.text_input("Brand Name", "By Futureway Classes")

live_preview = st.sidebar.toggle("🖼️ Enable Live Poster Preview", value=True)

# ---------- MAIN WORK AREA ----------
st.title("🖌️ Pro  Poster Generator")

st.info(f"Posters will be generated in **{selected_platform}** format ({canvas_size[0]}×{canvas_size[1]} pixels).")

generate_button = st.button("🚀 Generate Posters", type="primary")

# ---------- POSTER GENERATION ----------
if generate_button:
    st.subheader(f"Generating {poster_count} Posters...")

    zip_buffer = io.BytesIO()
    progress = st.progress(0)

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
        for idx, quote in enumerate(random.sample(quotes_list, poster_count), start=1):
            wallpaper_path = random.choice(wallpaper_images)
            bg_image = Image.open(wallpaper_path)

            poster_img = create_poster(
                bg_image.copy(),
                quote.strip(),
                author_name,
                selected_font_path,
                font_size,
                author_font_size,
                text_color,
                author_color,
                canvas_size,
                brand_logo_file,
                logo_position
            )

            img_buffer = io.BytesIO()
            poster_img.save(img_buffer, format="JPEG")
            zipf.writestr(f"poster_{idx}.jpg", img_buffer.getvalue())

            if live_preview:
                st.image(poster_img, caption=f"Poster {idx}", use_container_width=True)



            progress.progress(idx / poster_count)

    st.success(f"🎉 {poster_count} Posters Ready for Download!")
    zip_size = zip_buffer.tell() / 1024
    st.write(f"📦 ZIP Size: {zip_size:.2f} KB")

    zip_buffer.seek(0)
    st.download_button(
        label="⬇️ Download ZIP File",
        data=zip_buffer,
        file_name=f"{selected_category}_{selected_language}_{selected_platform}_posters.zip",
        mime="application/zip"
    )




# ---------- DEFAULT POSTER PREVIEW ----------
if not generate_button:
    bg_image = Image.open(DEFAULT_BG_PATH)

    if selected_language == "Quotes-Hindi":
        default_text = "यह एक डेमो पोस्टर है।\nअपना टेक्स्ट यहाँ लिखें।"
    else:
        default_text = "This is a demo poster.\nWrite your text here."

    poster_img = create_poster(
        bg_image.copy(),
        default_text,
        author_name,
        selected_font_path,
        font_size,
        author_font_size,
        text_color,
        author_color,
        canvas_size,
        brand_logo_file,
        logo_position
    )
    st.subheader("🎬 Default Poster Preview")
    st.image(poster_img, caption="Default Preview", use_container_width=True)
