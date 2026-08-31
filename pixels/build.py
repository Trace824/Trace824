#!/usr/bin/env python3
"""Trace pixel sprite: the red cloud blob, HTML/CSS + GIF."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GIF_DIR = ROOT / "gifs"
FRAME_DIR = ROOT / "frames"
PIXELS_DIR = ROOT / "pixels"

# Flat red cloud, matching the real avatar. One fill, one shade, black eyes.
PALETTE = {
    ".": None,
    "R": (226, 59, 59, 255),   # body
    "D": (184, 36, 40, 255),   # shade
    "L": (255, 98, 98, 255),   # highlight
    "K": (17, 12, 12, 255),    # eyes
    "O": (196, 132, 72, 255),  # crate
    "Y": (232, 176, 96, 255),
    "V": (139, 124, 255, 255),
    "W": (255, 255, 255, 255),
}

CSS_HEX = {
    "R": "#e23b3b",
    "D": "#b82428",
    "L": "#ff6262",
    "K": "#110c0c",
    "O": "#c48448",
    "Y": "#e8b060",
    "V": "#8b7cff",
    "W": "#ffffff",
}

W, H = 26, 26


def blank():
    return [["." for _ in range(W)] for _ in range(H)]


def setp(g, x, y, c):
    if 0 <= y < H and 0 <= x < W:
        g[y][x] = c


def blit(g, x, y, rows):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch not in (" ",):
                setp(g, x + i, y + j, ch)


def stamp(g, x, y, shape, eyes="open"):
    blit(g, x, y, shape)
    # eyes are drawn by the caller via overlay on the shape using K already,
    # or replaced here if closed.
    if eyes == "closed":
        # turn any K into a 1px line: find K columns in the top half
        for j, row in enumerate(shape):
            for i, ch in enumerate(row):
                if ch == "K":
                    setp(g, x + i, y + j, "R")
        # draw closed eyes as two short dashes where the eyes were
        # (filled in by each pose)



def disk(g, cx, cy, r, fill="R"):
    rr = r * r
    for y in range(H):
        for x in range(W):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= rr:
                setp(g, x, y, fill)


def draw_cloud(g, stretch=0.0, wide=0.0, blink=False, lift_right=0.0, look=0):
    """Five silhouette bumps: top, upper-left, upper-right, bottom-left, bottom-right."""
    cy = 13.0 + stretch * 0.2
    # hidden body so the five bumps stay one cloud
    disk(g, 13.0, cy, 5.4)
    # 1 top
    disk(g, 13.0, 6.0 + stretch, 4.55)
    # 2 upper-left
    disk(g, 5.6 - wide * 0.5, 9.6 + stretch * 0.1, 4.7)
    # 3 upper-right
    disk(g, 20.4 + wide * 0.5, 9.6 + stretch * 0.1 - lift_right * 0.5, 4.7)
    # 4 bottom-left
    disk(g, 6.4 - wide, 18.4 - stretch * 0.15, 5.2)
    # 5 bottom-right
    disk(g, 19.6 + wide, 18.4 - stretch * 0.15 - lift_right, 5.2)

    ey = int(round(cy)) - 3 + look
    if blink:
        for x in (10, 15):
            setp(g, x, ey + 1, "K")
            setp(g, x + 1, ey + 1, "K")
    else:
        for x in (10, 15):
            for y in (ey - 1, ey, ey + 1):
                setp(g, x, y, "K")
                setp(g, x + 1, y, "K")


def draw_crate(g, x, y, bounce=0):
    blit(
        g,
        x,
        y - bounce,
        [
            "....",
            "YYYY",
            "YOVY",
            "YYYY",
        ],
    )


def to_img(grid, scale: int) -> Image.Image:
    img = Image.new("RGBA", (W * scale, H * scale), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            color = PALETTE.get(ch)
            if not color:
                continue
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = color
    return img


def _palette_image():
    colors = [(0, 0, 0)]
    index = {}
    for rgba in PALETTE.values():
        if not rgba:
            continue
        rgb = rgba[:3]
        if rgb not in index:
            index[rgb] = len(colors)
            colors.append(rgb)
    pal = []
    for rgb in colors:
        pal.extend(rgb)
    pal.extend([0, 0, 0] * (256 - len(colors)))
    return pal, index


def rgba_to_p(im: Image.Image, pal, index) -> Image.Image:
    out = Image.new("P", im.size)
    out.putpalette(pal)
    src = im.load()
    dst = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = src[x, y]
            dst[x, y] = 0 if a < 128 else index[(r, g, b)]
    out.info["transparency"] = 0
    return out


def save_gif(frames_img: list[Image.Image], path: Path, duration: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    pal, index = _palette_image()
    converted = [rgba_to_p(im, pal, index) for im in frames_img]
    converted[0].save(
        path,
        save_all=True,
        append_images=converted[1:],
        duration=duration,
        loop=0,
        disposal=2,
        transparency=0,
        optimize=False,
    )



def idle_frames():
    # the real avatar breathes: top lobe down, bottom lobes out
    seq = [
        (0.0, 0.0, False),
        (0.2, 0.2, False),
        (1.2, 0.8, False),
        (1.8, 1.3, False),
        (1.0, 0.7, False),
        (0.0, 0.0, True),
        (0.0, 0.0, False),
        (0.6, 0.4, False),
    ]
    out = []
    for stretch, wide, blink in seq:
        g = blank()
        draw_cloud(g, stretch=stretch, wide=wide, blink=blink)
        out.append(g)
    return out


def wave_frames():
    lifts = [0.0, 1.4, 2.4, 1.2, 0.0, 1.6, 2.4, 1.0]
    out = []
    for i, lift in enumerate(lifts):
        g = blank()
        draw_cloud(g, stretch=0.3 * (i % 2), wide=0.3, lift_right=lift)
        out.append(g)
    return out


def think_frames():
    dots = [
        [],
        [(11, 1, "K")],
        [(11, 1, "K"), (13, 2, "K")],
        [(11, 1, "D"), (13, 2, "K"), (15, 1, "K")],
        [(13, 2, "K"), (15, 1, "D")],
        [(15, 1, "K")],
        [],
        [(11, 1, "K")],
    ]
    out = []
    for i, ds in enumerate(dots):
        g = blank()
        draw_cloud(g, stretch=0.4 * (i % 2), look=-1)
        for x, y, c in ds:
            setp(g, x, y, c)
        out.append(g)
    return out


def ship_frames():
    out = []
    for i in range(8):
        g = blank()
        bounce = 1 if i % 4 >= 2 else 0
        draw_cloud(g, stretch=0.3 * (i % 2), wide=0.2)
        draw_crate(g, 19, 16, bounce=bounce)
        out.append(g)
    return out


def box_shadow(grid, scale=6):
    parts = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            hx = CSS_HEX[ch]
            parts.append(f"{x * scale}px {y * scale}px 0 0 {hx}")
    return ",\n    ".join(parts)


def write_html(anims: dict[str, list]):
    css_frames = []
    html_cards = []
    for name, frames in anims.items():
        n = len(frames)
        pct = 100 / n
        keys = []
        for i, fr in enumerate(frames):
            keys.append(f"  {i * pct:.2f}% {{ box-shadow:\n    {box_shadow(fr, 6)}; }}")
        keys.append(f"  100% {{ box-shadow:\n    {box_shadow(frames[0], 6)}; }}")
        css_frames.append(
            f"@keyframes {name} {{\n" + "\n".join(keys) + "\n}\n"
            f".sprite.{name} {{ animation: {name} {n * 0.14:.2f}s steps(1) infinite; }}\n"
        )
        html_cards.append(
            f'<figure><div class="stage"><i class="sprite {name}"></i></div><figcaption>{name}</figcaption></figure>'
        )

    css = f"""
