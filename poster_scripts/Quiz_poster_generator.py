

# import os
# import random
# import pandas as pd
# from PIL import Image, ImageDraw, ImageFont, ImageColor
# import streamlit as st
# import io
# import zipfile
# from matplotlib import pyplot as plt
# import cv2
# import numpy as np
# # --- CONFIGURATION ---
# st.set_page_config(page_title="🔥 Pro Quiz Poster Generator", layout="wide")

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FONTS_DIR = os.path.join(BASE_DIR, '..', 'fonts')
# WALLPAPER_FOLDER = os.path.join(BASE_DIR, '..', 'input', 'wallpapers')

# FONT_OPTIONS = {
#     "Baloo2-Regular": os.path.join(FONTS_DIR, "Baloo2-Regular.ttf"),
#     "Hind-Regular": os.path.join(FONTS_DIR, "Hind-Regular.ttf"),
#     "Mukta-Regular": os.path.join(FONTS_DIR, "Mukta-Regular.ttf"),
# }

# PLATFORM_DIMENSIONS = {
#     "Facebook": (1200, 630),
#     "Instagram": (1080, 1080),
#     "WhatsApp Story": (1080, 1920),
#     "YouTube Shorts": (1080, 1920)
# }

# # --- FUNCTIONS ---
# def wrap_text(text, font, max_width):
#     lines = []
#     for paragraph in text.split('\n'):
#         words = paragraph.split()
#         line = ""
#         for word in words:
#             test_line = line + word + " "
#             if font.getlength(test_line) <= max_width:
#                 line = test_line
#             else:
#                 lines.append(line.strip())
#                 line = word + " "
#         if line:
#             lines.append(line.strip())
#         lines.append("")
#     return lines

# def draw_centered_text(draw_obj, lines, font, image_width, y_pos, color, image):
#     for line in lines:
#         if "$" in line or "\\" in line:
#             fig, ax = plt.subplots()
#             fig.patch.set_visible(False)
#             ax.axis('off')
#             ax.text(0.5, 0.5, line, fontsize=font.size, color=color, ha='center', va='center', usetex=False)
#             fig.canvas.draw()
#             w, h = fig.canvas.get_width_height()
#             latex_img = Image.frombytes('RGB', (w, h), fig.canvas.tostring_rgb()).convert("RGBA")
#             latex_img = latex_img.crop(latex_img.getbbox())
#             x_pos = (image_width - latex_img.width) // 2
#             image.paste(latex_img, (x_pos, int(y_pos)), latex_img)
#             y_pos += latex_img.height + 10
#             plt.close(fig)
#         else:
#             text_width = font.getlength(line)
#             text_height = font.getbbox(line)[3]
#             x_pos = (image_width - text_width) / 2
#             draw_obj.text((x_pos, y_pos), line, font=font, fill=color)
#             y_pos += text_height + 10
#     return y_pos

# def generate_quiz_text(row, question_number, show_answer):
#     def safe_text(value):
#         return str(value).strip() if pd.notna(value) else "Not Provided"

#     question_text = safe_text(row['Question'])
#     option_a = safe_text(row['Option A'])
#     option_b = safe_text(row['Option B'])
#     option_c = safe_text(row['Option C'])
#     option_d = safe_text(row['Option D'])
#     answer_text = safe_text(row['Answer']) if 'Answer' in row else "Not Provided"

#     full_text = f"Q{question_number}. {question_text}\n\nA) {option_a}\nB) {option_b}\nC) {option_c}\nD) {option_d}"

#     if show_answer:
#         full_text += f"\n\nAnswer: {answer_text}"

#     return full_text

