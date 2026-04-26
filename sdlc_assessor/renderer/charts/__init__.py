"""SVG chart primitives for persona-aware reports (SDLC-072).

All charts are pure-Python SVG generation — no external libraries, no
external assets, all rendering happens at report-build time. Each chart
is a function that takes a typed payload and returns an SVG string ready
to embed inside the report HTML.

Charts:

- :func:`score_gauge` — circular gauge for the overall score (0–100).
- :func:`category_radar` — 8-axis spider chart for category scores,
  optionally drawn against an archetype baseline.
- :func:`risk_matrix` — 2×2 likelihood × impact grid with risks plotted.
- :func:`effort_impact_matrix` — 2×2 with remediation tasks plotted.
- :func:`score_lift_trajectory` — bar chart showing
  current → projected per-phase score lift.

Design conventions (kept consistent across all charts):

- Single colour palette tied to severity (critical/high/medium/low/info).
- Embedded font stack: ``-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif``.
- ``role="img"`` + ``aria-label`` for screen-reader accessibility.
- ``viewBox`` always declared so the chart scales cleanly.
- No external CSS reliance — all styling is inline so the chart can be
  pasted into any HTML context (including email clients).
"""

from __future__ import annotations

from sdlc_assessor.renderer.charts.gauge import score_gauge
from sdlc_assessor.renderer.charts.matrix import effort_impact_matrix, risk_matrix
from sdlc_assessor.renderer.charts.radar import category_radar
from sdlc_assessor.renderer.charts.trajectory import score_lift_trajectory

__all__ = [
    "category_radar",
    "effort_impact_matrix",
    "risk_matrix",
    "score_gauge",
    "score_lift_trajectory",
]
