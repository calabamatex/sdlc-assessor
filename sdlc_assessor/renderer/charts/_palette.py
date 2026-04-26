"""Shared visual palette for all SVG charts (SDLC-072).

Kept in one module so colour decisions are auditable in a single place.
"""

from __future__ import annotations

# Severity → fill / stroke. Tuned to match the v0.9.0 HTML stylesheet so
# the report reads as one designed artifact, not a chart bolted onto a
# different colour scheme.
SEVERITY_FILL = {
    "critical": "#fbe9e9",
    "high": "#fff0e0",
    "medium": "#fff8d6",
    "low": "#eef5ff",
    "info": "#f0f0f0",
}

SEVERITY_STROKE = {
    "critical": "#861818",
    "high": "#803e00",
    "medium": "#6a5500",
    "low": "#1d4380",
    "info": "#555a60",
}

# Score-band colours for gauges and trajectories.
# 0–35 fail · 36–55 conditional · 56–75 pass · 76–100 distinction.
BAND_FILL = {
    "fail": "#e25d5d",
    "conditional": "#f0a050",
    "pass": "#7bbf6e",
    "distinction": "#3d8c3d",
}


def band_for(score: float) -> str:
    if score >= 76:
        return "distinction"
    if score >= 56:
        return "pass"
    if score >= 36:
        return "conditional"
    return "fail"


# Neutral / supporting colours.
INK = "#111317"
MUTED = "#5d6470"
GRID = "#d8dade"
ACCENT = "#0058a3"
BG = "#ffffff"
BG_ALT = "#f7f8fa"

FONT_STACK = (
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, '
    '"Helvetica Neue", Arial, sans-serif'
)


def font(size: float, *, weight: int | str = 400, color: str = INK) -> str:
    """Return an inline ``font=...`` style fragment for SVG ``<text>``."""
    return (
        f'font-family=\'{FONT_STACK}\' font-size="{size}" '
        f'font-weight="{weight}" fill="{color}"'
    )


__all__ = [
    "ACCENT",
    "BAND_FILL",
    "BG",
    "BG_ALT",
    "FONT_STACK",
    "GRID",
    "INK",
    "MUTED",
    "SEVERITY_FILL",
    "SEVERITY_STROKE",
    "band_for",
    "font",
]
