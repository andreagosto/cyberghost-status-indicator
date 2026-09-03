#!/usr/bin/env python3
"""Generate the "VPN" text icons (green = ON, gray = OFF).

Dependencies: python3-gi + gir1.2-pango-1.0 (+ pango libcairo).
Usage: python3 make-icons.py [output_directory]
"""
import os
import sys

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo  # noqa: E402

CANVAS = 96
FONT_SIZE = 46


def text_icon(text, color, path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, CANVAS, CANVAS)
    ctx = cairo.Context(surf)
    layout = PangoCairo.create_layout(ctx)
    fd = Pango.FontDescription()
    fd.set_family("Ubuntu")
    fd.set_weight(Pango.Weight.BOLD)
    fd.set_absolute_size(int(FONT_SIZE * Pango.SCALE))
    layout.set_font_description(fd)
    layout.set_text(text)
    w, h = layout.get_pixel_size()
    ctx.move_to((CANVAS - w) / 2, (CANVAS - h) / 2 - 2)
    ctx.set_source_rgba(*color)
    PangoCairo.show_layout(ctx, layout)
    surf.write_to_png(path)
    print("generated %s (text %dx%d)" % (path, w, h))


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "icons")
    os.makedirs(outdir, exist_ok=True)
    text_icon("VPN", (0.15, 0.62, 0.41, 1.0), os.path.join(outdir, "vpn-on.png"))
    text_icon("VPN", (0.55, 0.55, 0.55, 1.0), os.path.join(outdir, "vpn-off.png"))


if __name__ == "__main__":
    main()
