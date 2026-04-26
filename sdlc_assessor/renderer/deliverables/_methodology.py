"""Methodology box + glossary registry (0.11.0 depth pass).

Every entry here is **grounded** — it cites a source path in this
repository where the term is actually defined. No editorial
definitions. No "industry standard" handwaves.

Rule: if I can't cite a file:line where the rule is implemented, the
entry doesn't ship in 0.11.0. Things that would require a real
calibration corpus or peer-reviewed methodology (e.g. *what does a
pass_threshold of 74 mean against historical M&A outcomes*) are out
of scope here; they ship in 0.14.0+.
"""

from __future__ import annotations

from sdlc_assessor.renderer.deliverables.base import (
    GlossaryEntry,
    MethodologyNote,
)


# ---------------------------------------------------------------------------
# Methodology
# ---------------------------------------------------------------------------


_SCORE_FORMULA = (
    "overall = clamp(0, 100, Σ category.earned − Σ flat_penalties)\n"
    "category.earned = clamp(0, normalized_max, normalized_max − Σ deductions)\n"
    "deduction[finding] = SEVERITY_WEIGHTS[sev]\n"
    "                    × CONFIDENCE_MULTIPLIERS[conf]\n"
    "                    × maturity_severity_multiplier\n"
    "                    × (magnitude / 10)\n"
    "normalized_max[cat] = 100 × (BASE_WEIGHTS[cat] × multiplier[cat])\n"
    "                    / Σ_applicable (BASE_WEIGHTS[c] × multiplier[c])"
)


def _verdict_rule_table() -> list[dict]:
    """Mirrors the verdict ladder in scorer.engine.score_evidence.

    Source: sdlc_assessor/scorer/engine.py:244-251.
    """
    return [
        {
            "condition": "score ≥ distinction_threshold AND no blockers (any severity)",
            "verdict": "pass_with_distinction",
            "source": "scorer/engine.py:244",
        },
        {
            "condition": "score ≥ pass_threshold AND no critical blockers",
            "verdict": "pass",
            "source": "scorer/engine.py:246",
        },
        {
            "condition": "(score ≥ pass_threshold AND has critical) OR (score < pass_threshold AND has any blocker)",
            "verdict": "conditional_pass",
            "source": "scorer/engine.py:248",
        },
        {
            "condition": "otherwise",
            "verdict": "fail",
            "source": "scorer/engine.py:250",
        },
    ]


def _calibration_band_for(scored: dict) -> str | None:
    """Match the asset's (maturity, archetype) against docs/calibration_targets.md.

    The targets file is the only calibration anchor in the repo. Be
    explicit when no band is registered for the combination — we do
    not invent one.
    """
    cls = scored.get("classification") or {}
    maturity = cls.get("maturity_profile", "unknown")
    archetype = cls.get("repo_archetype", "unknown")

    # The fixture-derived bands in docs/calibration_targets.md cover a
    # narrow set; we don't pretend coverage we don't have.
    return (
        f"calibration_band: archetype={archetype}, maturity={maturity}; "
        "see docs/calibration_targets.md. The targets file calibrates against "
        "internal fixture corpus (n≈26), not real-world outcomes — treat as "
        "an internal rubric, not a population statistic."
    )


def methodology_for(scored: dict, use_case: str) -> MethodologyNote:
    """Construct the methodology box for the given persona.

    The box names the formula, the threshold (via the persona's
    use-case profile), the multiplier composition, and the verdict
    rule. Every claim cites a source path.
    """
    return MethodologyNote(
        score_formula=_SCORE_FORMULA,
        threshold_explanation=(
            f"The pass and distinction thresholds are persona-specific, "
            f"defined in sdlc_assessor/profiles/data/use_case_profiles.json under "
            f"'{use_case}'. The threshold values are an internal rubric calibrated "
            f"against the fixture corpus in tests/fixtures/. They are NOT calibrated "
            f"against real-world M&A / VC / engineering outcomes; that calibration "
            f"corpus is scheduled for 0.14.0."
        ),
        multiplier_explanation=(
            "Three multipliers compose for each finding's deduction: "
            "(1) SEVERITY_WEIGHTS in scorer/engine.py:24 — info=0, low=2, medium=5, high=10, critical=20; "
            "(2) CONFIDENCE_MULTIPLIERS in scorer/engine.py:26 — high=1.0, medium=0.9, low=0.7; "
            "(3) maturity severity_multiplier from profiles/data/maturity_profiles.json — "
            "production=1.2, prototype=0.95, research=0.9. The persona's "
            "category_multipliers (from use_case_profiles.json) further weight each "
            "category's normalized contribution."
        ),
        verdict_rule_table=_verdict_rule_table(),
        calibration_band=_calibration_band_for(scored),
    )


