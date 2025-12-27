import os

# =============================
# SETTINGS
# =============================
FOLDER_PATH = r"D:\YoutubePoster\input\wallpapers-gym"
START_NUMBER = 1

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

# =============================
# VALIDATE FOLDER
# =============================
if not os.path.isdir(FOLDER_PATH):
    raise FileNotFoundError(f"Folder not found: {FOLDER_PATH}")

# =============================
# LIST & SORT FILES
# =============================
files = sorted(os.listdir(FOLDER_PATH))

count = START_NUMBER

# =============================
# RENAME FILES SAFELY
# =============================
for filename in files:
    old_path = os.path.join(FOLDER_PATH, filename)

    # Skip folders
    if not os.path.isfile(old_path):
        continue

    # Rename only image files
    if not filename.lower().endswith(IMAGE_EXTENSIONS):
        continue

    _, ext = os.path.splitext(filename)
    new_name = f"{count}{ext}"
    new_path = os.path.join(FOLDER_PATH, new_name)

    # Avoid overwriting existing files
    if os.path.exists(new_path):
        print(f"⚠ Skipped (already exists): {new_name}")
        count += 1
        continue

    os.rename(old_path, new_path)
    print(f"✔ {filename} → {new_name}")

    count += 1

print("\n✅ Renaming completed successfully!")
