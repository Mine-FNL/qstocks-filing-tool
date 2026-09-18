#!/usr/bin/env python3
"""Render caption strips as transparent PNGs for ffmpeg overlay.

For each video, generates 2 caption strips (timed chunks). Each strip is a
1934×180 transparent PNG with white text + black outline, centered.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

VIDEO_W = 1934
CAPTION_H = 180
FONT_PATH = "/System/Library/Fonts/Supplemental/Verdana Bold.ttf"
FONT_SIZE = 64

OUT_DIR = Path("/tmp/captions")

VIDEOS = {
    "why-1-pain": [
        (1.20, 3.80, "Today's PDF extractors are slow,"),
        (3.80, 5.43, "expensive and silent about contradictions."),
    ],
    "why-2-gate": [
        (0.40, 2.40, "Most extractors ship the JSON"),
        (2.40, 4.79, "regardless of internal consistency."),
    ],
    "why-3-proof": [
        (0.40, 2.40, "Re-ingest the same PDF on any commit,"),
        (2.40, 4.84, "same SHA-256 fingerprint — always."),
    ],
}


def render_caption(text: str, out_path: Path) -> None:
    img = Image.new("RGBA", (VIDEO_W, CAPTION_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Pillow 10+ uses textbbox; fall back to textsize on older versions.
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=4)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    else:
        text_w, text_h = draw.textsize(text, font=font, stroke_width=4)  # type: ignore[attr-defined]

    x = (VIDEO_W - text_w) // 2
    y = (CAPTION_H - text_h) // 2

    if hasattr(draw, "text"):
        draw.text(
            (x, y),
            text,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=4,
            stroke_fill=(0, 0, 0, 220),
        )
    img.save(out_path, "PNG")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_DIR,
        help="Output directory for caption PNGs (default: %(default)s)",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    for slug, chunks in VIDEOS.items():
        for idx, (start, end, text) in enumerate(chunks, start=1):
            out = args.out / f"{slug}-cap-{idx}.png"
            render_caption(text, out)
            print(f"  {out.name}  {start:>4.2f}s-{end:>4.2f}s  ({len(text)} chars)")


if __name__ == "__main__":
    main()
