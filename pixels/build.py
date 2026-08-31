#!/usr/bin/env python3
"""Trace as the red 5-bump cloud, animated in Clawd's language.

References:
- Lakshman's correction: flat red cloud, two oval eyes, no mouth, breathe
- Five silhouette bumps (top, UL, UR, BL, BR)
- Claude/Clawd mascot motion (Codrops 2026): rectangles only, look-around,
  squash/weight, body sway opposite the wave, stomp + confetti, uneven holds.
  Trace is the cloud. Not a crab, not terracotta.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GIF_DIR = ROOT / "gifs"
FRAME_DIR = ROOT / "frames"
PIXELS_DIR = ROOT / "pixels"

PALETTE = {
    ".": None,
    "R": (226, 59, 59, 255),
    "K": (17, 12, 12, 255),
    "W": (255, 255, 255, 255),
    "L": (255, 120, 110, 255),
    "D": (168, 32, 36, 255),
    "Y": (255, 214, 120, 255),
}

CSS_HEX = {
    "R": "#e23b3b",
    "K": "#110c0c",
    "W": "#ffffff",
    "L": "#ff7870",
    "D": "#a82024",
    "Y": "#ffd678",
}

W, H = 36, 34


def blank():
    return [["." for _ in range(W)] for _ in range(H)]


def setp(g, x, y, c):
    if 0 <= y < H and 0 <= x < W and c != ".":
        g[y][x] = c


def rect(g, x, y, w, h, c="R"):
    for j in range(int(h)):
        for i in range(int(w)):
            setp(g, int(x) + i, int(y) + j, c)


def round_rect(g, x, y, w, h, c="R"):
    """Axis-aligned rect with 1px corners knocked off — Clawd's rectangle language, slightly puffy."""
    rect(g, x, y, w, h, c)
    setp(g, x, y, ".")
    setp(g, x + w - 1, y, ".")
    setp(g, x, y + h - 1, ".")
    setp(g, x + w - 1, y + h - 1, ".")


def draw_cloud(g, ox=0, oy=0, squash=0, lean=0, look=0, blink=False, lift_ur=0, step=0):
    """Five bumps from rectangles, spread so they don't melt into a brick."""
    sy = squash
    lx = lean
    # body fill (hidden, no extra silhouette bump)
    round_rect(g, 12 + ox + lx, 11 + oy + sy, 12, 10)
    # 1 top
    round_rect(g, 13 + ox + lx, 2 + oy + sy, 10, 8)
    # 2 upper-left
    round_rect(g, 2 + ox + lx, 7 + oy + sy, 10, 8)
    # 3 upper-right (wave lifts this)
    round_rect(g, 24 + ox + lx, 7 + oy + sy - lift_ur, 10, 8)
    # 4 bottom-left
    bl_y = 18 + oy + sy + (2 if step < 0 else 0) - (1 if step > 0 else 0)
    round_rect(g, 3 + ox + lx, bl_y, 12, 9 - min(sy, 2))
    # 5 bottom-right
    br_y = 18 + oy + sy + (2 if step > 0 else 0) - (1 if step < 0 else 0)
    round_rect(g, 21 + ox + lx, br_y, 12, 9 - min(sy, 2))

    ex = 14 + ox + lx + look * 2
    ey = 12 + oy + sy
    if blink:
        rect(g, ex, ey + 2, 2, 1, "K")
        rect(g, ex + 6, ey + 2, 2, 1, "K")
    else:
        rect(g, ex, ey, 2, 3, "K")
        rect(g, ex + 6, ey, 2, 3, "K")


