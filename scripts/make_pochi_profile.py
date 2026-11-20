"""Build a small README GIF using the authentic Pochi repository sprites."""
from pathlib import Path
from urllib.request import urlopen, Request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

OUT = Path("assets/pochi-original.gif")
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = "https://raw.githubusercontent.com/sushan5140/Pochi/main/assets/"
# Native artwork, not a redesigned character. Ordered to make a calm idle sequence.
SPRITES = [
    ("poses/arms_crossed.png", 900),
    ("expressions/happy.png", 600),
    ("poses/reading.png", 1100),
    ("poses/arms_crossed.png", 750),
    ("expressions/sleepy.png", 650),
    ("poses/sleeping_pillow.png", 1300),
    ("poses/arms_crossed.png", 1000),
]
W, H = 700, 208
frames, durations = [], []
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except OSError:
    font_title = font_small = ImageFont.load_default()

for name, duration in SPRITES:
    url = BASE + name
    req = Request(url, headers={"User-Agent": "Pochi-profile-animation"})
    with urlopen(req, timeout=30) as response:
        sprite = Image.open(BytesIO(response.read())).convert("RGBA")
    # Preserve original art and aspect ratio; transparent padding stays transparent.
    sprite.thumbnail((182, 182), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (W, H), "#172334")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((13, 13, W - 14, H - 14), radius=17, fill="#223246", outline="#3d5369", width=2)
    draw.text((39, 54), "Pochi is here.", fill="#f5efe5", font=font_title)
    draw.text((40, 96), "Just doing Pochi things.", fill="#c4d0d9", font=font_small)
    draw.text((40, 151), "the original little desktop companion", fill="#9cbbca", font=font_small)
    x = 489 + (182 - sprite.width) // 2
    y = 13 + (182 - sprite.height) // 2
    canvas.alpha_composite(sprite, (x, y))
    frames.append(canvas.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    durations.append(duration)

frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations,
               loop=0, disposal=2, optimize=True)
print(f"Created {OUT}, {len(frames)} authentic sprite frames, {OUT.stat().st_size} bytes")
