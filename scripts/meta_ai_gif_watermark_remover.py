import os
from PIL import Image, ImageSequence

# 🔥 Hardcoded Input Folder
input_folder = r"D:\YoutubePoster\input\wallpapers-father"  # Change this path

# Process GIFs
gif_count = 0

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.gif'):
        gif_path = os.path.join(input_folder, filename)
        img = Image.open(gif_path)

        frames = []
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGBA")

            width, height = frame.size
            crop_height = int(height * 0.95)
            cropped_frame = frame.crop((0, 0, width, crop_height))

            frames.append(cropped_frame)

        # Save cropped GIF (overwrite)
        output_path = os.path.join(input_folder, filename)
        frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, duration=img.info.get('duration', 100))

        gif_count += 1
        print(f"✅ Processed GIF: {filename}")

print(f"\n🎉 Done! {gif_count} GIFs processed. Watermark removed and saved in '{input_folder}'.")
