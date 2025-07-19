import os

# Folder name
folder_name = "Quotes"

# File names to be created
file_names = [
    "motivational_quotes.txt",
    "emotional_quotes.txt",
    "life_reality_quotes.txt",
    "self_respect_quotes.txt",
    "spiritual_quotes.txt",
    "career_success_quotes.txt",
    "whatsapp_status.txt"
]

# Create folder if not exists
os.makedirs(folder_name, exist_ok=True)

# Create empty files
for file_name in file_names:
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        pass  # Empty file created
    print(f"Created: {file_path}")

print("✅ All files created successfully in 'Quotes' folder.")
