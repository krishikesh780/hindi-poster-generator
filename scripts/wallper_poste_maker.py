


import cv2
import os
import numpy as np

# 📁 Input folder containing images
input_folder = r"D:\YoutubePoster\input\wallpapers\wallpapers-father"

# 🖋 Footer text
footer_text = "Address: Partawal Bazar, Maharajganj, Near Gorakhpur"  # Customize your footer text here
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1.0
font_color = (255, 255, 255)
thickness = 2

# 🖼 Logo path (can be transparent PNG)
logo_path = r"D:\YoutubePoster\logo.png"  # Change this path to your logo





# 🖼 Logo path
logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
if logo is None:
    raise FileNotFoundError(f"❌ Logo not found at: {logo_path}")

image_count = 0

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(input_folder, filename)
        image = cv2.imread(image_path)

        if image is None:
            print(f"⚠️ Skipped (unable to read): {filename}")
            continue

        # ✂️ Crop bottom 5%
        height, width = image.shape[:2]
        cropped_height = int(height * 0.95)
        image = image[0:cropped_height, :]

        # ➕ Create footer bar
        footer_height = 80
        footer_bar = np.zeros((footer_height, width, 3), dtype=np.uint8)

        # 📝 Auto-center footer text
        text_size = cv2.getTextSize(footer_text, font, font_scale, thickness)[0]
        text_x = (width - text_size[0]) // 2  # 👈 center horizontally
        text_y = (footer_height + text_size[1]) // 2
        cv2.putText(footer_bar, footer_text, (text_x, text_y), font, font_scale, font_color, thickness, cv2.LINE_AA)

        # 🔗 Combine image and footer
        final_image = np.vstack((image, footer_bar))

        # 🖼 Add logo at bottom-right
        logo_resized = cv2.resize(logo, (80, 80))
        y_offset = final_image.shape[0] - 80
        x_offset = final_image.shape[1] - 80

        if logo.shape[2] == 4:  # Transparent logo
            for c in range(0, 3):
                final_image[y_offset:y_offset+80, x_offset:x_offset+80, c] = (
                    logo_resized[:, :, c] * (logo_resized[:, :, 3] / 255.0) +
                    final_image[y_offset:y_offset+80, x_offset:x_offset+80, c] * (1.0 - logo_resized[:, :, 3] / 255.0)
                )
        else:
            final_image[y_offset:y_offset+80, x_offset:x_offset+80] = logo_resized

        # 💾 Save with full path display
        output_path = os.path.join(input_folder, filename)
        cv2.imwrite(output_path, final_image)

        image_count += 1
        print(f"✅ Processed: {filename}")
        print(f"📁 Saved at: {output_path}\n")

print(f"\n🎉 Done! {image_count} images processed with watermark removed, centered footer, and logo added.")
