"""Score gauge chart (SDLC-072).

A circular gauge showing a 0–100 score with band-coloured fill, the
numeric score in the centre, and the verdict label below.
"""

from __future__ import annotations

import math

from sdlc_assessor.renderer.charts._palette import (
    BAND_FILL,
    GRID,
    INK,
    MUTED,
    band_for,
    font,
)


def _arc_path(cx: float, cy: float, r: float, start_deg: float, end_deg: float) -> str:
    """SVG path "d" for an arc from ``start_deg`` to ``end_deg`` (degrees)."""
    start_rad = math.radians(start_deg)
    end_rad = math.radians(end_deg)
    x1 = cx + r * math.cos(start_rad)
    y1 = cy + r * math.sin(start_rad)
    x2 = cx + r * math.cos(end_rad)
    y2 = cy + r * math.sin(end_rad)
    large_arc = 1 if (end_deg - start_deg) > 180 else 0
    return f"M {x1:.2f} {y1:.2f} A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f}"


def score_gauge(
    *,
    score: float,
    verdict: str | None = None,
    width: int = 240,
    height: int = 240,
    title: str = "Overall score",
) -> str:
    """Render a circular score gauge.

    ``score`` is 0–100; the arc fills proportionally and the colour is
    chosen by band (fail / conditional / pass / distinction).
    """
    score = max(0.0, min(100.0, float(score)))
    cx = width / 2
    cy = height / 2
    r = min(width, height) * 0.36
    stroke_w = max(8.0, min(width, height) * 0.08)

    # The arc spans 270° from 135° (lower-left) clockwise to 45° (lower-right).
    arc_start = 135.0
    arc_end_full = 360.0 + 45.0  # 405°, i.e. 45° after a full circle wrap
    arc_total = arc_end_full - arc_start  # 270°
    arc_end_filled = arc_start + (score / 100.0) * arc_total

    band = band_for(score)
    fill = BAND_FILL[band]

    # Background arc (the unfilled portion).
    bg_path = _arc_path(cx, cy, r, arc_start, arc_end_full)
    fill_path = _arc_path(cx, cy, r, arc_start, arc_end_filled)

    # Tick marks at 25/50/75 — annotated, subtle.
    ticks_svg = []
    for tick in (0, 25, 50, 75, 100):
        tick_angle = arc_start + (tick / 100.0) * arc_total
        tx = cx + (r + stroke_w / 2 + 6) * math.cos(math.radians(tick_angle))
        ty = cy + (r + stroke_w / 2 + 6) * math.sin(math.radians(tick_angle))
        ticks_svg.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" {font(9, color=MUTED)} '
            f'text-anchor="middle" dominant-baseline="middle">{tick}</text>'
        )

    score_label = str(int(round(score)))
    verdict_text = verdict.replace("_", " ") if verdict else ""

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{title}: {score_label}/100">',
        f'<title>{title}: {score_label}/100</title>',
        f'<path d="{bg_path}" fill="none" stroke="{GRID}" stroke-width="{stroke_w}" '
        'stroke-linecap="round" />',
        f'<path d="{fill_path}" fill="none" stroke="{fill}" stroke-width="{stroke_w}" '
        'stroke-linecap="round" />',
        "".join(ticks_svg),
        f'<text x="{cx}" y="{cy + 4}" {font(46, weight=700, color=INK)} '
        f'text-anchor="middle" dominant-baseline="middle">{score_label}</text>',
        f'<text x="{cx}" y="{cy + 36}" {font(11, color=MUTED)} '
        'text-anchor="middle" dominant-baseline="middle">of 100</text>',
    ]
    if verdict_text:
        parts.append(
            f'<text x="{cx}" y="{cy + 60}" {font(13, weight=600, color=INK)} '
            f'text-anchor="middle" dominant-baseline="middle">{verdict_text}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


__all__ = ["score_gauge"]
