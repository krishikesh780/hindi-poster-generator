import os
from PIL import Image

# --- SETTINGS ---
input_folder = r'D:\YoutubePoster\input\image-bg'       # Folder with original images
output_folder = r'resized_images'    # Folder to save resized images
target_size = (1920, 1080)           # Desired size (width, height)

# Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# Process all images in input_folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        img = Image.open(image_path)
        resized_img = img.resize(target_size)   # Force resize to exact size

        resized_img.save(output_path)

print(f"✅ All images resized to {target_size} and saved in '{output_folder}' folder.")
