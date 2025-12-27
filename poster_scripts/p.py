# Google Sheet ID
SHEET_ID = "1-JWPfIMSAc7IYrZemq4qBfh1lo8vb-hHh3mjdNOqCBU"

# Sheets list
# SHEET_NAMES = ["Technology", "Business", "Sarkari Yojana", "Politics", "Social Issues", "How to Earn Money"]
SHEET_NAMES = ["Technology", "How to Earn Money"]


# Columns
TAGS_COL = "Tags"
PROMPT_COL = "Image_Generation_Prompt"

# Output on Drive
OUTPUT_ROOT = "/content/drive/MyDrive/DeshDishaOutputs"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# Image size (Full HD)
WIDTH, HEIGHT = 1980, 1080

# Model preference order
MODEL_TRY_LIST = [
    "stabilityai/stable-diffusion-xl-base-1.0",   # High Quality
    "stabilityai/stable-diffusion-2-1",
    "runwayml/stable-diffusion-v1-5"
]

GUIDANCE_SCALE = 7.5
STEPS = 28
PAUSE_SEC = 1.2
