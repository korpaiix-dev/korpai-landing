#!/usr/bin/env python3
"""Generate og-default.png for korpai.co — 1200x630 brand image.

Runs with: python3 scripts/gen-og-image.py
Output:    site/public/og-default.png

Design: navy bg + diagonal cyan/violet gradient beams +
        KORP AI wordmark + English tagline + brand dots.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "site" / "public" / "assets" / "logo-horizontal.png"
OUT = ROOT / "site" / "public" / "og-default.png"

W, H = 1200, 630
NAVY = (5, 7, 14)
NAVY_2 = (15, 20, 32)
CYAN = (38, 215, 246)
VIOLET = (124, 95, 255)
SOFT = (180, 195, 220)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def vertical_gradient(w: int, h: int, top: tuple[int, int, int], bot: tuple[int, int, int]) -> Image.Image:
    base = Image.new("RGB", (w, h), top)
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] * (1 - t) + bot[0] * t)
        g = int(top[1] * (1 - t) + bot[1] * t)
        b = int(top[2] * (1 - t) + bot[2] * t)
        ImageDraw.Draw(base).line([(0, y), (w, y)], fill=(r, g, b))
    return base


def diagonal_beam(w: int, h: int, color: tuple[int, int, int], angle: int, alpha: int = 60) -> Image.Image:
    """Soft diagonal light beam."""
    beam = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(beam)
    # horizontal stripe
    for i in range(120):
        a = int(alpha * (1 - i / 120))
        d.line([(0, h + i), (w * 2, h + i)], fill=color + (a,), width=1)
        d.line([(0, h - i), (w * 2, h - i)], fill=color + (a,), width=1)
    beam = beam.rotate(angle, resample=Image.BICUBIC, expand=False)
    beam = beam.filter(ImageFilter.GaussianBlur(18))
    return beam.crop((w // 2, h // 2, w // 2 + w, h // 2 + h))


def grid(w: int, h: int, color: tuple[int, int, int], step: int = 40, alpha: int = 18) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=color + (alpha,), width=1)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=color + (alpha,), width=1)
    return layer


def main() -> None:
    # 1 — base gradient navy
    base = vertical_gradient(W, H, NAVY, NAVY_2).convert("RGBA")

    # 2 — subtle grid overlay (Raycast feel)
    base = Image.alpha_composite(base, grid(W, H, (120, 140, 180), step=60, alpha=14))

    # 3 — diagonal beams
    beam1 = diagonal_beam(W, H, CYAN, -22, alpha=55)
    beam2 = diagonal_beam(W, H, VIOLET, 14, alpha=48)
    base = Image.alpha_composite(base, beam1)
    base = Image.alpha_composite(base, beam2)

    # 4 — soft orbs
    for cx, cy, r, col, a in [
        (200, 140, 220, CYAN, 60),
        (1000, 500, 280, VIOLET, 50),
    ]:
        blob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(blob).ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (a,))
        blob = blob.filter(ImageFilter.GaussianBlur(90))
        base = Image.alpha_composite(base, blob)

    # 5 — logo
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((180, 180))
        base.alpha_composite(logo, (80, 80))

    # 6 — typography
    draw = ImageDraw.Draw(base)
    eyebrow = ImageFont.truetype(FONT_MONO, 22)
    title = ImageFont.truetype(FONT_BOLD, 78)
    title_2 = ImageFont.truetype(FONT_BOLD, 60)
    sub = ImageFont.truetype(FONT_REG, 30)
    tiny = ImageFont.truetype(FONT_MONO, 20)

    draw.text((80, 290), "KORP AI AUTOMATION", font=eyebrow, fill=CYAN)
    draw.text((80, 325), "AI Chatbot. Automation.", font=title, fill=(255, 255, 255))
    draw.text((80, 410), "Dashboard.", font=title_2, fill=(255, 255, 255))
    draw.text((80, 490), "Build. Ship. Repeat. — for Thai SME.", font=sub, fill=SOFT)

    # 7 — URL badge bottom-right
    badge = "korpai.co"
    bw = draw.textlength(badge, font=tiny)
    draw.rectangle((W - int(bw) - 50, H - 60, W - 30, H - 30), outline=(60, 80, 120, 255), width=1)
    draw.text((W - int(bw) - 40, H - 55), badge, font=tiny, fill=CYAN)

    # 8 — soft vignette
    vign = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vign)
    for i in range(80):
        a = int(120 * (1 - i / 80))
        vd.rectangle((i, i, W - i, H - i), outline=(0, 0, 0, a), width=1)
    base = Image.alpha_composite(base, vign)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} — {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
