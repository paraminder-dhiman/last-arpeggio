import math
from PIL import Image, ImageChops, ImageDraw, ImageFilter
import customtkinter as ctk

K = 4  # draw at 4x, then shrink for smooth lines

def _draw(kind, colour):
    img = Image.new("RGBA", (18 * K, 18 * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = round(1.6 * K)

    def line(*pts):
        d.line([(x * K, y * K) for x, y in pts], fill=colour, width=w, joint="curve")

    def ring(cx, cy, r):
        d.ellipse([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], outline=colour, width=w)

    if kind == "library":
        for y, end in ((4, 11), (9, 10), (14, 10)):
            line((1, y), (end, y))
        line((15, 3), (15, 13))
        line((15, 3), (18, 4.5))
        ring(13, 13.5, 2.2)
    elif kind == "import":
        line((9, 1), (9, 11))
        line((5, 7), (9, 11), (13, 7))
        line((2, 11), (2, 16), (16, 16), (16, 11))
    elif kind == "settings":
        for y, x in ((4, 12), (9, 6), (14, 10)):
            line((1, y), (17, y))
            d.ellipse([(x - 2.3) * K, (y - 2.3) * K, (x + 2.3) * K, (y + 2.3) * K], fill=(0, 0, 0, 0), outline=colour, width=w)
    elif kind == "sun":
        ring(9, 9, 3.4)
        for a in range(0, 360, 45):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            line((9 + c * 6, 9 + s * 6), (9 + c * 8.2, 9 + s * 8.2))
    elif kind == "moon":
        # a crescent: a full disc with a smaller disc cut out of its top right, then only its outline kept
        shape = Image.new("L", img.size, 0)
        m = ImageDraw.Draw(shape)
        m.ellipse([1.8 * K, 1.8 * K, 16.2 * K, 16.2 * K], fill=255)
        m.ellipse([6.4 * K, -1.2 * K, 19.4 * K, 11.8 * K], fill=0)
        inside = shape.filter(ImageFilter.MinFilter(2 * w + 1))
        outline = ImageChops.subtract(shape, inside)
        img.paste(Image.new("RGBA", img.size, colour), (0, 0), outline)
    return img.resize((36, 36), Image.LANCZOS)

def icon(kind, colors, size=18):
    light, dark = colors
    return ctk.CTkImage(_draw(kind, light), _draw(kind, dark), (size, size))

def theme_toggle(colors, size=18):
    light, dark = colors
    # light mode shows the moon (switch to dark), dark mode shows the sun
    return ctk.CTkImage(_draw("moon", light), _draw("sun", dark), (size, size))