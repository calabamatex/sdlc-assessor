"""Glue between the depth-pass modules and the persona builders.

Each persona builder (``acquisition.py`` / ``vc.py`` / ``engineering.py``
/ ``remediation.py``) calls :func:`apply_depth_pass` once after
constructing its base :class:`Deliverable`. The function attaches the
:class:`ScoreDecomposition`, :class:`GapAnalysis`, :class:`MethodologyNote`,
glossary slice, citation list, and the executive-summary paragraphs.

Builders stay terse; the depth pass stays consistent across personas.
"""

from __future__ import annotations

from sdlc_assessor.renderer.deliverables._citations import CitationRegistry
from sdlc_assessor.renderer.deliverables._decomposition import build_score_decomposition
from sdlc_assessor.renderer.deliverables._exec_summary import build_executive_summary
from sdlc_assessor.renderer.deliverables._gap import build_gap_analysis
from sdlc_assessor.renderer.deliverables._methodology import (
    glossary_for,
    methodology_for,
)
from sdlc_assessor.renderer.deliverables.base import Deliverable


def apply_depth_pass(
    deliverable: Deliverable,
    *,
    scored: dict,
    use_case_profile: dict,
) -> Deliverable:
    """Attach the 0.11.0 depth-pass fields to ``deliverable`` in place.

    Returns the same Deliverable for chaining. Idempotent — re-running
    rebuilds the depth-pass fields from ``scored`` + the profile and
    overwrites whatever was attached previously.
    """
    use_case = deliverable.use_case
    citations = CitationRegistry()

    decomposition = build_score_decomposition(scored, use_case_profile)
    gap = build_gap_analysis(scored, decomposition)
    methodology = methodology_for(scored, use_case)
    glossary = glossary_for(use_case)

    executive_summary = build_executive_summary(
        use_case=use_case,
        scored=scored,
        decomposition=decomposition,
        gap=gap,
        verdict=deliverable.cover.recommendation,
        citations=citations,
    )

    deliverable.score_decomposition = decomposition
    deliverable.gap = gap
    deliverable.methodology = methodology
    deliverable.glossary = list(glossary)
    deliverable.executive_summary = executive_summary
    deliverable.citations = citations.as_list()

    return deliverable


__all__ = ["apply_depth_pass"]
