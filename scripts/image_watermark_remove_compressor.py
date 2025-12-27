


import os
from PIL import Image
import cv2




def remove_watermark_and_compress(input_folder, output_folder, jpeg_quality=80, crop_percent=10):
    # वॉटरमार्क हटाना और इमेज़ कम्प्रेस करना
    count = 0

    for root, dirs, files in os.walk(input_folder):
        rel_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, rel_path)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(root, filename)
                # Open image via OpenCV for cropping
                img_cv = cv2.imread(img_path)
                if img_cv is None:
                    print(f"⚠️ Skipped (unable to read): {filename}")
                    continue
                height, width = img_cv.shape[:2]
                crop_h = int(height * (1 - crop_percent / 100.0))
                img_cropped = img_cv[0:crop_h, 0:width]

                # Save temp-cropped image to memory (for PIL)
                temp_path = os.path.join(output_subfolder, filename)
                cv2.imwrite(temp_path, img_cropped)

                # Re-open cropped image with PIL for compression
                img_pil = Image.open(temp_path)
                # Save compressed file to output folder
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    img_pil = img_pil.convert("RGB")
                    img_pil.save(temp_path, format='JPEG', quality=jpeg_quality, optimize=True)
                elif filename.lower().endswith('.png'):
                    img_pil.save(temp_path, format='PNG', optimize=True)
                count += 1
                print(f"✅ Processed: {temp_path}")
    print(f"\n🎉 Done! {count} images processed. Watermark removed (last {crop_percent}% cropped) and compressed in '{output_folder}'.")

# ====== यूजर इनपुट्स (Customize Here):
input_folder = r"D:\Clients-Images\Perfect-Diagnostic\AI"
# output_folder = r"D:\YoutubePoster\input\wallpapers\Perpect-Diagnostic-Centre\final_compress"
output_folder = r"D:\Clients-Images\Perfect-Diagnostic\AI\final_compress"

print("\nCompression Quality Options:")
print("1. Low (50-60)  - Maximum compression, less quality")
print("2. Medium (75-85)  - Good compression, good quality (recommended)")
print("3. High (90-100)  - Minimum compression, best quality\n")
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

# Change this percentage if watermark area is different size
crop_percent = 10    # आखिरी 10% कटेंगे—अगर watermark छोटा है तो 5 भी कर सकते हैं

remove_watermark_and_compress(input_folder, output_folder, jpeg_quality, crop_percent)
