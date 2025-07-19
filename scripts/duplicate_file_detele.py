import os
import hashlib

# === Your Folder Path ===
folder_path = r"C:\Users\DELL\OneDrive\Desktop\ssc\ssc_papers"

# === Get File Hash ===
def get_md5_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# === Detect and Delete Duplicates ===
seen_hashes = {}
duplicate_files = []

for filename in os.listdir(folder_path):
    if not filename.endswith(".pdf"):
        continue

    full_path = os.path.join(folder_path, filename)
    file_hash = get_md5_hash(full_path)

    if file_hash in seen_hashes:
        print(f"❌ Duplicate found: {filename} == {seen_hashes[file_hash]}")
        duplicate_files.append(full_path)
    else:
        seen_hashes[file_hash] = filename

# === Delete Duplicate Files ===
for file in duplicate_files:
    os.remove(file)
    print(f"🗑️ Deleted: {os.path.basename(file)}")

print(f"\n✅ Done! {len(duplicate_files)} duplicate file(s) removed from: {folder_path}")
