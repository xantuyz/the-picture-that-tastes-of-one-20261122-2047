#!/usr/bin/env python3
"""Render one giant macro strawberry to entry.png (1024x1024).

Procedural Pillow artwork for make.fun bounty
the-picture-that-tastes-of-one-20261122-2047.
Run: python3 render.py  -> writes entry.png next to this file.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

S = 2                      # supersample factor (draw at 2048, downscale)
W = H = 1024 * S

CX = 1024                  # fruit centre x (at 2x scale)
TOP = 480                  # fruit top y
BOT = 1760                 # fruit tip y
FH = BOT - TOP             # fruit height
HALF = 620                 # max half-width of the fruit


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def half_width(t):
    """Half-width of the strawberry at fraction t (0 = top, 1 = tip).

    Rounded shoulders (narrow at the very top, full width by t~0.18)
    then a steady taper to a point at the tip.
    """
    if t <= 0:
        return HALF * 0.35
    if t >= 1:
        return 0.0
    shoulder = 0.35 + 0.65 * min(1.0, t / 0.18) ** 0.7
    taper = (1.0 - t ** 2.4) ** 0.8
    return HALF * shoulder * taper


def background():
    """Dark charcoal-green radial gradient, lighter in the centre."""
    small = Image.new("RGB", (256, 256))
    d = ImageDraw.Draw(small)
    centre = (128, 128)
    c_in = (20, 26, 22)    # #141a16
    c_out = (7, 9, 10)     # #07090a
    for r in range(256, 0, -1):
        t = r / 256.0
        d.ellipse([centre[0] - r, centre[1] - r,
                   centre[0] + r, centre[1] + r],
                  fill=lerp_color(c_in, c_out, t))
    img = small.resize((W, H), Image.BICUBIC)
    return img.filter(ImageFilter.GaussianBlur(2))


def fruit_mask():
    """Silhouette of the strawberry: wide shoulders, tapering tip."""
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    pts = []
    # top edge: shallow dip in the middle where the calyx sits
    for i in range(41):
        x = -half_width(0) + 2 * half_width(0) * i / 40.0
        y = TOP + 34 * (1.0 - (x / half_width(0)) ** 2)
        pts.append((CX + x, y))
    # right side, top -> tip
    for i in range(1, 61):
        t = i / 60.0
        pts.append((CX + half_width(t), TOP + t * FH))
    # left side, tip -> top
    for i in range(59, 0, -1):
        t = i / 60.0
        pts.append((CX - half_width(t), TOP + t * FH))
    d.polygon(pts, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(3))


def fruit_body(mask):
    """Red vertical gradient + soft light/shadow, clipped to the mask."""
    # vertical gradient: bright red -> mid red -> deep shadow red
    grad = Image.new("RGB", (1, 256))
    gd = ImageDraw.Draw(grad)
    stops = [(0.0, (255, 45, 58)), (0.45, (214, 31, 43)), (1.0, (143, 15, 28))]
    for y in range(256):
        t = y / 255.0
        if t < 0.45:
            col = lerp_color(stops[0][1], stops[1][1], t / 0.45)
        else:
            col = lerp_color(stops[1][1], stops[2][1], (t - 0.45) / 0.55)
        gd.point((0, y), fill=col)
    body = grad.resize((W, H), Image.BICUBIC).convert("RGBA")

    # soft light wash, upper left
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    ld.ellipse([CX - 700, TOP - 260, CX + 220, TOP + 620],
               fill=(255, 130, 115, 60))
    light = light.filter(ImageFilter.GaussianBlur(110))
    body.alpha_composite(light)

    # deep shadow, lower right
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dark)
    dd.ellipse([CX - 120, TOP + 520, CX + 760, BOT + 160],
               fill=(52, 0, 10, 105))
    dark = dark.filter(ImageFilter.GaussianBlur(130))
    body.alpha_composite(dark)

    # glossy highlight, upper left of the body
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(gloss)
    gd2.ellipse([CX - 480, TOP + 90, CX - 60, TOP + 330],
                fill=(255, 255, 255, 46))
    gloss = gloss.filter(ImageFilter.GaussianBlur(42))
    body.alpha_composite(gloss)

    # clip to the fruit silhouette
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(body, (0, 0), mask)
    return out


def draw_seed(layer, x, y, w, h, angle):
    """One pale seed with a faint shadow, rotated to follow the surface."""
    pad = 14
    tile = Image.new("RGBA", (int(w) + 2 * pad, int(h) + 2 * pad), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    # faint shadow just below the seed
    td.ellipse([pad + 1, pad + 3, pad + w - 1, pad + h + 1],
               fill=(120, 10, 20, 130))
    # pale yellow seed with a golden rim
    td.ellipse([pad, pad, pad + w, pad + h], fill=(247, 224, 138, 255),
               outline=(198, 158, 62, 255), width=2)
    td.ellipse([pad + 2, pad + 2, pad + w - 4, pad + h - 6],
               fill=(252, 236, 170, 255))
    tile = tile.rotate(angle, resample=Image.BICUBIC, expand=False)
    layer.alpha_composite(tile, (int(x - tile.width // 2),
                                 int(y - tile.height // 2)))


def seeds_layer(mask):
    """~70 seeds in 9 curving rows that follow the fruit's contour."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rng = random.Random(20261122)
    rows = 9
    for r in range(rows):
        t = 0.14 + 0.78 * r / (rows - 1)
        y = TOP + t * FH
        hw = half_width(t)
        if hw < 40:
            continue
        n = max(3, int(2 * hw / 110))
        size = lerp(38, 18, t)          # seeds shrink towards the tip
        for i in range(n):
            fx = -0.88 + 1.76 * i / max(n - 1, 1)
            fx += rng.uniform(-0.03, 0.03)
            x = CX + fx * hw
            # rows bow downwards at the edges, following the surface
            yy = y + 26 * fx * fx + rng.uniform(-6, 6)
            angle = fx * 28
            draw_seed(layer, x, yy, size * 0.62, size,
                      -angle if fx < 0 else angle)
    # clip seeds to the fruit
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(layer, (0, 0), mask)
    return out


