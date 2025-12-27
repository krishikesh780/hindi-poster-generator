import os
import re

# Folder path
folder_path = r"C:\Users\DELL\Downloads\Social_Issues-20250920T174415Z-1-001\Social_Issues"

# Iterate over files in the folder
for filename in os.listdir(folder_path):
    old_path = os.path.join(folder_path, filename)

    # Skip if it's not a file
    if not os.path.isfile(old_path):
        continue

    # Extract only digits from filename (without extension)
    name, ext = os.path.splitext(filename)
    digits_only = re.sub(r"\D", "", name)  # remove everything except digits

    # If no digits found, skip renaming
    if not digits_only:
        continue

    new_filename = f"{digits_only}{ext}"
    new_path = os.path.join(folder_path, new_filename)

    # Rename file
    os.rename(old_path, new_path)
    print(f"Renamed: {filename} -> {new_filename}")

print("✅ Renaming completed!")
