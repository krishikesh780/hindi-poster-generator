import os
from PIL import Image
import cv2

# =====================================================
# CORE FUNCTION
# =====================================================
def remove_watermark_and_compress(
    input_folder,
    output_folder,
    jpeg_quality=80,
    crop_percent=10
):
    """
    Removes bottom watermark by cropping last X%
    and compresses images while keeping folder structure.
    """
    count = 0

    for root, _, files in os.walk(input_folder):
        rel_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, rel_path)
        os.makedirs(output_subfolder, exist_ok=True)

        for filename in files:
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            input_path = os.path.join(root, filename)
            output_path = os.path.join(output_subfolder, filename)

            try:
                # ---------- READ IMAGE ----------
                img_cv = cv2.imread(input_path)
                if img_cv is None:
                    print(f"⚠️ Skipped (cannot read): {filename}")
                    continue

                h, w = img_cv.shape[:2]
                crop_h = int(h * (1 - crop_percent / 100))
                img_cropped = img_cv[:crop_h, :]

                # ---------- CONVERT TO PIL ----------
                img_pil = Image.fromarray(cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB))

                # ---------- SAVE COMPRESSED ----------
                if filename.lower().endswith((".jpg", ".jpeg")):
                    img_pil.save(
                        output_path,
                        format="JPEG",
                        quality=jpeg_quality,
                        optimize=True
                    )
                else:  # PNG
                    img_pil.save(
                        output_path,
                        format="PNG",
                        optimize=True
                    )

                count += 1
                print(f"✅ Processed: {output_path}")

            except Exception as e:
                print(f"❌ Failed: {filename} | Error: {e}")

    print("\n🎉 DONE")
    print(f"📂 Output folder: {output_folder}")
    print(f"🖼️ Total images processed: {count}")
    print(f"✂️ Cropped bottom: {crop_percent}%")
    print(f"🗜️ JPEG Quality: {jpeg_quality}")

# =====================================================
# USER CONFIGURATION
# =====================================================
INPUT_FOLDER = r"D:\Clients-Images\Perfect-Diagnostic\AI"
OUTPUT_FOLDER = r"D:\Clients-Images\Perfect-Diagnostic\AI\final_compress"

print("\nCompression Quality Options:")
print("1. Low (50–60)   → Maximum compression")
print("2. Medium (75–85) → Best balance (recommended)")
print("3. High (90–100) → Best quality\n")

choice = input("Select compression type [1 / 2 / 3]: ").strip()

if choice == "1":
    JPEG_QUALITY = 55
elif choice == "3":
    JPEG_QUALITY = 95
else:
    JPEG_QUALITY = 80  # default

CROP_PERCENT = 10  # Bottom watermark size (%)

# =====================================================
# RUN
# =====================================================
remove_watermark_and_compress(
    INPUT_FOLDER,
    OUTPUT_FOLDER,
    JPEG_QUALITY,
    CROP_PERCENT
)
