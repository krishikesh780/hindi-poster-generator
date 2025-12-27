import os
import cv2
from PIL import Image

# =============================
# SETTINGS
# =============================
INPUT_FOLDER = r"D:\YoutubePoster\input\wallpapers\futureway\compress"
CROP_PERCENT = 10        # Bottom % to remove (watermark area)
JPEG_QUALITY = 85        # JPG quality (80–90 recommended)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# =============================
# VALIDATION
# =============================
if not os.path.isdir(INPUT_FOLDER):
    raise FileNotFoundError(f"Folder not found: {INPUT_FOLDER}")

image_count = 0

# =============================
# PROCESS IMAGES
# =============================
for filename in os.listdir(INPUT_FOLDER):
    if not filename.lower().endswith(IMAGE_EXTENSIONS):
        continue

    image_path = os.path.join(INPUT_FOLDER, filename)

    if not os.path.isfile(image_path):
        continue

    try:
        # ---- Read with OpenCV ----
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            print(f"⚠️ Skipped (cannot read): {filename}")
            continue

        h, w = img_cv.shape[:2]
        crop_h = int(h * (1 - CROP_PERCENT / 100))
        cropped_cv = img_cv[:crop_h, :]

        # ---- Convert to PIL for better saving ----
        img_pil = Image.fromarray(cv2.cvtColor(cropped_cv, cv2.COLOR_BGR2RGB))

        # ---- Save (overwrite safely) ----
        if filename.lower().endswith((".jpg", ".jpeg")):
            img_pil.save(
                image_path,
                format="JPEG",
                quality=JPEG_QUALITY,
                optimize=True
            )
        else:  # PNG
            img_pil.save(
                image_path,
                format="PNG",
                optimize=True
            )

        image_count += 1
        print(f"✅ Processed: {filename}")

    except Exception as e:
        print(f"❌ Failed: {filename} | Error: {e}")

# =============================
# SUMMARY
# =============================
print("\n🎉 DONE")
print(f"📂 Folder: {INPUT_FOLDER}")
print(f"🖼️ Images processed: {image_count}")
print(f"✂️ Cropped bottom: {CROP_PERCENT}%")
print(f"🗜️ JPEG Quality: {JPEG_QUALITY}")
