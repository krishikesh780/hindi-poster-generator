import os
import hashlib

# =============================
# SETTINGS
# =============================
FOLDER_PATH = r"C:\Users\DELL\OneDrive\Desktop\ssc\ssc_papers"
CHUNK_SIZE = 1024 * 1024  # 1 MB chunks (memory-safe)

# =============================
# GET FILE HASH (MEMORY SAFE)
# =============================
def get_md5_hash(file_path):
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            md5.update(chunk)
    return md5.hexdigest()

# =============================
# DETECT DUPLICATES
# =============================
seen_hashes = {}
duplicate_files = []

for filename in os.listdir(FOLDER_PATH):
    if not filename.lower().endswith(".pdf"):
        continue

    full_path = os.path.join(FOLDER_PATH, filename)

    if not os.path.isfile(full_path):
        continue

    try:
        file_hash = get_md5_hash(full_path)

        if file_hash in seen_hashes:
            print(f"❌ Duplicate found:")
            print(f"   ➜ {filename}")
            print(f"   ➜ Original: {seen_hashes[file_hash]}\n")
            duplicate_files.append(full_path)
        else:
            seen_hashes[file_hash] = filename

    except Exception as e:
        print(f"⚠️ Error reading {filename}: {e}")

# =============================
# DELETE DUPLICATES
# =============================
for file_path in duplicate_files:
    try:
        os.remove(file_path)
        print(f"🗑️ Deleted: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"❌ Failed to delete {file_path}: {e}")

# =============================
# SUMMARY
# =============================
print("\n✅ DONE")
print(f"📂 Folder: {FOLDER_PATH}")
print(f"🧾 Total duplicates removed: {len(duplicate_files)}")
