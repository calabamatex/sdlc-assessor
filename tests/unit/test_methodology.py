"""Tests for the methodology + glossary registry (0.11.0 depth pass).

Every glossary entry must cite a real code path. Every methodology
claim must reference a source. The 0.11.0 cut explicitly excludes
editorial / unsourced definitions.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from sdlc_assessor.renderer.deliverables._methodology import (
    all_glossary_terms,
    glossary_for,
    methodology_for,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _scored_for(use_case: str) -> dict:
    return {
        "classification": {"repo_archetype": "service", "maturity_profile": "production"},
        "scoring": {"effective_profile": {"use_case": use_case, "maturity": "production"}},
    }


# ---------------------------------------------------------------------------
# Methodology
# ---------------------------------------------------------------------------


def test_methodology_formula_names_real_constants() -> None:
    m = methodology_for(_scored_for("acquisition_diligence"), "acquisition_diligence")
    formula = m.score_formula
    for token in (
        "SEVERITY_WEIGHTS",
        "CONFIDENCE_MULTIPLIERS",
        "maturity_severity_multiplier",
        "BASE_WEIGHTS",
    ):
        assert token in formula


def test_methodology_threshold_explanation_names_use_case() -> None:
    m = methodology_for(_scored_for("vc_diligence"), "vc_diligence")
    assert "vc_diligence" in m.threshold_explanation
    assert "use_case_profiles.json" in m.threshold_explanation


def test_methodology_threshold_explanation_discloses_internal_calibration() -> None:
    """The reader must know the threshold is internal-rubric, not real-outcome."""
    m = methodology_for(_scored_for("acquisition_diligence"), "acquisition_diligence")
    assert "internal rubric" in m.threshold_explanation
    assert "0.14.0" in m.threshold_explanation  # points to the corpus phase


def test_methodology_multiplier_explanation_lists_three_multipliers() -> None:
    m = methodology_for(_scored_for("engineering_triage"), "engineering_triage")
    assert "SEVERITY_WEIGHTS" in m.multiplier_explanation
    assert "CONFIDENCE_MULTIPLIERS" in m.multiplier_explanation
    assert "severity_multiplier" in m.multiplier_explanation


def test_methodology_verdict_rule_table_has_four_rules_and_sources() -> None:
    m = methodology_for(_scored_for("acquisition_diligence"), "acquisition_diligence")
    verdicts = {r["verdict"] for r in m.verdict_rule_table}
    assert verdicts == {"pass_with_distinction", "pass", "conditional_pass", "fail"}
    for rule in m.verdict_rule_table:
        assert "scorer/engine.py" in rule["source"]


def test_methodology_calibration_band_discloses_internal_corpus() -> None:
    m = methodology_for(_scored_for("acquisition_diligence"), "acquisition_diligence")
    assert m.calibration_band is not None
    assert "internal fixture corpus" in m.calibration_band
    assert "not real-world outcomes" in m.calibration_band


# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "use_case",
    [
        "acquisition_diligence",
        "vc_diligence",
        "engineering_triage",
        "remediation_agent",
    ],
)
def test_glossary_present_for_persona(use_case: str) -> None:
    g = glossary_for(use_case)
    assert len(g) >= 4
    # Every entry has a non-empty short_def AND at least one source.
    for entry in g:
        assert entry.term
        assert entry.short_def
        assert entry.sources


def test_glossary_entries_cite_real_paths() -> None:
    """Every source path in every glossary entry resolves to a real file in this repo."""
    for term_key in all_glossary_terms():
        from sdlc_assessor.renderer.deliverables._methodology import _GLOSSARY_REGISTRY

        entry = _GLOSSARY_REGISTRY[term_key]
        for src in entry.sources:
            # Strip line numbers (e.g. "scorer/engine.py:24") for existence check.
            path_only = src.split(":", 1)[0]
            full_path = REPO_ROOT / path_only
            assert full_path.exists(), f"glossary entry {term_key!r} cites missing path {src!r}"


def test_glossary_line_citations_resolve_to_actual_lines() -> None:
    """Glossary entries that cite a specific line number must be in-bounds."""
    from sdlc_assessor.renderer.deliverables._methodology import _GLOSSARY_REGISTRY

    for term_key, entry in _GLOSSARY_REGISTRY.items():
        for src in entry.sources:
            if ":" not in src:
                continue
            path_str, line_str = src.rsplit(":", 1)
            if not line_str.isdigit():
                continue
            full_path = REPO_ROOT / path_str
            line_count = sum(1 for _ in full_path.open())
            assert int(line_str) <= line_count, (
                f"glossary entry {term_key!r} cites {src!r} but file has only {line_count} lines"
            )


def test_diligence_bar_in_acquisition_glossary() -> None:
    """The user explicitly asked what 'the diligence bar' is — that term must ship."""
    g = glossary_for("acquisition_diligence")
    assert any(e.term == "diligence bar" for e in g)


def test_diligence_bar_definition_discloses_internal_rubric() -> None:
    """The definition must not imply industry-standard authority."""
    g = glossary_for("acquisition_diligence")
    bar = next(e for e in g if e.term == "diligence bar")
    assert "internal rubric" in bar.long_def
    assert "industry-standard" in bar.long_def or "not as industry" in bar.long_def


def test_glossary_includes_the_full_multiplier_chain() -> None:
    g = glossary_for("acquisition_diligence")
    terms = {e.term for e in g}
    # The reader must be able to look up every input that drives a deduction.
    for required in ("severity weight", "confidence multiplier", "maturity factor"):
        assert required in terms, f"missing glossary term: {required}"


def test_no_editorial_holdback_or_tranche_terms_in_glossary() -> None:
    """The 0.11.0 cut deliberately excludes economic terms that rest on speculation."""
    for use_case in ["acquisition_diligence", "vc_diligence", "engineering_triage", "remediation_agent"]:
        g = glossary_for(use_case)
        terms = {e.term for e in g}
        for forbidden in ("holdback", "tranche", "escrow", "valuation discount"):
            assert forbidden not in terms, (
                f"glossary for {use_case} contains editorial term {forbidden!r} — "
                "drop until 0.14.0 corpus exists"
            )
