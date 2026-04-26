"""SVG chart primitive tests (SDLC-072)."""

from __future__ import annotations

import re

import pytest

from sdlc_assessor.renderer.charts import (
    category_radar,
    effort_impact_matrix,
    risk_matrix,
    score_gauge,
    score_lift_trajectory,
)
from sdlc_assessor.renderer.charts._palette import band_for
from sdlc_assessor.renderer.charts.matrix import MatrixPoint
from sdlc_assessor.renderer.charts.trajectory import PhaseLift


def _is_well_formed_svg(svg: str) -> bool:
    return svg.lstrip().startswith("<svg") and svg.rstrip().endswith("</svg>")


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "fail"),
        (35, "fail"),
        (36, "conditional"),
        (55, "conditional"),
        (56, "pass"),
        (75, "pass"),
        (76, "distinction"),
        (100, "distinction"),
    ],
)
def test_band_for_classifies_correctly(score: int, expected: str) -> None:
    assert band_for(score) == expected


# ---------------------------------------------------------------------------
# Score gauge
# ---------------------------------------------------------------------------


def test_score_gauge_well_formed() -> None:
    svg = score_gauge(score=72, verdict="pass")
    assert _is_well_formed_svg(svg)
    assert "72" in svg
    assert 'aria-label' in svg


def test_score_gauge_clamps_score() -> None:
    high = score_gauge(score=200)
    low = score_gauge(score=-10)
    assert "100" in high
    assert "0" in low


def test_score_gauge_renders_verdict_when_provided() -> None:
    svg = score_gauge(score=80, verdict="pass_with_distinction")
    assert "pass with distinction" in svg


def test_score_gauge_omits_verdict_when_none() -> None:
    svg = score_gauge(score=80, verdict=None)
    assert "pass" not in svg.split("</svg>")[0].split("of 100")[1]


# ---------------------------------------------------------------------------
# Category radar
# ---------------------------------------------------------------------------


def test_category_radar_well_formed_with_8_axes() -> None:
    axes = [
        ("architecture_design", 12, 15),
        ("code_quality_contracts", 8, 14),
        ("testing_quality_gates", 15, 15),
        ("security_posture", 5, 21),
        ("dependency_release_hygiene", 9, 11),
        ("documentation_truthfulness", 10, 10),
        ("maintainability_operability", 11, 11),
        ("reproducibility_research_rigor", 3, 3),
    ]
    svg = category_radar(axes=axes)
    assert _is_well_formed_svg(svg)
    # Each label should appear at least once.
    for label, _, _ in axes:
        assert label in svg


def test_category_radar_with_baseline_renders_two_polygons() -> None:
    axes = [("a", 5, 10), ("b", 7, 10), ("c", 3, 10), ("d", 9, 10)]
    baseline = [0.6, 0.6, 0.6, 0.6]
    svg = category_radar(axes=axes, baseline=baseline)
    # Two filled polygons (baseline + score) should produce at least two <path> elements.
    paths = re.findall(r"<path[^>]*d=\"M[^\"]+Z\"", svg)
    # Plus N gridlines that are also closed paths — so we just check ≥2 closed paths.
    assert len(paths) >= 2


def test_category_radar_handles_zero_max() -> None:
    axes = [("a", 0, 0), ("b", 5, 10), ("c", 7, 10)]
    svg = category_radar(axes=axes)
    assert _is_well_formed_svg(svg)


def test_category_radar_returns_message_for_too_few_axes() -> None:
    svg = category_radar(axes=[("a", 5, 10), ("b", 5, 10)])
    assert "Need ≥3" in svg


# ---------------------------------------------------------------------------
# Risk matrix
# ---------------------------------------------------------------------------


def test_risk_matrix_well_formed() -> None:
    svg = risk_matrix(risks=[
        MatrixPoint(label="Bus factor 1", x=0.85, y=0.8, severity="high"),
        MatrixPoint(label="Lockfile gap", x=0.6, y=0.45, severity="medium"),
    ])
    assert _is_well_formed_svg(svg)
    assert "Bus factor 1" in svg
    assert "Likelihood" in svg
    assert "Impact" in svg


def test_risk_matrix_quadrant_labels_present() -> None:
    svg = risk_matrix(risks=[])
    for label in ("Low likelihood", "High likelihood", "High impact", "Low impact"):
        assert label in svg


def test_risk_matrix_with_no_severity_renders_default() -> None:
    svg = risk_matrix(risks=[MatrixPoint(label="Unknown risk", x=0.5, y=0.5)])
    assert _is_well_formed_svg(svg)
    assert "Unknown risk" in svg


# ---------------------------------------------------------------------------
# Effort × impact matrix
# ---------------------------------------------------------------------------


def test_effort_impact_matrix_well_formed() -> None:
    svg = effort_impact_matrix(tasks=[
        MatrixPoint(label="Add CI", x=0.2, y=0.85, severity="high"),
        MatrixPoint(label="Refactor", x=0.8, y=0.3, severity="medium"),
    ])
    assert _is_well_formed_svg(svg)
    assert "DO FIRST" in svg
    assert "DEFER" in svg


# ---------------------------------------------------------------------------
# Score-lift trajectory
# ---------------------------------------------------------------------------


def test_score_lift_trajectory_well_formed() -> None:
    svg = score_lift_trajectory(
        current_score=59,
        phases=[
            PhaseLift(label="Phase 1: Security", delta=12),
            PhaseLift(label="Phase 2: Contracts", delta=8),
        ],
    )
    assert _is_well_formed_svg(svg)
    assert "Phase 1: Security" in svg
    # Current score label.
    assert "Current" in svg


def test_score_lift_trajectory_caps_at_100() -> None:
    svg = score_lift_trajectory(
        current_score=80,
        phases=[PhaseLift(label="Big lift", delta=50)],  # would overshoot
    )
    # No occurrence of "130" — capped to 100.
    assert "130" not in svg


def test_score_lift_trajectory_handles_no_phases() -> None:
    svg = score_lift_trajectory(current_score=50, phases=[])
    assert _is_well_formed_svg(svg)
    assert "Current" in svg


# ---------------------------------------------------------------------------
# XSS / escaping
# ---------------------------------------------------------------------------


def test_charts_escape_label_html() -> None:
    """Labels are user-controlled and may contain HTML metacharacters."""
    nasty = "<script>alert(1)</script>"
    svg = risk_matrix(risks=[MatrixPoint(label=nasty, x=0.5, y=0.5)])
    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg
