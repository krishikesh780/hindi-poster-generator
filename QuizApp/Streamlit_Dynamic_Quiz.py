import os
import random
import pandas as pd
import json
from PIL import Image, ImageDraw, ImageFont, ImageColor
import streamlit as st
import io
import zipfile
import cv2
from itertools import cycle, islice

# --- BASE DIR ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CONFIG LOAD ---
try:
    with open(os.path.join(BASE_DIR, "data.json"), "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except Exception as e:
    st.error(f"❌ Failed to load config: {e}")
    st.stop()

# --- EXTRACT CONFIG DATA ---
FONT_OPTIONS = {
    name: os.path.join(BASE_DIR, path)
    for name, path in CONFIG["font_options"].items()
}
PLATFORM_DIMENSIONS = {
    name: tuple(dim)
    for name, dim in CONFIG["platform_dimensions"].items()
}
defaults = CONFIG["defaults"]
watermark_defaults = defaults["watermark"]
labels = CONFIG["labels"]

# --- STREAMLIT CONFIG ---
st.set_page_config(page_title=labels["app_title"], layout="wide")

# --- PATH SETUP ---
FONTS_DIR = os.path.join(BASE_DIR, '..', 'fonts')
WALLPAPER_FOLDER = os.path.join(BASE_DIR, '..', 'input', 'Question-Wallpapers')

# --- CACHING ---
@st.cache_data
def load_excel(url):
    return pd.read_excel(url, sheet_name=None)

@st.cache_resource
def load_wallpapers_cached(category_path):
    return load_wallpapers(category_path)

# --- HELPER FUNCTIONS ---
def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if font.getlength(test_line) <= max_width:
                line = test_line
            else:
                lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())
        lines.append("")
    return lines

def draw_centered_text(draw_obj, lines, font, image_width, y_pos, color, bg_color):
    for line in lines:
        text_width = font.getlength(line)
        text_height = font.getbbox(line)[3]
        x_pos = (image_width - text_width) / 2
        if bg_color:
            draw_obj.rectangle(
                [x_pos - 10, y_pos - 5, x_pos + text_width + 10, y_pos + text_height + 5],
                fill=bg_color
            )
        draw_obj.text((x_pos, y_pos), line, font=font, fill=color)
        y_pos += text_height + 10
    return y_pos

def add_watermark(image, text, font_path, font_size, color, rotation_angle, opacity_percent):
    watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    font = ImageFont.truetype(font_path, font_size)
    opacity = int(255 * (opacity_percent / 100))
    fill_color = ImageColor.getrgb(color) + (opacity,)
    spacing_x = int(font.getlength(text) * 1.5)
    spacing_y = int(font_size * 2)

    for y in range(0, image.height, spacing_y):
        for x in range(0, image.width, spacing_x):
            draw.text((x, y), text, font=font, fill=fill_color)

    rotated = watermark.rotate(rotation_angle, expand=True)
    left = (rotated.width - image.width) // 2
    top = (rotated.height - image.height) // 2
    cropped = rotated.crop((left, top, left + image.width, top + image.height))
    return Image.alpha_composite(image.convert("RGBA"), cropped).convert("RGB")

def generate_quiz_text(row, question_number, show_answer):
    def safe_text(value):
        return str(value).strip() if pd.notna(value) else "Not Provided"

    question_text = safe_text(row.get('Question'))
    option_a = safe_text(row.get('Option A'))
    option_b = safe_text(row.get('Option B'))
    option_c = safe_text(row.get('Option C'))
    option_d = safe_text(row.get('Option D'))
    answer_text = safe_text(row.get('Answer')) if 'Answer' in row else "Not Provided"

    full_text = f"Q{question_number}. {question_text}\n\nA) {option_a}\nB) {option_b}\nC) {option_c}\nD) {option_d}"
    if show_answer:
        full_text += f"\n\nAnswer: {answer_text}"
    return full_text