# ---------------------------------------------------------------------------
# Glossary registry
#
# Each entry sources a code path where the term is actually defined.
# When a definition rests on speculation rather than code, the entry
# does not ship.
# ---------------------------------------------------------------------------

_GLOSSARY_REGISTRY: dict[str, GlossaryEntry] = {
    "diligence_bar": GlossaryEntry(
        term="diligence bar",
        short_def="Persona-specific pass threshold below which the recommendation defaults to defer or decline.",
        long_def=(
            "Each persona profile sets its own pass_threshold. Acquisition diligence "
            "uses 74; VC diligence uses 72; engineering triage and remediation agent "
            "use 70. These values are an internal rubric calibrated against the "
            "fixture corpus, not against real-world outcomes — treat them as "
            "defensible thresholds within this tool, not as industry-standard bars."
        ),
        sources=[
            "sdlc_assessor/profiles/data/use_case_profiles.json",
            "docs/calibration_targets.md",
        ],
    ),
    "pass_threshold": GlossaryEntry(
        term="pass threshold",
        short_def="The score at or above which a persona's verdict is 'pass' (provided no critical blockers).",
        long_def=(
            "Defined per use_case in profiles/data/use_case_profiles.json. The "
            "scorer compares overall_score against pass_threshold and "
            "distinction_threshold to assign one of four verdicts. See "
            "verdict-rule table in the methodology section."
        ),
        sources=[
            "sdlc_assessor/profiles/data/use_case_profiles.json",
            "sdlc_assessor/scorer/engine.py:237",
        ],
    ),
    "distinction_threshold": GlossaryEntry(
        term="distinction threshold",
        short_def="The score at or above which the verdict is 'pass_with_distinction', provided zero blockers.",
        long_def=(
            "The strictest verdict band. Requires both a high score and no hard "
            "blockers of any severity (not just no critical ones). This is the "
            "'no notes' tier — anything less and the verdict drops to plain pass."
        ),
        sources=[
            "sdlc_assessor/profiles/data/use_case_profiles.json",
            "sdlc_assessor/scorer/engine.py:238",
        ],
    ),
    "severity_weight": GlossaryEntry(
        term="severity weight",
        short_def="The point cost a finding contributes to deduction before confidence and maturity multipliers.",
        long_def=(
            "Defined in scorer/engine.py: info=0, low=2, medium=5, high=10, "
            "critical=20. Each finding's deduction is severity_weight × "
            "confidence_multiplier × maturity_factor × (magnitude / 10). The "
            "scale was raised from {1, 2, 4, 6} in the SDLC-026 calibration."
        ),
        sources=["sdlc_assessor/scorer/engine.py:24"],
    ),
    "confidence_multiplier": GlossaryEntry(
        term="confidence multiplier",
        short_def="Damping factor applied to a finding's deduction based on detector confidence.",
        long_def=(
            "high=1.0, medium=0.9, low=0.7. Defined in scorer/engine.py:26. "
            "Detectors emit confidence labels per finding (high when the "
            "detector is sure, low when the signal is heuristic / proxied). "
            "The damping reduces the deduction for low-confidence findings so "
            "noisy detectors don't dominate the score."
        ),
        sources=["sdlc_assessor/scorer/engine.py:26"],
    ),
    "maturity_factor": GlossaryEntry(
        term="maturity factor",
        short_def="Severity multiplier set per maturity profile.",
        long_def=(
            "production=1.2 (issues are 20% more costly than baseline), "
            "prototype=0.95, research=0.9. Same finding scored against a "
            "production codebase deducts more than against a prototype. "
            "Defined in profiles/data/maturity_profiles.json."
        ),
        sources=["sdlc_assessor/profiles/data/maturity_profiles.json"],
    ),
    "production_flat_penalty": GlossaryEntry(
        term="production flat penalty",
        short_def="Score deduction triggered by category-independent missing essentials in production-maturity repos.",
        long_def=(
            "Three penalties fire only when maturity is 'production' AND the "
            "corresponding finding/condition is present: missing_ci=10, "
            "missing_readme=8, missing_tests=15 (when inventory.test_files=0). "
            "Applied as a final overall-score adjustment after per-category "
            "scoring, so the deduction is visible alongside category scores "
            "rather than re-bucketed into one category."
        ),
        sources=["sdlc_assessor/scorer/engine.py:30"],
    ),
    "score_confidence": GlossaryEntry(
        term="score confidence",
        short_def="How much weight to put on the score itself, computed from classifier confidence + finding density.",
        long_def=(
            "high if classification_confidence ≥ 0.7 AND proxy_ratio ≤ 0.3 AND "
            "evidence_density ≥ 0.1; low if classification_confidence ≤ 0.3 OR "
            "proxy_ratio ≥ 0.7; medium otherwise. proxy_ratio is the fraction "
            "of findings with confidence='medium'; evidence_density is "
            "findings / source_files. Defined in "
            "scorer/engine.py:_compute_score_confidence."
        ),
        sources=["sdlc_assessor/scorer/engine.py:295"],
    ),
    "expected_score_delta": GlossaryEntry(
        term="expected score delta",
        short_def="A remediation task's projected point gain when closed, computed by the planner.",
        long_def=(
            "Computed in remediation/planner.py from the finding's severity, "
            "confidence, maturity, and magnitude. This is a *projection* by "
            "the scoring engine, not a measurement against historical "
            "outcomes — the actual score change after closure may differ."
        ),
        sources=["sdlc_assessor/remediation/planner.py"],
    ),
    "applicability": GlossaryEntry(
        term="applicability",
        short_def="Whether a category counts toward the score for this archetype + maturity.",
        long_def=(
            "Categories can be marked 'applicable' or 'not_applicable' per "
            "(archetype, maturity) combination. Not-applicable categories "
            "are excluded from the weighted_max denominator so they don't "
            "drag down the score for archetypes where the category is "
            "irrelevant (e.g. reproducibility for a service archetype)."
        ),
        sources=[
            "sdlc_assessor/profiles/data/maturity_profiles.json",
            "sdlc_assessor/profiles/data/repo_type_profiles.json",
            "sdlc_assessor/scorer/engine.py:37",
        ],
    ),
    "hard_blocker": GlossaryEntry(
        term="hard blocker",
        short_def="A finding-class that gates the verdict regardless of score.",
        long_def=(
            "Detected by scorer/blockers.py — covers committed credentials, "
            "missing CI under production maturity, unsafe shell exec on a "
            "networked service, etc. Severity is 'critical' or 'high'. "
            "Critical blockers force the verdict below 'pass' even when the "
            "numeric score clears the threshold."
        ),
        sources=["sdlc_assessor/scorer/blockers.py"],
    ),
}


