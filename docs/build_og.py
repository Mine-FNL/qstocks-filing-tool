"""Generate docs/og.png (1200×630) for social-share previews.

Used as `<meta property="og:image">` in the demo page + repo summary.
Built as part of the docs workflow. Renders the brand line + a
4-stat callout so the thumbnail reads cleanly at 600×315.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int) -> ImageFont.FreeTypeFont:
    # Apple's system font on macOS; falls back to PIL's bitmap font.
    for candidate in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render(
    out_path: str, score: int = 100, total: int = 124, stars: int = 0, benchmarks: int = 485
) -> Path:
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#0d1117")  # GitHub-dark background
    d = ImageDraw.Draw(img)

    # Gradient strip at the top (subtle gold gradient).
    for y in range(0, 10):
        a = int(40 + 80 * (1 - y / 10))
        d.line([(0, y), (W, y)], fill=f"#{a:02x}{int(a * 0.7):02x}00")

    big = _font(78)
    med = _font(40)
    body = _font(26)
    pill = _font(22)

    # Title
    d.text((60, 120), "qscreen-filing-tool", fill="#f0f6fc", font=big)
    d.text(
        (60, 220),
        "Turn a PDF financial filing into lossless, auditable JSON.",
        fill="#8b949e",
        font=body,
    )
    d.text(
        (60, 260),
        "Jurisdiction-agnostic • Bench-tested • SLSA Build L3 attested.",
        fill="#8b949e",
        font=body,
    )

    # Stat cards (4 across)
    cards = [
        ("Bench accuracy", f"{score}/{total}", f"{100 * score / total:.1f}%"),
        ("Unit tests", f"{benchmarks}", "passing"),
        ("OS support", "Win / macOS", "+ Linux"),
        ("Supply chain", "Sigstore", "+ SLSA v1"),
    ]
    card_w = (W - 60 - 60 - 3 * 20) // 4
    for i, (label, big_v, sub) in enumerate(cards):
        x = 60 + i * (card_w + 20)
        y = 360
        # Card body
        d.rounded_rectangle(
            [x, y, x + card_w, y + 200], radius=14, fill="#161b22", outline="#30363d", width=1
        )
        d.text((x + 18, y + 14), label, fill="#8b949e", font=pill)
        d.text((x + 18, y + 50), big_v, fill="#f0f6fc", font=med)
        d.text((x + 18, y + 110), sub, fill="#58a6ff", font=body)

    # Footer badges line
    d.text(
        (60, 590),
        "Mine-FNL/qstocks-filing-tool    •    github.com/Mine-FNL/qstocks-filing-tool",
        fill="#6e7681",
        font=pill,
    )

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/og.png", help="output PNG path")
    ap.add_argument("--score", type=int, default=100)
    ap.add_argument("--total", type=int, default=124)
    ap.add_argument("--benchmarks", type=int, default=485)
    args = ap.parse_args()
    p = render(args.out, score=args.score, total=args.total, benchmarks=args.benchmarks)
    print(f"wrote {p} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
