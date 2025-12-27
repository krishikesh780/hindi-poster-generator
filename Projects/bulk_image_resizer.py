import os
from PIL import Image

# =============================
# SETTINGS
# =============================
INPUT_FOLDER = r"D:\YoutubePoster\input\image-bg"   # Source images
OUTPUT_FOLDER = r"D:\YoutubePoster\output\resized_images"
TARGET_SIZE = (1920, 1080)  # (width, height)

# =============================
# CREATE OUTPUT FOLDER
# =============================
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =============================
# IMAGE RESIZE PROCESS
# =============================
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        try:
            with Image.open(input_path) as img:
                # Convert RGBA / P mode images to RGB (important for JPG)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                resized_img = img.resize(TARGET_SIZE, Image.LANCZOS)
                resized_img.save(output_path, quality=95, optimize=True)

                print(f"✔ Resized: {filename}")

        except Exception as e:
            print(f"❌ Failed: {filename} | Error: {e}")

print(f"\n✅ All images resized to {TARGET_SIZE}")
print(f"📂 Output folder: {OUTPUT_FOLDER}")
