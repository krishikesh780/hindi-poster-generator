#!/usr/bin/env python3
"""
FutureWay Bulk Image Generator
--------------------------------
Two backends:
  1) A1111 (Automatic1111 WebUI API) - generates with Stable Diffusion
  2) Pillow fallback - clean text posters (no SD required)

Usage examples:
  # Pillow only (no SD), outputs to ./out and creates a ZIP
  python futureway_bulk_image_gen.py --backend pillow --out out

  # A1111 Stable Diffusion (make sure WebUI is running on localhost:7860)
  python futureway_bulk_image_gen.py --backend a1111 --a1111-url http://127.0.0.1:7860 --out out

Optional:
  --zip yes          -> also bundle outputs into a ZIP file
  --overlay yes      -> after SD render, overlay crisp title/subtitle via Pillow to avoid text glitches
  --steps 30 --cfg 7 -> SD sampling params

Prompts are prefilled for your 8 posts below but you can edit or point to a JSON file via --json prompts.json

JSON format:
[
  {
    "filename": "01_social_media_marketing.png",
    "title": "SOCIAL MEDIA MARKETING",
    "subtitle": "FB • Instagram • WhatsApp",
    "prompt": "A vibrant digital ad...",
    "negative": "blurry, artifacts, bad text, misspelled letters",
    "theme": "gradient_pp"
  },
  ...
]
"""
import os, io, json, base64, argparse, zipfile, textwrap, sys
from PIL import Image, ImageDraw, ImageFont

try:
    import requests
except Exception:
    requests = None

def load_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FONT_H1 = load_font(100, bold=True)
FONT_H2 = load_font(64, bold=True)

W = H = 1080

def gradient(img, c1, c2, horizontal=False):
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    if horizontal:
        for x in range(W):
            t = x/(W-1)
            r = int(c1[0]*(1-t)+c2[0]*t); g=int(c1[1]*(1-t)+c2[1]*t); b=int(c1[2]*(1-t)+c2[2]*t)
            draw.line([(x,0),(x,H)], fill=(r,g,b))
    else:
        for y in range(H):
            t = y/(H-1)
            r = int(c1[0]*(1-t)+c2[0]*t); g=int(c1[1]*(1-t)+c2[1]*t); b=int(c1[2]*(1-t)+c2[2]*t)
            draw.line([(0,y),(W,y)], fill=(r,g,b))

def themed_bg(theme):
    from PIL import Image
    img = Image.new("RGB", (W,H), (14,108,255))
    if theme == "gradient_pp":
        gradient(img, (128,71,248), (236,72,153), horizontal=True)
    elif theme == "brand_blue":
        img.paste((14,108,255), [0,0,W,H])
    elif theme == "orange_navy":
        gradient(img, (255,140,0), (11,39,89), horizontal=True)
    elif theme == "light_blue_green":
        gradient(img, (220,240,255), (160,230,200), horizontal=False)
    elif theme == "money_theme":
        img.paste((249,200,0), [0,0,W,H])
    return img

