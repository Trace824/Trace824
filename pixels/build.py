#!/usr/bin/env python3
"""Trace pixel sprite: HTML/CSS animations + GIF render."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GIF_DIR = ROOT / "gifs"
FRAME_DIR = ROOT / "frames"
PIXELS_DIR = ROOT / "pixels"

PALETTE = {
    ".": None,
    "K": (11, 16, 32, 255),
    "D": (26, 39, 68, 255),
    "B": (46, 63, 104, 255),
    "L": (74, 93, 138, 255),
    "C": (92, 225, 255, 255),
    "G": (214, 251, 255, 255),
    "W": (255, 255, 255, 255),
    "R": (255, 90, 106, 255),
    "P": (255, 180, 186, 255),
    "V": (139, 124, 255, 255),
    "N": (26, 90, 102, 255),
    "O": (196, 132, 72, 255),  # crate
    "Y": (232, 176, 96, 255),
}

CSS_HEX = {
    "K": "#0b1020",
    "D": "#1a2744",
    "B": "#2e3f68",
    "L": "#4a5d8a",
    "C": "#5ce1ff",
    "G": "#d6fbff",
    "W": "#ffffff",
    "R": "#ff5a6a",
    "P": "#ffb4ba",
    "V": "#8b7cff",
    "N": "#1a5a66",
    "O": "#c48448",
    "Y": "#e8b060",
}

W, H = 22, 22


def blank():
    return [["." for _ in range(W)] for _ in range(H)]


def setp(g, x, y, c):
    if 0 <= y < H and 0 <= x < W:
        g[y][x] = c


def blit(g, x, y, rows):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != " ":
                setp(g, x + i, y + j, ch)


def draw_body(g, ox=0, oy=0, blink=False, antenna="bright", mouth="smile"):
    """Chibi Trace: big head, cyan node-eye, T chest, red boots."""
    # antenna: a little T with a glowing node, like the mark
    if antenna == "bright":
        blit(g, 9 + ox, 0 + oy, ["CGC", "NCN", "NCN"])
        setp(g, 10 + ox, 0 + oy, "W")
    elif antenna == "mid":
        blit(g, 9 + ox, 0 + oy, ["CCC", "NCN", "NCN"])
    else:
        blit(g, 9 + ox, 1 + oy, ["CCC", "NCN"])

    # head outline + fill
    head = [
        " KKKKKKKKK ",
        "KBBBBBBBBBK",
        "KBBBBBBBBBK",
        "KBBBBBBBBBK",
        "KBBBBBBBBBK",
        "KBBBBBBBBBK",
        "KBBBBBBBBBK",
        " KBBBBBBBK ",
        "  KKKKKKK  ",
    ]
    blit(g, 6 + ox, 3 + oy, head)

    # left eye = glowing node (the Trace mark)
    if blink:
        blit(g, 8 + ox, 6 + oy, ["CCC", "KKK"])
        blit(g, 13 + ox, 6 + oy, ["CC", "KK"])
    else:
        blit(g, 8 + ox, 5 + oy, ["CCC", "CGC", "CCC"])
        setp(g, 9 + ox, 6 + oy, "W")
        # small right eye
        blit(g, 13 + ox, 6 + oy, ["L", "G", "L"])
        setp(g, 13 + ox, 7 + oy, "C")

    # mouth
    if mouth == "smile":
        setp(g, 10 + ox, 8 + oy, "K")
        setp(g, 11 + ox, 9 + oy, "K")
        setp(g, 12 + ox, 8 + oy, "K")
    elif mouth == "o":
        setp(g, 11 + ox, 8 + oy, "K")
        setp(g, 10 + ox, 9 + oy, "K")
        setp(g, 12 + ox, 9 + oy, "K")
        setp(g, 11 + ox, 10 + oy, "K")
    elif mouth == "grin":
        setp(g, 9 + ox, 8 + oy, "K")
        setp(g, 10 + ox, 9 + oy, "K")
        setp(g, 11 + ox, 9 + oy, "K")
        setp(g, 12 + ox, 9 + oy, "K")
        setp(g, 13 + ox, 8 + oy, "K")

    # torso
    torso = [
        " KBBBBBBK ",
        "KBBBBBBBBK",
        "KBBBBBBBBK",
        "KBBBBBBBBK",
        "KBBBBBBBBK",
        " KBBBBBBK ",
    ]
    blit(g, 6 + ox, 11 + oy, torso)

    # cyan T emblem (the mark, chest-sized)
    blit(g, 8 + ox, 13 + oy, ["CCCCC", "NNCNN", "NNCNN"])

    # legs + red boots
    blit(g, 8 + ox, 17 + oy, ["KK", "BB", "RR", "KK"])
    blit(g, 12 + ox, 17 + oy, ["KK", "BB", "RR", "KK"])


def draw_arm_down(g, side, ox=0, oy=0):
    if side == "left":
        blit(g, 5 + ox, 12 + oy, ["K", "B", "B", "K"])
    else:
        blit(g, 16 + ox, 12 + oy, ["K", "B", "B", "K"])


def draw_arm_wave(g, phase, ox=0, oy=0):
    """phase 0=up, 1=mid, 2=out."""
    draw_arm_down(g, "left", ox, oy)
    if phase == 0:
        blit(g, 16 + ox, 8 + oy, ["  K", " CB", "KC ", " K "])
        setp(g, 18 + ox, 7 + oy, "P")  # hand
    elif phase == 1:
        blit(g, 16 + ox, 9 + oy, [" K", "CB", "K ", "  "])
        setp(g, 18 + ox, 9 + oy, "P")
        setp(g, 19 + ox, 8 + oy, "P")
    else:
        blit(g, 16 + ox, 10 + oy, ["K  ", "BCK", "K  "])
        setp(g, 19 + ox, 11 + oy, "P")


def draw_arm_think(g, ox=0, oy=0):
    draw_arm_down(g, "left", ox, oy)
    # right hand on chin
    blit(g, 15 + ox, 9 + oy, [" K", "PB", "K "])
    setp(g, 16 + ox, 10 + oy, "B")


def draw_glass(g, ox=0, oy=0, up=0):
    y = 8 + oy - up
    x = 15 + ox
    blit(g, x, y, [" CC", "C C", " CC"])
    setp(g, x + 1, y + 3, "K")
    setp(g, x + 2, y + 4, "K")


def draw_crate(g, ox=0, oy=0, bounce=0):
    y = 14 + oy - bounce
    x = 15 + ox
    blit(
        g,
        x,
        y,
        [
            "KKKK",
            "KYYK",
            "KYOK",
            "KKKK",
        ],
    )
    setp(g, x + 1, y + 1, "V")  # tiny "label"


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


def grid_copy(g):
    return [row[:] for row in g]


def idle_frames():
    out = []
    for i, (oy, ant, blink) in enumerate(
        [
            (0, "bright", False),
            (0, "bright", False),
            (1, "mid", False),
            (1, "dim", False),
            (0, "mid", False),
            (0, "bright", True),
            (0, "bright", False),
            (1, "mid", False),
        ]
    ):
        g = blank()
        draw_body(g, oy=oy, blink=blink, antenna=ant)
        draw_arm_down(g, "left", oy=oy)
        draw_arm_down(g, "right", oy=oy)
        out.append(g)
    return out


def wave_frames():
    out = []
    phases = [0, 1, 2, 1, 0, 1, 2, 1]
    for i, ph in enumerate(phases):
        oy = i % 2
        g = blank()
        draw_body(g, oy=oy, antenna="bright" if i % 2 == 0 else "mid", mouth="grin")
        draw_arm_wave(g, ph, oy=oy)
        out.append(g)
    return out


def think_frames():
    out = []
    dots = [
        [],
        [(11, 0, "C")],
        [(11, 0, "C"), (13, 1, "C")],
        [(11, 0, "G"), (13, 1, "C"), (15, 0, "C")],
        [(13, 1, "C"), (15, 0, "G")],
        [(15, 0, "C")],
        [],
        [(11, 0, "C")],
    ]
    for i, ds in enumerate(dots):
        g = blank()
        draw_body(g, antenna="mid" if i % 2 else "bright", mouth="o")
        draw_arm_think(g)
        draw_glass(g, up=i % 2)
        for x, y, c in ds:
            setp(g, x, y, c)
        out.append(g)
    return out


def ship_frames():
    out = []
    for i in range(8):
        oy = i % 2
        bounce = 1 if i % 4 >= 2 else 0
        g = blank()
        draw_body(g, oy=oy, antenna="bright" if i % 2 == 0 else "mid", mouth="grin")
        draw_arm_down(g, "left", oy=oy)
        # right arm holding crate
        blit(g, 16, 12 + oy, ["K", "B"])
        draw_crate(g, oy=oy, bounce=bounce)
        out.append(g)
    return out


def box_shadow(grid, scale=8):
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
:root {{
  --bg: #07080d;
  --ink: #d6fbff;
  --muted: #8aa0c8;
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}}
header {{
  text-align: center; padding: 36px 16px 8px;
}}
header h1 {{
  font-weight: 600; letter-spacing: .4em; font-size: 14px; margin: 0 0 8px;
}}
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
  width: 132px; height: 132px; margin: 0 auto;
  image-rendering: pixelated;
  filter: drop-shadow(0 0 12px #5ce1ff44);
}}
.sprite {{
  display: block; width: 6px; height: 6px;
  background: transparent;
}}
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
  <p>cute 8-bit, html + css. i don't guess. i look.</p>
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
    durations = {"idle": 140, "wave": 110, "think": 160, "ship": 120}
    for name, frames in anims.items():
        dump_preview(name, frames, scale)
        imgs = [to_img(g, scale) for g in frames]
        save_gif(imgs, GIF_DIR / f"{name}.gif", durations[name])
        print("wrote", name, len(frames), "frames")


if __name__ == "__main__":
    main()