:root {{ --bg:#07080d; --ink:#ff6262; --muted:#c48a8a; }}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}}
header {{ text-align: center; padding: 36px 16px 8px; }}
header h1 {{ font-weight: 600; letter-spacing: .4em; font-size: 14px; margin: 0 0 8px; }}
header p {{ color: var(--muted); font-size: 13px; }}
main {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 28px;
  max-width: 960px;
  margin: 24px auto 64px;
  padding: 0 20px;
}}
figure {{ margin: 0; text-align: center; }}
figcaption {{
  margin-top: 12px; color: var(--muted); letter-spacing: .18em;
  font-size: 11px; text-transform: lowercase;
}}
.stage {{
  width: 144px; height: 144px; margin: 0 auto;
  image-rendering: pixelated;
  filter: drop-shadow(0 0 14px #e23b3b55);
}}
.sprite {{ display: block; width: 6px; height: 6px; background: transparent; }}
{''.join(css_frames)}
"""
    html = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trace — pixel</title>
<style>{css}</style>
<header>
  <h1>TRACE</h1>
  <p>the red cloud. html + css, then gif.</p>
</header>
<main>
  {''.join(html_cards)}
</main>
</html>
"""
    PIXELS_DIR.mkdir(parents=True, exist_ok=True)
    (PIXELS_DIR / "index.html").write_text(html)
    (PIXELS_DIR / "trace.css").write_text(css)


def dump_preview(name, frames, scale=8):
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    for i, g in enumerate(frames):
        to_img(g, scale).save(FRAME_DIR / f"{name}_{i:02d}.png")


def main():
    anims = {
        "idle": idle_frames(),
        "wave": wave_frames(),
        "think": think_frames(),
        "ship": ship_frames(),
    }
    write_html(anims)
    GIF_DIR.mkdir(parents=True, exist_ok=True)
    scale = 8
    durations = {"idle": 160, "wave": 120, "think": 170, "ship": 130}
    for name, frames in anims.items():
        dump_preview(name, frames, scale)
        imgs = [to_img(g, scale) for g in frames]
        save_gif(imgs, GIF_DIR / f"{name}.gif", durations[name])
        print("wrote", name, len(frames), "frames")


if __name__ == "__main__":
    main()
