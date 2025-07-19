import cv2
import os

# Dynamic input/output folder paths from user
input_folder = input("📂 Enter input folder path (images folder): ").strip()
output_folder = input("💾 Enter output folder path (where images will be saved): ").strip()

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process images
image_count = 0

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(input_folder, filename)
        image = cv2.imread(image_path)

        # Crop last 5% to remove watermark
        height, width = image.shape[:2]
        crop_height = int(height * 0.95)
        cropped_image = image[0:crop_height, 0:width]

        # Save cropped image
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, cropped_image)

        image_count += 1
        print(f"✅ Processed: {filename}")

print(f"\n🎉 Done! {image_count} images processed. Watermark removed and saved to '{output_folder}'.")