def confetti(g, frame):
    """Scatter of 1-2px rects. Spreads then thins, like Clawd's burst."""
    bursts = [
        [(8, 6, "Y"), (22, 5, "L"), (16, 3, "W")],
        [(6, 4, "L"), (24, 3, "Y"), (14, 2, "W"), (20, 6, "L"), (10, 5, "W")],
        [(4, 5, "Y"), (26, 4, "W"), (12, 1, "L"), (22, 2, "Y"), (18, 4, "W"), (8, 3, "L")],
        [(5, 8, "L"), (25, 7, "Y"), (15, 4, "W"), (21, 5, "L")],
        [(7, 11, "Y"), (23, 10, "W"), (13, 8, "L")],
        [(9, 14, "L"), (21, 13, "Y")],
        [(11, 16, "W")],
        [],
    ]
    for x, y, c in bursts[frame % len(bursts)]:
        rect(g, x, y, 2 if c != "W" else 1, 2 if c != "W" else 1, c)


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


def save_gif(frames_img, durs, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    pal, index = _palette_image()
    converted = [rgba_to_p(im, pal, index) for im in frames_img]
    converted[0].save(
        path,
        save_all=True,
        append_images=converted[1:],
        duration=durs,
        loop=0,
        disposal=2,
        transparency=0,
        optimize=False,
    )


def idle_frames():
    """Look left, hold, look right, blink, breathe. Uneven holds like Clawd gym."""
    poses = [
        dict(look=0, squash=0, blink=False),
        dict(look=-1, squash=0, blink=False),
        dict(look=-1, squash=1, blink=False),
        dict(look=0, squash=0, blink=False),
        dict(look=1, squash=0, blink=False),
        dict(look=1, squash=1, blink=False),
        dict(look=0, squash=0, blink=True),
        dict(look=0, squash=0, blink=False),
        dict(look=0, squash=2, blink=False),
        dict(look=0, squash=0, blink=False),
    ]
    durs = [280, 420, 180, 220, 420, 180, 90, 260, 160, 300]
    frames = []
    for p in poses:
        g = blank()
        draw_cloud(g, **p)
        frames.append(g)
    return frames, durs


def wave_frames():
    """Body sways opposite the lifted UR bump. Feet planted."""
    poses = [
        dict(lift_ur=0, lean=0, squash=0),
        dict(lift_ur=1, lean=0, squash=0),
        dict(lift_ur=3, lean=1, squash=1),
        dict(lift_ur=4, lean=2, squash=0),
        dict(lift_ur=2, lean=0, squash=0),
        dict(lift_ur=4, lean=-1, squash=1),
        dict(lift_ur=3, lean=-2, squash=0),
        dict(lift_ur=1, lean=0, squash=0),
    ]
    durs = [110, 110, 125, 125, 110, 125, 125, 110]
    frames = []
    for p in poses:
        g = blank()
        draw_cloud(g, **p)
        frames.append(g)
    return frames, durs


def walk_frames():
    """In-place walk: opposite lobes, squash on plant, eyes look forward."""
    poses = [
        dict(step=-1, squash=1, lean=-1, look=-1),
        dict(step=0, squash=0, lean=0, look=0),
        dict(step=1, squash=1, lean=1, look=1),
        dict(step=0, squash=0, lean=0, look=0),
        dict(step=-1, squash=2, lean=-1, look=-1),
        dict(step=0, squash=0, lean=0, look=0),
        dict(step=1, squash=2, lean=1, look=1),
        dict(step=0, squash=0, lean=0, look=0),
    ]
    durs = [125] * 8
    frames = []
    for p in poses:
        g = blank()
        draw_cloud(g, **p)
        frames.append(g)
    return frames, durs


def ship_frames():
    """Stomp + confetti. Clawd's celebrate, Trace's shipping."""
    poses = [
        dict(lean=-2, squash=0, lift_ur=2),
        dict(lean=-1, squash=2, lift_ur=4),
        dict(lean=0, squash=0, lift_ur=1),
        dict(lean=2, squash=0, lift_ur=0),
        dict(lean=1, squash=2, lift_ur=3),
        dict(lean=0, squash=0, lift_ur=1),
        dict(lean=-2, squash=1, lift_ur=3),
        dict(lean=0, squash=0, lift_ur=0),
    ]
    durs = [125] * 8
    frames = []
    for i, p in enumerate(poses):
        g = blank()
        draw_cloud(g, **p)
        confetti(g, i)
        frames.append(g)
    return frames, durs


def box_shadow(grid, scale=5):
    parts = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            parts.append(f"{x * scale}px {y * scale}px 0 0 {CSS_HEX[ch]}")
    return ",\n    ".join(parts)


def write_html(anims):
    css_frames = []
    html_cards = []
    for name, (frames, durs) in anims.items():
        n = len(frames)
        total = sum(durs)
        t = 0
        keys = []
        for i, fr in enumerate(frames):
            pct = 100 * t / total
            keys.append(f"  {pct:.2f}% {{ box-shadow:\n    {box_shadow(fr)}; }}")
            t += durs[i]
        keys.append(f"  100% {{ box-shadow:\n    {box_shadow(frames[0])}; }}")
        css_frames.append(
            f"@keyframes {name} {{\n" + "\n".join(keys) + "\n}\n"
            f".sprite.{name} {{ animation: {name} {total/1000:.2f}s steps(1) infinite; }}\n"
        )
        html_cards.append(
            f'<figure><div class="stage"><i class="sprite {name}"></i></div><figcaption>{name}</figcaption></figure>'
        )
    css = f"""
:root {{ --bg:#07080d; --ink:#ff7870; --muted:#c48a8a; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; background:var(--bg); color:var(--ink);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
header {{ text-align:center; padding:36px 16px 8px; }}
header h1 {{ font-weight:600; letter-spacing:.4em; font-size:14px; margin:0 0 8px; }}
header p {{ color:var(--muted); font-size:13px; }}
main {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:28px; max-width:960px; margin:24px auto 64px; padding:0 20px; }}
figure {{ margin:0; text-align:center; }}
figcaption {{ margin-top:12px; color:var(--muted); letter-spacing:.18em;
  font-size:11px; text-transform:lowercase; }}
.stage {{ width:160px; height:160px; margin:0 auto; image-rendering:pixelated;
  filter: drop-shadow(0 0 14px #e23b3b55); }}
.sprite {{ display:block; width:5px; height:5px; background:transparent; }}
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
  <p>the red cloud. clawd timing. not a crab.</p>
</header>
<main>
  {''.join(html_cards)}
</main>
</html>
"""
    PIXELS_DIR.mkdir(parents=True, exist_ok=True)
    (PIXELS_DIR / "index.html").write_text(html)
    (PIXELS_DIR / "trace.css").write_text(css)


def dump_preview(name, frames, scale=6):
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    for i, g in enumerate(frames):
        to_img(g, scale).save(FRAME_DIR / f"{name}_{i:02d}.png")


def main():
    anims = {
        "idle": idle_frames(),
        "wave": wave_frames(),
        "walk": walk_frames(),
        "ship": ship_frames(),
    }
    write_html(anims)
    GIF_DIR.mkdir(parents=True, exist_ok=True)
    scale = 6
    # keep think.gif as a look-down alias of idle's thinking beat for the README
    think_frames = []
    think_durs = []
    for look, sq, blink, d in [
        (0, 0, False, 200),
        (0, 1, False, 180),
        (-1, 0, False, 400),
        (-1, 1, False, 180),
        (1, 0, False, 400),
        (1, 1, False, 180),
        (0, 0, True, 90),
        (0, 2, False, 220),
    ]:
        g = blank()
        draw_cloud(g, look=look, squash=sq, blink=blink)
        think_frames.append(g)
        think_durs.append(d)

    for name, (frames, durs) in {**anims, "think": (think_frames, think_durs)}.items():
        dump_preview(name, frames, scale)
        imgs = [to_img(g, scale) for g in frames]
        save_gif(imgs, durs, GIF_DIR / f"{name}.gif")
        print("wrote", name, len(frames))


if __name__ == "__main__":
    main()
