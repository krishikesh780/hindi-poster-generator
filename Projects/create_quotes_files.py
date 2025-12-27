import os

# =============================
# SETTINGS
# =============================
BASE_DIR = os.getcwd()          # Current directory
FOLDER_NAME = "Quotes"

FILE_NAMES = [
    "motivational_quotes.txt",
    "emotional_quotes.txt",
    "life_reality_quotes.txt",
    "self_respect_quotes.txt",
    "spiritual_quotes.txt",
    "career_success_quotes.txt",
    "whatsapp_status.txt"
]

# =============================
# CREATE FOLDER
# =============================
quotes_dir = os.path.join(BASE_DIR, FOLDER_NAME)
os.makedirs(quotes_dir, exist_ok=True)

# =============================
# CREATE FILES (SAFE)
# =============================
for file_name in FILE_NAMES:
    file_path = os.path.join(quotes_dir, file_name)

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")   # empty file
        print(f"✔ Created: {file_name}")
    else:
        print(f"⚠ Already exists: {file_name}")

# =============================
# DONE
# =============================
print(f"\n✅ All files are ready inside folder: {quotes_dir}")
