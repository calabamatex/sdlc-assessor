"""Citation registry for in-prose footnote markers (0.11.0 depth pass).

Builders call ``registry.cite(claim_id, text, evidence_refs, source_files)``
to emit a stable footnote number for any prose claim that references a
threshold, multiplier, or evidence line. The registry guarantees:

- Monotonic numbering — the first cite gets ``[1]``, regardless of
  rendering order.
- Deterministic emission — citations are returned in insertion order so
  the rendered footnote list matches the inline marker numbering.
- De-duplication — citing the same ``claim_id`` twice returns the same
  marker number (so the exec summary and methodology can both reference
  "the score below the bar" claim without producing two footnotes).
"""

from __future__ import annotations

from dataclasses import dataclass

from sdlc_assessor.renderer.deliverables.base import Citation


@dataclass(slots=True)
class _MarkedCitation:
    """A :class:`Citation` augmented with its assigned footnote number."""

    marker: int
    citation: Citation


class CitationRegistry:
    """Hand out monotonic footnote numbers; emit citations in order.

    Builders interact via :meth:`cite` for new claims and
    :meth:`marker_for` for repeat references. The renderer calls
    :meth:`as_list` once at the end to materialize the footnote block.
    """

    def __init__(self) -> None:
        self._by_claim: dict[str, _MarkedCitation] = {}
        self._next_marker: int = 1

    def cite(
        self,
        claim_id: str,
        text: str,
        *,
        evidence_refs: list[str] | None = None,
        source_files: list[tuple[str, int | None]] | None = None,
    ) -> int:
        """Register a claim → evidence pointer; return its footnote number.

        Idempotent on ``claim_id``: re-citing the same id returns the
        same marker without duplicating the footnote. The first call
        wins for ``text`` / ``evidence_refs`` / ``source_files`` so
        builders can treat ``cite()`` as both a "register" and "lookup"
        primitive without worrying about ordering.
        """
        existing = self._by_claim.get(claim_id)
        if existing is not None:
            return existing.marker

        marker = self._next_marker
        self._next_marker += 1
        citation = Citation(
            claim_id=claim_id,
            text=text,
            evidence_refs=list(evidence_refs or []),
            source_files=list(source_files or []),
        )
        self._by_claim[claim_id] = _MarkedCitation(marker=marker, citation=citation)
        return marker

    def marker_for(self, claim_id: str) -> int | None:
        """Look up the marker number for an already-registered claim."""
        existing = self._by_claim.get(claim_id)
        return None if existing is None else existing.marker

    def as_list(self) -> list[Citation]:
        """Return all citations in insertion order (== marker order)."""
        return [m.citation for m in sorted(self._by_claim.values(), key=lambda x: x.marker)]

    def __len__(self) -> int:
        return len(self._by_claim)


def render_marker(marker: int) -> str:
    """Format a marker as a superscript-friendly bracketed label.

    Renderers wrap this in ``<sup class="cite">``; markdown / plain-text
    renderers can use the bare string.
    """
    return f"[{marker}]"


__all__ = ["CitationRegistry", "render_marker"]
