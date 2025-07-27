import os
import json

# Set this to your wallpapers folder path
base_folder = r"D:\YoutubePoster\input\wallpapers-react"

# This will store our result
image_data = {}

for category in os.listdir(base_folder):
    category_path = os.path.join(base_folder, category)
    
    if os.path.isdir(category_path):
        images = []
        for file in os.listdir(category_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                # Save path relative to public folder (React will use it)
                relative_path = f"/img/wallpapers/{category}/{file}"
                images.append(relative_path)
        
        if images:
            image_data[category] = images

# Output JSON file to use in React
output_file = os.path.join(base_folder, "wallpapers.json")
with open(output_file, "w", encoding='utf-8') as f:
    json.dump(image_data, f, indent=2)

print("✅ JSON created:", output_file)