def auto_fit_text(draw, text, top_y, font, color=(255,255,255), max_width=W-160, line_spacing=10):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    y = top_y
    for line in lines:
        tw = draw.textlength(line, font=font)
        draw.text(((W-tw)//2, y), line, font=font, fill=color)
        y += (font.getbbox(line)[3]-font.getbbox(line)[1]) + line_spacing
    return y

def overlay_text(img, title, subtitle):
    draw = ImageDraw.Draw(img)
    # Auto shrink if too wide
    font1 = FONT_H1
    while draw.textlength(title, font=font1) > W-160 and font1.size > 50:
        font1 = load_font(font1.size-6, bold=True)
    font2 = FONT_H2
    while draw.textlength(subtitle, font=font2) > W-160 and font2.size > 36:
        font2 = load_font(font2.size-4, bold=True)

    y = 140
    y = auto_fit_text(draw, title, y, font1, (255,255,255))
    y += 8
    auto_fit_text(draw, subtitle, y, font2, (255,255,255))
    return img

def sd_txt2img(a1111_url, prompt, negative="", steps=28, cfg=7, width=1080, height=1080, seed=-1):
    if requests is None:
        raise RuntimeError("requests not available. Install requests to use A1111 backend.")
    payload = {
        "prompt": prompt,
        "negative_prompt": negative or "blurry, artifacts, deformed, bad text, misspelled letters, low quality",
        "steps": steps,
        "cfg_scale": cfg,
        "width": width,
        "height": height,
        "sampler_name": "DPM++ 2M Karras",
        "seed": seed,
        "batch_size": 1,
        "restore_faces": False,
        "tiling": False,
        "hr_scale": 1.0
    }
    r = requests.post(f"{a1111_url.rstrip('/')}/sdapi/v1/txt2img", json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    if not data.get("images"):
        raise RuntimeError("A1111 returned no images.")
    b64 = data["images"][0].split(",",1)[-1]
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["a1111","pillow"], default="pillow")
    ap.add_argument("--a1111-url", default="http://127.0.0.1:7860")
    ap.add_argument("--out", default="out")
    ap.add_argument("--zip", choices=["yes","no"], default="yes")
    ap.add_argument("--overlay", choices=["yes","no"], default="yes")
    ap.add_argument("--json", default="")
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--cfg", type=float, default=7.0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    default_items = [
      {"filename":"01_social_media_marketing.png","title":"SOCIAL MEDIA MARKETING","subtitle":"FB • Instagram • WhatsApp","prompt":"A vibrant digital ad with purple to pink gradient background, bold white headline 'SOCIAL MEDIA MARKETING', icons of WhatsApp, Facebook, Instagram around a clean white megaphone, minimal flat style, modern layout, high contrast.","negative":"blurry, artifacts, bad text, misspelled letters","theme":"gradient_pp"},
      {"filename":"02_boost_your_brand.png","title":"BOOST YOUR BRAND ONLINE","subtitle":"Consistent Posts • Smart Ads","prompt":"Blue and white brand poster with subtle orange highlights, rocket launch, growth bar graph, spotlight on social media icons, professional minimal design, corporate feel.","negative":"busy background, clutter, low contrast","theme":"brand_blue"},
      {"filename":"03_trusted_service.png","title":"WHY CHOOSE FUTUREWAY","subtitle":"Trusted • Secure • Reliable","prompt":"Deep blue background with white and gold accents, shield, handshake, tick mark and stars representing trust, clean minimal layout, professional business poster.","negative":"messy, noisy, crowded layout","theme":"brand_blue"},
      {"filename":"04_business_pack.png","title":"BUSINESS PACK","subtitle":"1500 SMS + 120 Social Posts","prompt":"Orange and navy theme poster, package box, SMS bubble, social media icons, small calendar, modern flat style, bold composition.","negative":"overcrowded, blurry text","theme":"orange_navy"},
      {"filename":"05_all_in_one.png","title":"ALL-IN-ONE","subtitle":"SMS + WhatsApp + Email","prompt":"Purple‑pink gradient background, white headline, WhatsApp logo, email envelope, SMS bubble and a globe icon, sleek modern composition.","negative":"low contrast, messy layout","theme":"gradient_pp"},
      {"filename":"06_engage_daily.png","title":"ENGAGE CUSTOMERS DAILY","subtitle":"Smart Posting • Likes • Comments","prompt":"Light blue and green themed poster, neat calendar, like and comment icons, mobile phone frame, fresh and engaging, minimal flat design.","negative":"busy cluttered design","theme":"light_blue_green"},
      {"filename":"07_global_reach.png","title":"MULTI-ROUTE MESSAGING","subtitle":"Global Reach • Reliable Routes","prompt":"Green and dark blue professional poster, globe, airplane, message envelope and signal tower, clean corporate layout.","negative":"noisy, low quality","theme":"brand_blue"},
      {"filename":"08_affordable_branding.png","title":"AFFORDABLE BRANDING","subtitle":"Perfect for Startups","prompt":"Yellow and black theme, piggy bank, rupee symbol, social media icons and upward growth arrow, startup friendly flat design.","negative":"overly complex, clutter","theme":"money_theme"}
    ]

    items = default_items
    if args.json and os.path.exists(args.json):
        with open(args.json, "r", encoding="utf-8") as f:
            items = json.load(f)

    images = []
    for item in items:
        bg = themed_bg(item.get("theme","brand_blue"))
        if args.backend == "a1111":
            try:
                sd_img = sd_txt2img(args.a1111_url, item["prompt"], item.get("negative",""), steps=args.steps, cfg=args.cfg, width=W, height=H)
                img = sd_img
            except Exception as e:
                print(f"[WARN] A1111 failed for {item['filename']}: {e}. Falling back to theme background.")
                img = bg
        else:
            img = bg

        if args.overlay == "yes":
            img = overlay_text(img, item["title"], item["subtitle"])

        out_path = os.path.join(args.out, item["filename"])
        img.save(out_path, "PNG")
        images.append(out_path)
        print(f"Saved: {out_path}")

    zip_path = None
    if args.zip == "yes":
        zip_path = os.path.join(args.out, "FutureWay_Bulk_Posts.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in images:
                zf.write(p, os.path.basename(p))
        print(f"ZIP created: {zip_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