def load_wallpapers(category_path):
    images = []
    if not os.path.exists(category_path):
        return images
    for filename in os.listdir(category_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
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

def create_poster(image, main_text, font_path, font_size, text_color, text_bg_color, canvas_size,
                  watermark_text, watermark_font_size, watermark_color, rotation_angle, opacity_percent):
    image = image.convert("RGBA").resize(canvas_size)
    draw = ImageDraw.Draw(image)
    font_main = ImageFont.truetype(font_path, font_size)
    max_text_width = image.width - 100
    wrapped_lines = wrap_text(main_text, font_main, max_text_width)
    total_text_height = sum([font_main.getbbox(line)[3] + 10 for line in wrapped_lines])
    text_start_y = (image.height - total_text_height) / 2
    draw_centered_text(draw, wrapped_lines, font_main, image.width, text_start_y, text_color, text_bg_color)
    image = add_watermark(image, watermark_text, font_path, watermark_font_size, watermark_color, rotation_angle, opacity_percent)
    return image.convert("RGB")

# --- LOAD DATA ---
SHEET_URL = CONFIG.get("sheet_url", "")
all_sheets = load_excel(SHEET_URL)

if not all_sheets:
    st.warning("⚠️ No sheets found in the Excel file.")
    st.stop()

subject_names = list(all_sheets.keys())
wallpaper_categories = [name for name in os.listdir(WALLPAPER_FOLDER)
                        if os.path.isdir(os.path.join(WALLPAPER_FOLDER, name))]

if not wallpaper_categories:
    st.warning("⚠️ No wallpaper categories found.")
    st.stop()

# --- SIDEBAR ---
selected_wallpaper_category = st.sidebar.selectbox(labels["wallpaper_category"], wallpaper_categories)
wallpaper_images = load_wallpapers_cached(os.path.join(WALLPAPER_FOLDER, selected_wallpaper_category))
if not wallpaper_images:
    st.warning("⚠️ No valid wallpaper images found.")
    st.stop()

random.shuffle(wallpaper_images)

selected_subject = st.sidebar.selectbox(labels["subject"], subject_names)
df_quiz = all_sheets[selected_subject]
if "Topic" not in df_quiz.columns:
    st.error("❌ 'Topic' column missing in selected sheet.")
    st.stop()

unique_topics = sorted(df_quiz['Topic'].dropna().unique())
selected_topic = st.sidebar.selectbox(labels["topic"], unique_topics)
filtered_df = df_quiz[df_quiz['Topic'] == selected_topic]
if filtered_df.empty:
    st.warning("⚠️ No quiz data found for selected topic.")
    st.stop()

selected_platform = st.sidebar.selectbox(labels["poster_format"], list(PLATFORM_DIMENSIONS.keys()))
canvas_size = PLATFORM_DIMENSIONS[selected_platform]

selected_font_path = FONT_OPTIONS[st.sidebar.selectbox(labels["font"], list(FONT_OPTIONS.keys()))]
font_size = st.sidebar.slider(labels["font_size"], 20, 100, defaults["font_size"])
text_color = st.sidebar.color_picker(labels["text_color"], defaults["text_color"])
bg_transparent = st.sidebar.checkbox(labels["bg_transparent"], value=defaults["bg_transparent"])
text_bg_color = None if bg_transparent else st.sidebar.color_picker(labels["text_bg_color"], defaults["text_bg_color"])
show_answer = st.sidebar.checkbox(labels["show_answer"], defaults["show_answer"])

question_mode = st.sidebar.radio(
    labels["question_mode"],
    labels["question_mode_options"],
    index=0 if defaults["question_mode"] == "Sequential" else 1
)

poster_count = st.sidebar.slider(labels["poster_count"], 1, min(200, len(filtered_df)),
                                 min(defaults["poster_count"], len(filtered_df)))

with st.sidebar.expander(labels["watermark_section"], expanded=False):
    watermark_text = st.text_area(labels["watermark_text"], watermark_defaults["text"])
    watermark_font_size = st.slider(labels["watermark_font_size"], 20, 80, watermark_defaults["font_size"])
    watermark_color = st.color_picker(labels["watermark_color"], watermark_defaults["color"])
    rotation_angle = st.slider(labels["watermark_rotation"], 0, 180, watermark_defaults["rotation"])
    opacity_percent = st.slider(labels["watermark_opacity"], 5, 50, watermark_defaults["opacity"])

with st.sidebar.expander(labels["output_settings"], expanded=False):
    output_format = st.radio(labels["output_format"], labels["output_format_options"],
                             index=0 if defaults["output_format"] == "JPEG" else 1)

# --- SESSION ---
if 'gallery' not in st.session_state:
    st.session_state.gallery = []

# --- UI ---
st.title(labels["app_title"])

if st.button(labels["generate_button"], use_container_width=True):
    st.session_state.gallery = []
    progress = st.progress(0)

    posters_to_generate = poster_count
    wallpaper_cycle = cycle(wallpaper_images)
    wallpapers_to_use = list(islice(wallpaper_cycle, posters_to_generate))
    quiz_rows = filtered_df.sample(n=posters_to_generate) if question_mode == "Random" else filtered_df.iloc[:posters_to_generate]

    for idx, (row, wallpaper) in enumerate(zip(quiz_rows.iterrows(), wallpapers_to_use), start=1):
        _, quiz_row = row
        quiz_text = generate_quiz_text(quiz_row, idx, show_answer)
        poster_img = create_poster(
            wallpaper.copy(), quiz_text, selected_font_path, font_size, text_color, text_bg_color, canvas_size,
            watermark_text, watermark_font_size, watermark_color, rotation_angle, opacity_percent
        )
        st.session_state.gallery.append(poster_img)
        progress.progress(idx / posters_to_generate)

# --- DOWNLOADS ---
if st.session_state.gallery:
    with st.expander("⬇️ Download Options", expanded=True):
        # ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
            for idx, img in enumerate(st.session_state.gallery, start=1):
                buf = io.BytesIO()
                ext = "PNG" if output_format == "PNG" else "JPEG"
                img.save(buf, format=ext)
                zipf.writestr(f"{selected_topic}_poster_{idx}.{ext.lower()}", buf.getvalue())
        st.download_button("⬇️ Download ZIP", data=zip_buffer.getvalue(),
                           file_name=f"{selected_topic}_Quiz_Posters.zip", mime="application/zip")

        # PDF (on demand)
        if st.button("📄 Generate PDF"):
            pdf_buffer = io.BytesIO()
            st.session_state.gallery[0].save(pdf_buffer, format="PDF", save_all=True,
                                             append_images=st.session_state.gallery[1:])
            st.download_button("⬇️ Download PDF", data=pdf_buffer.getvalue(),
                               file_name=f"{selected_topic}_Quiz_Posters.pdf", mime="application/pdf")

# --- GALLERY ---
st.subheader(labels["gallery_title"])
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, img in enumerate(st.session_state.gallery):
        cols[idx % 3].image(img, caption=f"Poster {idx+1}", use_container_width=True)
else:
    st.info(labels["empty_gallery_msg"])
