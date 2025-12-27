import os
import cv2
from PIL import Image, ImageDraw, ImageFont



def add_watermark_with_rotation(image_pil, watermark_text, rotation_angle=45):
    """Add repeated rotated watermark across full image"""
    img = image_pil.convert("RGBA")

    # Transparent layer same size as image
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Choose font
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Text size
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    textwidth = bbox[2] - bbox[0]
    textheight = bbox[3] - bbox[1]

    # Repeat text in grid pattern
    step_x = textwidth + 100   # horizontal gap
    step_y = textheight + 100  # vertical gap

    for y in range(0, img.height, step_y):
        for x in range(0, img.width, step_x):
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 120))

    # Rotate full text layer
    rotated = txt_layer.rotate(rotation_angle, expand=1)

    # Crop back to original size (after expand=1, layer becomes bigger)
    rotated = rotated.crop((0, 0, img.width, img.height))

    # Merge
    watermarked = Image.alpha_composite(img, rotated)
    return watermarked.convert("RGB")




def remove_watermark_and_compress(input_folder, output_folder,
                                  jpeg_quality=80, crop_percent=10,
                                  add_watermark=False,
                                  watermark_text="", rotation_angle=45):
    count = 0

    for root, dirs, files in os.walk(input_folder):
        rel_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, rel_path)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(root, filename)

                # Open with cv2 for cropping
                img_cv = cv2.imread(img_path)
                if img_cv is None:
                    print(f"⚠️ Skipped (unable to read): {filename}")
                    continue

                height, width = img_cv.shape[:2]
                crop_h = int(height * (1 - crop_percent / 100.0))
                img_cropped = img_cv[0:crop_h, 0:width]

                # Save temp cropped
                temp_path = os.path.join(output_subfolder, filename)
                cv2.imwrite(temp_path, img_cropped)

                # Open with PIL for compression / watermark
                img_pil = Image.open(temp_path)

                # Optional watermark
                if add_watermark and watermark_text.strip() != "":
                    img_pil = add_watermark_with_rotation(img_pil, watermark_text, rotation_angle)

                # Save compressed
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    img_pil = img_pil.convert("RGB")
                    img_pil.save(temp_path, format='JPEG', quality=jpeg_quality, optimize=True)
                elif filename.lower().endswith('.png'):
                    img_pil.save(temp_path, format='PNG', optimize=True)

                count += 1
                print(f"✅ Processed: {temp_path}")

    print(f"\n🎉 Done! {count} images processed. Cropped last {crop_percent}%, compressed, "
          f"{'with watermark' if add_watermark else 'without watermark'} saved in '{output_folder}'.")


# ===== MAIN SCRIPT =====
input_folder = r"D:\YoutubePoster\input\wallpapers\premsagar"
output_folder = r"D:\YoutubePoster\input\wallpapers\premsagar\final_compress"

print("\nCompression Quality Options:")
print("1. Low (50-60)  - Maximum compression, less quality")
print("2. Medium (75-85)  - Good compression, good quality (recommended)")
print("3. High (90-100)  - Minimum compression, best quality\n")

choice = input("Select compression type [1-Low, 2-Medium, 3-High]: ").strip()
if choice == '1':
    jpeg_quality = 55
elif choice == '2':
    jpeg_quality = 80
elif choice == '3':
    jpeg_quality = 95
else:
    print("Invalid choice, using Medium quality (80).")
    jpeg_quality = 80

# Crop % for removing watermark area
crop_percent = 10

# Ask for watermark option
add_watermark = input("Do you want to add custom watermark? (yes/no): ").strip().lower() == "yes"
watermark_text = ""
rotation_angle = 0
if add_watermark:
    watermark_text = input("Enter watermark text: ").strip()
    rotation_angle = int(input("Enter rotation angle in degrees (e.g., 45): ").strip())

# Run
remove_watermark_and_compress(input_folder, output_folder,
                              jpeg_quality, crop_percent,
                              add_watermark, watermark_text, rotation_angle)