# def add_watermark(image, text, font_path, font_size, color, rotation_angle, opacity_percent):
#     watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
#     draw = ImageDraw.Draw(watermark)
#     font = ImageFont.truetype(font_path, font_size)
#     watermark_rgb = ImageColor.getrgb(color)
#     opacity = int(255 * (opacity_percent / 100))
#     fill_color = watermark_rgb + (opacity,)
#     text_lines = text.strip().split('\n')
#     block_height = sum([font.getbbox(line)[3] + 10 for line in text_lines])
#     block_width = max([font.getlength(line) for line in text_lines]) + 20
#     spacing_y = int(block_height * 2)
#     spacing_x = int(block_width * 1.5)
#     for y in range(0, image.height, spacing_y):
#         for x in range(0, image.width, spacing_x):
#             current_y = y
#             for line in text_lines:
#                 draw.text((x, current_y), line, font=font, fill=fill_color)
#                 current_y += font.getbbox(line)[3] + 5
#     rotated_watermark = watermark.rotate(rotation_angle, expand=True)
#     left = (rotated_watermark.width - image.width) // 2
#     top = (rotated_watermark.height - image.height) // 2
#     rotated_cropped = rotated_watermark.crop((left, top, left + image.width, top + image.height))
#     image = Image.alpha_composite(image.convert("RGBA"), rotated_cropped)
#     return image.convert("RGB")


# def load_wallpapers_without_watermark(folder_path):
#     processed_images = []

#     for filename in os.listdir(folder_path):
#         if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#             image_path = os.path.join(folder_path, filename)
#             image_cv = cv2.imread(image_path)

#             if image_cv is None:
#                 print(f"⚠️ Skipped (unable to read): {filename}")
#                 continue

#             # Crop last 5% (remove watermark)
#             height, width = image_cv.shape[:2]
#             crop_height = int(height * 0.95)
#             cropped_image_cv = image_cv[0:crop_height, 0:width]

#             # Convert OpenCV image to PIL format (RGB)
#             cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image_cv, cv2.COLOR_BGR2RGB))

#             processed_images.append(cropped_image_pil)

#     print(f"\n🎉 Loaded {len(processed_images)} watermark-free wallpapers.")
#     return processed_images


# def create_poster(image, main_text, font_path, font_size, text_color, canvas_size,
#                   watermark_text, watermark_font_size, watermark_color, rotation_angle, opacity_percent):
#     image = image.convert("RGBA").resize(canvas_size)
#     draw = ImageDraw.Draw(image)
#     font_main = ImageFont.truetype(font_path, font_size)
#     max_text_width = image.width - 100
#     wrapped_lines = wrap_text(main_text, font_main, max_text_width)
#     total_text_height = sum([font_main.getbbox(line)[3] + 10 for line in wrapped_lines])
#     text_start_y = (image.height - total_text_height) / 2
#     draw_centered_text(draw, wrapped_lines, font_main, image.width, text_start_y, text_color, image)
#     image = add_watermark(image, watermark_text, font_path, watermark_font_size,
#                           watermark_color, rotation_angle, opacity_percent)
#     return image.convert("RGB")


# # --- LOAD DATA ---
# SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJb689LR1ev_Y9xDq6Qv_hbtDWJCYlERLFy7NBhIaDayaB4df5Q8fi2jOwPT3W1bJZSqK8pr4kPbOQ/pub?output=xlsx"
# all_sheets = pd.read_excel(SHEET_URL, sheet_name=None)

# subject_names = list(all_sheets.keys())
# selected_subject = st.sidebar.selectbox("📚 Select Subject", subject_names)
# df_quiz = all_sheets[selected_subject]

# if not {'Topic', 'Question', 'Option A', 'Option B'}.issubset(df_quiz.columns):
#     st.error(f"⚠️ The sheet '{selected_subject}' is not formatted correctly.")
#     st.stop()

# unique_topics = sorted(df_quiz['Topic'].dropna().unique())
# selected_topic = st.sidebar.selectbox("📂 Select Topic", unique_topics)
# filtered_df = df_quiz[df_quiz['Topic'] == selected_topic]

# # wallpaper_images = [os.path.join(WALLPAPER_FOLDER, f)
# #                     for f in os.listdir(WALLPAPER_FOLDER)
# #                     if f.lower().endswith((".jpg", ".jpeg", ".png"))]

# wallpaper_images = load_wallpapers_without_watermark(WALLPAPER_FOLDER)

