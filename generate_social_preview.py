import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 640
img = Image.new('RGBA', (W, H), (8, 12, 20, 255))

# 1. Subtle Background Grid
grid_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid_layer)
grid_spacing = 40
for x in range(0, W, grid_spacing):
    gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 6), width=1)
for y in range(0, H, grid_spacing):
    gd.line([(0, y), (W, y)], fill=(255, 255, 255, 6), width=1)

# Mask grid towards center
mask = Image.new('L', (W, H), 0)
md = ImageDraw.Draw(mask)
md.ellipse((100, -100, W - 100, H + 100), fill=200)
mask = mask.filter(ImageFilter.GaussianBlur(100))
grid_layer.putalpha(mask)
img = Image.alpha_composite(img, grid_layer)

# 2. Ambient Colorful Glows
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r in range(500, 0, -8):
    a1 = int(38 * (1 - r / 500)**1.6)
    gd.ellipse((W - 220 - r, -80 - r, W - 220 + r, -80 + r), fill=(34, 139, 230, a1))
    a2 = int(24 * (1 - r / 500)**1.6)
    gd.ellipse((160 - r, H + 120 - r, 160 + r, H + 120 + r), fill=(16, 185, 129, a2))
img = Image.alpha_composite(img, glow)

# 3. Glassmorphism Main Card
card_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
cd = ImageDraw.Draw(card_layer)
cx0, cy0, cx1, cy1 = 70, 70, W - 70, H - 70

# Card background & border
cd.rounded_rectangle((cx0, cy0, cx1, cy1), radius=28, fill=(15, 23, 42, 215), outline=(255, 255, 255, 30), width=1)
# Top inner highlight line
cd.rounded_rectangle((cx0 + 1, cy0 + 1, cx1 - 1, cy0 + 3), radius=2, fill=(255, 255, 255, 35))

img = Image.alpha_composite(img, card_layer)

# 4. Fonts setup
font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 68)
font_tagline = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 22)
font_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 16)
font_badge = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 13)
font_feature = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 15)

draw = ImageDraw.Draw(img)

# 5. Left Icon Container
icon_box_x = 130
icon_box_y = 200
box_size = 200

# Ambient glow under icon
icon_glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
igd = ImageDraw.Draw(icon_glow)
for r in range(120, 0, -4):
    a = int(45 * (1 - r / 120))
    igd.ellipse((icon_box_x + box_size//2 - r, icon_box_y + box_size//2 - r,
                 icon_box_x + box_size//2 + r, icon_box_y + box_size//2 + r), fill=(34, 139, 230, a))
img = Image.alpha_composite(img, icon_glow)

# Icon box glass
draw = ImageDraw.Draw(img)
draw.rounded_rectangle(
    (icon_box_x, icon_box_y, icon_box_x + box_size, icon_box_y + box_size),
    radius=36,
    fill=(22, 32, 54, 230),
    outline=(255, 255, 255, 45),
    width=1
)

# Load and place folder icon
icon_path = r"d:\File Juggler 3\fileflow\icon.png"
if os.path.exists(icon_path):
    icon_img = Image.open(icon_path).convert("RGBA")
    icon_resized = icon_img.resize((130, 130), Image.Resampling.LANCZOS)
    img.alpha_composite(icon_resized, (icon_box_x + 35, icon_box_y + 35))

# 6. Right Content Section
text_x = 380
text_y = 135

# Pill Badges
badges = [
    ("WINDOWS APP", (34, 139, 230, 30), (34, 139, 230, 120), (96, 165, 250, 255)),
    ("100% OFFLINE & PRIVATE", (16, 185, 129, 30), (16, 185, 129, 120), (52, 211, 153, 255)),
    ("AUTO-ORGANIZER", (168, 85, 247, 30), (168, 85, 247, 120), (192, 132, 252, 255))
]

badge_cur_x = text_x
for text, bg_col, border_col, text_col in badges:
    bbox = font_badge.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pw, ph = tw + 22, th + 12
    draw.rounded_rectangle((badge_cur_x, text_y, badge_cur_x + pw, text_y + ph), radius=999, fill=bg_col, outline=border_col, width=1)
    draw.text((badge_cur_x + 11, text_y + 5), text, font=font_badge, fill=text_col)
    badge_cur_x += pw + 12

# Title: FileFlow.
title_y = text_y + 36
draw.text((text_x, title_y), "FileFlow", font=font_title, fill=(255, 255, 255, 255))
title_w = font_title.getbbox("FileFlow")[2] - font_title.getbbox("FileFlow")[0]
draw.text((text_x + title_w + 2, title_y), ".", font=font_title, fill=(34, 139, 230, 255))

# Tagline
tag_y = title_y + 85
draw.text((text_x, tag_y), "Intelligent Automated File Organization for Windows", font=font_tagline, fill=(241, 245, 249, 255))
draw.text((text_x, tag_y + 34), "Tames folder chaos in seconds. Deep content extraction, smart rules & duplicate cleaner.", font=font_sub, fill=(148, 163, 184, 255))

# Divider Line
div_y = tag_y + 80
draw.line([(text_x, div_y), (W - 130, div_y)], fill=(255, 255, 255, 20), width=1)

# Key Features Grid
features = [
    ("⚡ Real-Time Watcher", (96, 165, 250, 255)),
    ("📄 PDF & EXIF Parsing", (52, 211, 153, 255)),
    ("🔍 3-Stage Duplicate Cleaner", (251, 191, 36, 255)),
    ("🛡️ Zero Cloud / No Accounts", (244, 114, 182, 255))
]

feat_x = text_x
feat_y = div_y + 22
for ftext, dot_col in features:
    draw.ellipse((feat_x, feat_y + 6, feat_x + 7, feat_y + 13), fill=dot_col)
    draw.text((feat_x + 15, feat_y + 2), ftext, font=font_feature, fill=(226, 232, 240, 255))
    feat_x += 185

# Convert to RGB and save
final_img = img.convert("RGB")
out_dir = r"d:\File Juggler 3\fileflow\assets"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "social_preview.png")
final_img.save(out_path, format="PNG", quality=95)
print(f"Social preview saved successfully to {out_path} ({final_img.size})")

# Also copy to root assets
root_assets = r"d:\File Juggler 3\assets"
os.makedirs(root_assets, exist_ok=True)
final_img.save(os.path.join(root_assets, "social_preview.png"), format="PNG", quality=95)
