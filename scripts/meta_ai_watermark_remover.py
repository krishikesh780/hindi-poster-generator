import cv2
import os

# 🔥 Hardcoded Input/Output Folder (Overwrite in same folder)
input_folder = r"D:\YoutubePoster\input\wallpapers-father"  # Change this path

# Process images
image_count = 0

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(input_folder, filename)
        image = cv2.imread(image_path)

        if image is None:
            print(f"⚠️ Skipped (unable to read): {filename}")
            continue

        # Crop last 5% (remove watermark)
        height, width = image.shape[:2]
        crop_height = int(height * 0.95)
        cropped_image = image[0:crop_height, 0:width]

        # Save cropped image (overwrite)
        output_path = os.path.join(input_folder, filename)
        cv2.imwrite(output_path, cropped_image)

        image_count += 1
        print(f"✅ Processed: {filename}")

print(f"\n🎉 Done! {image_count} images processed. Watermark removed and saved in '{input_folder}'.")