# # --- SESSION STATE ---
# if 'show_preview' not in st.session_state:
#     st.session_state.show_preview = True
# if 'generated_gallery' not in st.session_state:
#     st.session_state.generated_gallery = []

# # --- SIDEBAR SETTINGS ---
# selected_platform = st.sidebar.selectbox("Poster Format", list(PLATFORM_DIMENSIONS.keys()))
# canvas_size = PLATFORM_DIMENSIONS[selected_platform]
# selected_font_path = FONT_OPTIONS[st.sidebar.selectbox("Font", list(FONT_OPTIONS.keys()))]
# font_size = st.sidebar.slider("Font Size", 20, 100, 40)
# text_color = st.sidebar.color_picker("Text Color", "#FFFFFF")
# show_answer = st.sidebar.checkbox("Show Answers", True)
# question_mode = st.sidebar.radio("Question Mode", ["Sequential", "Random"])

# max_posters_limit = max(1, min(1000, len(filtered_df)))
# if max_posters_limit > 1:
#     poster_count = st.sidebar.slider("Number of Posters", 1, max_posters_limit, min(10, max_posters_limit))
# else:
#     poster_count = 1
#     st.sidebar.write("Only 1 poster available for this topic.")

# with st.sidebar.expander("💧 Watermark Settings", expanded=False):

#     watermark_text = st.text_area("Watermark Text", "Created by FutureWay")

#     rotation_angle = st.slider("Watermark Rotation", 0, 180, 45)
#     watermark_font_size = st.slider("Watermark Font Size", 20, 80, 40)
#     watermark_color = st.color_picker("Watermark Color", "#CCCCCC")
#     opacity_percent = st.slider("Watermark Opacity (%)", 5, 50, 15)

# with st.sidebar.expander("🛠️ Output Settings", expanded=False):
#     output_format = st.radio("Output Format", ["JPEG", "PNG"])

# # --- MAIN PAGE HEADER ---
# st.title("🔥 Pro Quiz Poster Generator")
# st.markdown(f"""
# <div style='background-color:#e0f7fa; padding:15px; border-radius:8px; 
#              font-size:18px; color:#00796b; font-weight:bold; text-align:center;'>
#     📂 Selected Subject : {selected_subject} | Topic : {selected_topic}
# </div><br>
# """, unsafe_allow_html=True)

# col_btn1, col_btn2 = st.columns([1, 1])
# with col_btn1:
#     btn_generate = st.button("🚀 Generate Posters", use_container_width=True)
# with col_btn2:
#     btn_reset = st.button("🔁 Reset Preview", use_container_width=True)

# if btn_generate:
#     st.session_state.show_preview = False
#     st.session_state.generated_gallery = []
#     zip_buffer = io.BytesIO()
#     pdf_buffer = io.BytesIO()
#     pdf_images = []
#     progress = st.progress(0)
#     poster_count_final = min(poster_count, len(filtered_df))
#     rows = filtered_df.sample(n=poster_count_final) if question_mode == "Random" else filtered_df.iloc[:poster_count_final]

#     with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
#         for idx, (_, row) in enumerate(rows.iterrows(), start=1):
#             quiz_text = generate_quiz_text(row, idx, show_answer)
#             # bg_image = Image.open(random.choice(wallpaper_images))
#             bg_image = random.choice(wallpaper_images)

#             poster_img = create_poster(
#                 bg_image.copy(), quiz_text, selected_font_path, font_size, text_color, canvas_size,
#                 watermark_text, watermark_font_size, watermark_color, rotation_angle, opacity_percent
#             )
#             img_buffer = io.BytesIO()
#             ext = "PNG" if output_format == "PNG" else "JPEG"
#             poster_img.save(img_buffer, format=ext)
#             zipf.writestr(f"{selected_topic}_poster_{idx}.{ext.lower()}", img_buffer.getvalue())
#             st.session_state.generated_gallery.append(poster_img)
#             pdf_images.append(poster_img.convert("RGB"))
#             progress.progress(idx / poster_count_final)