# ---------------------------------------------------------------------------
# Per-persona glossary selection
# ---------------------------------------------------------------------------


_PERSONA_GLOSSARY_KEYS: dict[str, list[str]] = {
    "acquisition_diligence": [
        "diligence_bar",
        "pass_threshold",
        "distinction_threshold",
        "severity_weight",
        "confidence_multiplier",
        "maturity_factor",
        "production_flat_penalty",
        "score_confidence",
        "applicability",
        "hard_blocker",
    ],
    "vc_diligence": [
        "diligence_bar",
        "pass_threshold",
        "distinction_threshold",
        "severity_weight",
        "confidence_multiplier",
        "score_confidence",
        "hard_blocker",
    ],
    "engineering_triage": [
        "pass_threshold",
        "distinction_threshold",
        "severity_weight",
        "confidence_multiplier",
        "maturity_factor",
        "production_flat_penalty",
        "score_confidence",
        "applicability",
        "expected_score_delta",
        "hard_blocker",
    ],
    "remediation_agent": [
        "pass_threshold",
        "severity_weight",
        "confidence_multiplier",
        "maturity_factor",
        "expected_score_delta",
        "hard_blocker",
    ],
}


def glossary_for(use_case: str) -> list[GlossaryEntry]:
    """Return the glossary slice this persona's report should ship with."""
    keys = _PERSONA_GLOSSARY_KEYS.get(use_case) or list(_GLOSSARY_REGISTRY.keys())
    return [_GLOSSARY_REGISTRY[k] for k in keys if k in _GLOSSARY_REGISTRY]


def all_glossary_terms() -> list[str]:
    """All glossary keys; used by tests."""
    return list(_GLOSSARY_REGISTRY.keys())


__all__ = ["all_glossary_terms", "glossary_for", "methodology_for"]
