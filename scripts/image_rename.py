import os

# Folder path
folder_path = r'D:\YoutubePoster\input\wallpapers-gym'

# Change working directory
os.chdir(folder_path)

# List all files and sort (optional)
files = sorted(os.listdir())

# Rename images
count = 1
for filename in files:
    # Split filename and extension
    name, ext = os.path.splitext(filename)
    
    # Skip folders (only files)
    if os.path.isfile(filename):
        new_name = f"{count}{ext}"
        os.rename(filename, new_name)
        count += 1

print("Renaming Complete!")