#     if pdf_images:
#         pdf_images[0].save(pdf_buffer, format="PDF", save_all=True, append_images=pdf_images[1:])

#     st.success(f"🎉 {poster_count_final} Posters Generated Successfully!")

#     st.download_button("⬇️ Download All Posters (ZIP)", data=zip_buffer.getvalue(),
#                        file_name=f"{selected_topic}_Quiz_Posters.zip", mime="application/zip",
#                        use_container_width=True)

#     st.download_button("⬇️ Download All Posters (PDF)", data=pdf_buffer.getvalue(),
#                        file_name=f"{selected_topic}_Quiz_Posters.pdf", mime="application/pdf",
#                        use_container_width=True)

# if btn_reset:
#     st.session_state.show_preview = True
#     st.session_state.generated_gallery = []

# st.subheader("🖼️ Output Gallery")
# if st.session_state.show_preview:
#     st.markdown("""
#     <div style='background-color:#f0f2f6; color:#f0f2f6; padding:20px; border-radius:10px; text-align:center; font-size:16px;'>
#         <b>This is Preview Area</b><br>
#         Click <b>'Generate Posters'</b> to display your quiz posters here.
#     </div><br>
#     """, unsafe_allow_html=True)
# else:
#     if st.session_state.generated_gallery:
#         cols = st.columns(3)
#         for idx, img in enumerate(st.session_state.generated_gallery):
#             cols[idx % 3].image(img, caption=f"Poster {idx+1}", use_container_width=True)
#     else:
#         st.warning("No posters generated yet.")

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
st.set_page_config(page_title="🔥 Pro Quiz Poster Generator", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, '..', 'fonts')
WALLPAPER_FOLDER = os.path.join(BASE_DIR, '..', 'input', 'wallpapers')