def calyx_layer():
    """Star of 6 pointed green leaves + a short stem on top."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    base = (CX, TOP + 52)
    leaf_defs = [
        (-78, 330, 96, (47, 125, 50)),
        (-48, 360, 104, (63, 148, 66)),
        (-18, 330, 100, (47, 125, 50)),
        (12, 350, 104, (87, 168, 79)),
        (44, 360, 100, (47, 125, 50)),
        (74, 320, 92, (63, 148, 66)),
    ]
    for deg, length, width, col in leaf_defs:
        a = math.radians(deg)
        dx, dy = math.sin(a), -math.cos(a)   # 0 deg = straight up
        px, py = -dy, dx                    # perpendicular
        tip = (base[0] + dx * length, base[1] + dy * length)
        left = (base[0] + px * width * 0.5 + dx * length * 0.38,
                base[1] + py * width * 0.5 + dy * length * 0.38)
        right = (base[0] - px * width * 0.5 + dx * length * 0.38,
                 base[1] - py * width * 0.5 + dy * length * 0.38)
        d.polygon([base, left, tip, right], fill=col + (255,))
        # centre vein
        vein_end = (base[0] + dx * length * 0.82,
                    base[1] + dy * length * 0.82)
        d.line([base, vein_end], fill=(190, 225, 160, 200), width=5)
    # stem last so it pokes out above the leaves
    d.line([(CX + 10, TOP + 40), (CX + 54, TOP - 235)],
           fill=(92, 122, 58, 255), width=28)
    d.line([(CX + 10, TOP + 40), (CX + 54, TOP - 235)],
           fill=(122, 150, 84, 255), width=11)
    return layer.filter(ImageFilter.GaussianBlur(1))


def dew_layer(mask):
    """A few translucent dew drops with bright rims."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = random.Random(7)
    spots = []
    # two larger drops near the gloss highlight
    spots.append((CX - 300, TOP + 260, 30))
    spots.append((CX - 190, TOP + 380, 24))
    for _ in range(7):
        t = rng.uniform(0.15, 0.75)
        hw = half_width(t)
        fx = rng.uniform(-0.7, 0.7)
        spots.append((CX + fx * hw, TOP + t * FH + rng.uniform(-20, 20),
                      rng.uniform(10, 18)))
    for x, y, r in spots:
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=(255, 255, 255, 26),
                  outline=(255, 255, 255, 150), width=4)
        d.ellipse([x - r * 0.45, y - r * 0.55, x - r * 0.05, y - r * 0.15],
                  fill=(255, 255, 255, 220))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(layer, (0, 0), mask)
    return out


def main():
    img = background().convert("RGBA")

    # soft ground shadow under the fruit
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([CX - 520, BOT - 60, CX + 520, BOT + 150],
               fill=(0, 0, 0, 115))
    shadow = shadow.filter(ImageFilter.GaussianBlur(60))
    img.alpha_composite(shadow)

    mask = fruit_mask()
    img.alpha_composite(fruit_body(mask))
    img.alpha_composite(seeds_layer(mask))
    img.alpha_composite(calyx_layer())
    img.alpha_composite(dew_layer(mask))

    # downscale to the final 1024x1024
    img = img.resize((1024, 1024), Image.LANCZOS).convert("RGB")

    # very faint grain so the surface does not look flat/plastic
    noise = Image.effect_noise((1024, 1024), 20).convert("RGB")
    img = Image.blend(img, noise, 0.035)

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print("wrote %s (%d bytes)" % (OUT, size))
    if size >= 1048576:
        print("WARNING: entry.png exceeds 1 MiB")


if __name__ == "__main__":
    main()
