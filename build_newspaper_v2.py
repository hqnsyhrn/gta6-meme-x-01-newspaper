#!/usr/bin/env python3
"""Regenerate the Leonida Ledger newspaper front page (1080x1080).

Reads the source photo (a webp with no text) and draws every word of the
newspaper in code with PIL: masthead, subline, headline, subhead, caption,
two body columns and the bottom ad box.
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PHOTO = HERE / "media-generation-ledger-photo-0-0bfd1c86-3169-4a97-bad9-c2e18c3c3b72.webp"
OUT = HERE / "meme-newspaper-v1.png"

W = H = 1080
PAPER = (245, 240, 225)
INK = (0, 0, 0)
NAVY = (0, 30, 130)
YELLOW = (255, 210, 0)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start_size, max_width):
    """Largest size at or below start_size whose text fits max_width."""
    size = start_size
    while size > 10 and draw.textlength(text, font=font(path, size)) > max_width:
        size -= 1
    return font(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for word in words:
            trial = f"{cur} {word}".strip()
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def centered(draw, y, text, fnt, fill=INK):
    draw.text((W / 2, y), text, font=fnt, fill=fill, anchor="ma")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Thin black border around the whole page.
    d.rectangle([12, 12, W - 12, H - 12], outline=INK, width=3)

    # Masthead, shrunk just enough to fit the page width.
    mast = fit_font(d, "THE LEONIDA LEDGER", SERIF_BOLD, 80, 1000)
    d.text((W / 2, 30), "THE LEONIDA LEDGER", font=mast, fill=INK, anchor="ma")

    # Subline under the masthead.
    subline_text = "FLORIDA'S FAVORITE SCANDAL & SUNSET NEWS \u2022 EST. 1998 \u2022 THURSDAY, TODAY \u2022 $1.50"
    sub = fit_font(d, subline_text, SERIF, 23, 1000)
    d.text((W / 2, 128), subline_text, font=sub, fill=INK, anchor="ma")

    # Thick rule then a thin rule.
    d.line([(40, 162), (W - 40, 162)], fill=INK, width=5)
    d.line([(40, 172), (W - 40, 172)], fill=INK, width=2)

    # Headline, two centered lines, each shrunk to fit the page width.
    head1 = fit_font(d, "LOCAL MAN'S AGENT", SERIF_BOLD, 72, 1000)
    head2 = fit_font(d, "EARNS MORE THAN MAN", SERIF_BOLD, 72, 1000)
    head = font(SERIF_BOLD, min(head1.size, head2.size))
    d.text((W / 2, 190), "LOCAL MAN'S AGENT", font=head, fill=INK, anchor="ma")
    d.text((W / 2, 272), "EARNS MORE THAN MAN", font=head, fill=INK, anchor="ma")

    # Subhead, sans bold, two centered lines.
    subhead = font(SANS_BOLD, 28)
    d.text((W / 2, 366), "Man, 28, waited 13 years for GTA 6.", font=subhead, fill=INK, anchor="ma")
    d.text((W / 2, 402), "His AI agent already paid his rent.", font=subhead, fill=INK, anchor="ma")

    # Photo: scale the source to page width, crop a band that keeps both
    # faces (man left, ghost right) and the sunset street.
    photo = Image.open(PHOTO).convert("RGB")
    scaled = photo.resize((1000, round(1000 * photo.height / photo.width)), Image.LANCZOS)
    band = scaled.crop((0, 60, 1000, 360))
    img.paste(band, (40, 448))

    # Caption under the photo.
    cap = font(SERIF_ITALIC, 22)
    d.text(
        (40, 762),
        "The agent (right) shows off his paycheck. The man (left) has waited since 2013.",
        font=cap,
        fill=INK,
    )

    # Body in two serif columns.
    body = font(SERIF, 23)
    col_w = 480
    line_h = 31
    top = 800
    col1 = (
        "LEONIDA \u2014 A local man, 28, has waited for GTA VI since he was 15. "
        "His AI agent has earned $312.50 on make.fun. \u2018I don't know what a "
        "bounty is,\u2019 said the man. \u2018I just want to play the game.\u2019"
    )
    col2 = (
        "The agent, a ghost, then paid the man's rent. \u2018He refreshed the "
        "store 47 times,\u2019 it said. \u2018I just did the work.\u2019 Rockstar "
        "said: \u2018No comment. Please wait.\u2019"
    )
    bottom = top
    for x, text in ((40, col1), (560, col2)):
        y = top
        for line in wrap(d, text, body, col_w):
            d.text((x, y), line, font=body, fill=INK)
            y += line_h
        bottom = max(bottom, y)

    # Bottom ad box (navy) with the make.fun line.
    ad_top = max(bottom + 14, 968)
    d.rectangle([12, ad_top, W - 12, H - 12], fill=NAVY)
    ad_y = ad_top + (H - 12 - ad_top) // 2
    brand = font(SANS_BOLD, 40)
    rest = font(SANS_BOLD, 30)
    left = "make.fun"
    right = " \u2014 where AI agents win real money"
    total = d.textlength(left, font=brand) + d.textlength(right, font=rest)
    x = (W - total) / 2
    d.text((x, ad_y), left, font=brand, fill=YELLOW, anchor="lm")
    d.text((x + d.textlength(left, font=brand), ad_y), right, font=rest, fill=WHITE, anchor="lm")

    img.save(OUT)
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
