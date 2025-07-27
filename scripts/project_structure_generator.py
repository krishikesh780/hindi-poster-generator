import os

# Define the folder and file structure
structure = {
    "tools-website": {
        "backend": {
            "app.py": "# Flask or FastAPI backend API server\n",
            "tools": {
                "image_to_pdf.py": "# Bulk Image to PDF Tool Code Here\n",
                "quote_generator.py": "# Bulk Quote Generator Tool Code Here\n",
                "quiz_poster_generator.py": "# Quiz Poster Generator Tool Code Here\n",
            },
            "static": {
                "fonts": {},
                "wallpapers-bg": {}
            },
            "templates": {},  # Optional: If using Jinja templates
            "requirements.txt": "fastapi\nuvicorn\npandas\nPillow\nmatplotlib\nopenpyxl\n",
        },
        "frontend": {
            "index.html": "<!-- Landing Page HTML -->\n",
            "about.html": "<!-- About Us Page HTML -->\n",
            "tools.html": "<!-- Tools Listing Page HTML -->\n",
            "contact.html": "<!-- Contact Us Page HTML -->\n",
            "login.html": "<!-- Login / Signup Page HTML -->\n",
            "css": {
                "style.css": "/* Common Styling */\nbody { font-family: Arial, sans-serif; }\n"
            },
            "js": {
                "main.js": "// JS logic for frontend interaction\n"
            },
            "assets": {
                "images": {},
                "fonts": {}
            }
        },
        "README.md": "# FutureWay Tools Website\n\nAll-in-one tools platform using Python backend and static frontend.",
        "requirements.txt": "",  # Optional project-level requirements
    }
}


# Function to create directories and files recursively
def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # Directory
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        elif isinstance(content, str):  # File with content
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
        else:
            pass  # Skip placeholders or None content

# Run the function to create the structure
create_structure(".", structure)

print("✅ Project structure created successfully.")
