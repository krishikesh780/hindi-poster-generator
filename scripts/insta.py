from PIL import Image, ImageDraw, ImageFont

# Poster size
width, height = 768, 1152
background_color = (15, 15, 30)

# Create base image
poster = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(poster)

# Function: auto adjust font size
def fit_text(text, max_width, start_size=60, font_path="arialbd.ttf"):
    size = start_size
    while size > 10:
        font = ImageFont.truetype(font_path, size)
        if font.getlength(text) <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(font_path, 12)

# Function: paste logo
def paste_logo(path, size, pos):
    try:
        logo = Image.open(path).resize(size).convert("RGBA")
        poster.paste(logo, pos, logo)
    except:
        pass

# ------------------ TEXT AREA ------------------
# Title
title_text = "Master Python with AI"
title_font = fit_text(title_text, max_width=width-100, start_size=80)
draw.text((60, 60), title_text, font=title_font, fill=(255, 255, 255))

# Subtitle
sub_text = "INDUSTRY ORIENTED WORKSHOP"
sub_font = fit_text(sub_text, max_width=width-100, start_size=50)
draw.text((60, 150), sub_text, font=sub_font, fill=(255, 215, 0))

# Section Header
header_text = "WORKSHOP HIGHLIGHTS"
header_font = fit_text(header_text, max_width=width-100, start_size=50)
draw.text((60, 240), header_text, font=header_font, fill=(255, 215, 0))

# Highlights
highlights = [
    "3 Hours Live Online Session",
    "Certification Included",
    "Build 2 AI Projects for your resume",
    "Learn Python + AI Automation step by step"
]

y = 310
try:
    tick = Image.open("tick.png").resize((25, 25)).convert("RGBA")
except:
    tick = None

for line in highlights:
    if tick:
        poster.paste(tick, (50, y+5), tick)
    font = fit_text(line, max_width=width-150, start_size=38, font_path="arial.ttf")
    draw.text((90, y), line, font=font, fill=(200, 255, 200))
    y += 60

# Bonuses
bonus_text = "Bonuses (Worth ₹7,000+)"
bonus_font = fit_text(bonus_text, max_width=width-100, start_size=45)
draw.text((60, y + 20), bonus_text, font=bonus_font, fill=(255, 215, 0))

bonuses = [
    "Free Setup Guide (Python + AI tools)",
    "Python Cheatsheet (100+ codes)",
    "2 Resume-Ready AI Projects"
]

y += 90
for line in bonuses:
    if tick:
        poster.paste(tick, (50, y+5), tick)
    font = fit_text(line, max_width=width-150, start_size=36, font_path="arial.ttf")
    draw.text((90, y), line, font=font, fill=(255, 255, 255))
    y += 60

# Extras
extras = [
    "Secure Payment",
    "WhatsApp Updates",
    "100% Satisfaction Guarantee"
]

y += 60
for line in extras:
    if tick:
        poster.paste(tick, (50, y+5), tick)
    font = fit_text(line, max_width=width-150, start_size=34, font_path="arial.ttf")
    draw.text((90, y), line, font=font, fill=(0, 255, 100))
    y += 50

# ------------------ AUTO LOGO AREA ------------------
# Calculate remaining space for logos
remaining_height = height - y - 200
logo_y = y + remaining_height//2  # center of blank area

# Arrange logos equally spaced (left, center, right)
logo_size = (120, 120)
margin_x = 80
gap = (width - 2*margin_x - 3*logo_size[0]) // 2

# Python left
paste_logo(r"D:\main\YoutubePoster\scripts\python.png", logo_size, (margin_x, logo_y))
# Excel center
paste_logo("excel.png", logo_size, (margin_x + logo_size[0] + gap, logo_y))
# AI right
paste_logo("ai.png", logo_size, (margin_x + 2*(logo_size[0] + gap), logo_y))

# ----------------------------------------------------

# Save Poster
poster.save("python_ai_workshop_dynamic_auto.png")
poster.show()