FONT_OPTIONS = {
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

    question_text = safe_text(row['Question'])
    option_a = safe_text(row['Option A'])
    option_b = safe_text(row['Option B'])
    option_c = safe_text(row['Option C'])
    option_d = safe_text(row['Option D'])
    answer_text = safe_text(row['Answer']) if 'Answer' in row else "Not Provided"

    full_text = f"Q{question_number}. {question_text}\n\nA) {option_a}\nB) {option_b}\nC) {option_c}\nD) {option_d}"
    if show_answer:
        full_text += f"\n\nAnswer: {answer_text}"
    return full_text

def load_wallpapers(category_path):
    images = []
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
    image = add_watermark(image, watermark_text, font_path, watermark_font_size,
                          watermark_color, rotation_angle, opacity_percent)
    return image.convert("RGB")

# --- LOAD DATA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJb689LR1ev_Y9xDq6Qv_hbtDWJCYlERLFy7NBhIaDayaB4df5Q8fi2jOwPT3W1bJZSqK8pr4kPbOQ/pub?output=xlsx"
all_sheets = pd.read_excel(SHEET_URL, sheet_name=None)
subject_names = list(all_sheets.keys())

wallpaper_categories = [name for name in os.listdir(WALLPAPER_FOLDER)
                        if os.path.isdir(os.path.join(WALLPAPER_FOLDER, name))]

# --- SIDEBAR SETTINGS ---
selected_wallpaper_category = st.sidebar.selectbox("📂 Wallpaper Category", wallpaper_categories)
wallpaper_images = load_wallpapers(os.path.join(WALLPAPER_FOLDER, selected_wallpaper_category))
random.shuffle(wallpaper_images)

selected_subject = st.sidebar.selectbox("📚 Select Subject", subject_names)
df_quiz = all_sheets[selected_subject]
unique_topics = sorted(df_quiz['Topic'].dropna().unique())
selected_topic = st.sidebar.selectbox("📂 Select Topic", unique_topics)
filtered_df = df_quiz[df_quiz['Topic'] == selected_topic]

selected_platform = st.sidebar.selectbox("Poster Format", list(PLATFORM_DIMENSIONS.keys()))
canvas_size = PLATFORM_DIMENSIONS[selected_platform]
selected_font_path = FONT_OPTIONS[st.sidebar.selectbox("Font", list(FONT_OPTIONS.keys()))]
font_size = st.sidebar.slider("Font Size", 20, 100, 40)
text_color = st.sidebar.color_picker("Text Color", "#FFFFFF")

bg_transparent = st.sidebar.checkbox("Background Transparent", value=True)
text_bg_color = None if bg_transparent else st.sidebar.color_picker("Text Background Color", "#000000")

show_answer = st.sidebar.checkbox("Show Answers", True)
question_mode = st.sidebar.radio("Question Mode", ["Sequential", "Random"])

poster_count = st.sidebar.slider("Number of Posters", 1, min(200, len(filtered_df)), min(10, len(filtered_df)))

with st.sidebar.expander("💧 Watermark Settings", expanded=False):
    watermark_text = st.text_area("Watermark Text", "Created by FutureWay")
    watermark_font_size = st.slider("Watermark Font Size", 20, 80, 40)
    watermark_color = st.color_picker("Watermark Color", "#CCCCCC")
    rotation_angle = st.slider("Watermark Rotation", 0, 180, 45)
    opacity_percent = st.slider("Watermark Opacity (%)", 5, 50, 15)

with st.sidebar.expander("🛠️ Output Settings", expanded=False):
    output_format = st.radio("Output Format", ["JPEG", "PNG"])

# --- SESSION STATE ---
if 'gallery' not in st.session_state:
    st.session_state.gallery = []

# --- MAIN PAGE ---
st.title("🔥 Pro Quiz Poster Generator")

if st.button("🚀 Generate Posters", use_container_width=True):
    st.session_state.gallery = []
    zip_buffer = io.BytesIO()
    pdf_buffer = io.BytesIO()
    pdf_images = []
    progress = st.progress(0)


    posters_to_generate = poster_count

    # ✅ Repeat wallpapers if less
    wallpaper_cycle = cycle(wallpaper_images)
    wallpapers_to_use = list(islice(wallpaper_cycle, posters_to_generate))

    quiz_rows = filtered_df.sample(n=posters_to_generate) if question_mode == "Random" else filtered_df.iloc[:posters_to_generate]

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
        for idx, (row, wallpaper) in enumerate(zip(quiz_rows.iterrows(), wallpapers_to_use), start=1):
            _, quiz_row = row
            quiz_text = generate_quiz_text(quiz_row, idx, show_answer)

            poster_img = create_poster(
                wallpaper.copy(), quiz_text, selected_font_path, font_size, text_color, text_bg_color, canvas_size,
                watermark_text, watermark_font_size, watermark_color, rotation_angle, opacity_percent
            )

            img_buffer = io.BytesIO()
            ext = "PNG" if output_format == "PNG" else "JPEG"
            poster_img.save(img_buffer, format=ext)
            zipf.writestr(f"{selected_topic}_poster_{idx}.{ext.lower()}", img_buffer.getvalue())

            st.session_state.gallery.append(poster_img)
            pdf_images.append(poster_img.convert("RGB"))
            progress.progress(idx / posters_to_generate)

    progress.progress(1.0)  # ✅ Optional: Complete Progress Bar

    # Save PDF
    if pdf_images:
        pdf_images[0].save(pdf_buffer, format="PDF", save_all=True, append_images=pdf_images[1:])

    # Download buttons
    st.download_button("⬇️ Download All Posters (ZIP)", data=zip_buffer.getvalue(),
                       file_name=f"{selected_topic}_Quiz_Posters.zip", mime="application/zip",
                       use_container_width=True)

    st.download_button("⬇️ Download All Posters (PDF)", data=pdf_buffer.getvalue(),
                       file_name=f"{selected_topic}_Quiz_Posters.pdf", mime="application/pdf",
                       use_container_width=True)


# --- GALLERY ---
st.subheader("🖼️ Generated Posters Gallery")
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, img in enumerate(st.session_state.gallery):
        cols[idx % 3].image(img, caption=f"Poster {idx+1}", use_container_width=True)
else:
    st.info("Please generate posters to view them here.")
