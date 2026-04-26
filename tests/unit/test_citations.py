"""Tests for the CitationRegistry (0.11.0 depth pass)."""

from __future__ import annotations

from sdlc_assessor.renderer.deliverables._citations import (
    CitationRegistry,
    render_marker,
)


def test_first_cite_returns_marker_1() -> None:
    reg = CitationRegistry()
    n = reg.cite("score_below_bar", "score 59 vs threshold 74")
    assert n == 1


def test_subsequent_cites_increment_monotonically() -> None:
    reg = CitationRegistry()
    a = reg.cite("a", "first")
    b = reg.cite("b", "second")
    c = reg.cite("c", "third")
    assert (a, b, c) == (1, 2, 3)


def test_repeat_claim_id_returns_same_marker() -> None:
    """Citing the same claim twice yields the same footnote, not a duplicate."""
    reg = CitationRegistry()
    first = reg.cite("threshold", "pass=74", evidence_refs=["use_case_profiles.json:67"])
    second = reg.cite("threshold", "DIFFERENT TEXT")
    assert first == second
    assert len(reg) == 1


def test_marker_for_returns_none_for_unknown_claim() -> None:
    reg = CitationRegistry()
    assert reg.marker_for("never_cited") is None
    reg.cite("a", "x")
    assert reg.marker_for("a") == 1
    assert reg.marker_for("b") is None


def test_as_list_returns_citations_in_insertion_order() -> None:
    reg = CitationRegistry()
    reg.cite("a", "first")
    reg.cite("b", "second")
    reg.cite("c", "third")
    out = reg.as_list()
    assert [c.claim_id for c in out] == ["a", "b", "c"]


def test_first_call_text_and_refs_win() -> None:
    """Builders can use cite() as both register and lookup."""
    reg = CitationRegistry()
    reg.cite("x", "first text", evidence_refs=["ref1"])
    reg.cite("x", "second text", evidence_refs=["ref2"])
    out = reg.as_list()
    assert len(out) == 1
    assert out[0].text == "first text"
    assert out[0].evidence_refs == ["ref1"]


def test_cite_carries_source_files() -> None:
    reg = CitationRegistry()
    reg.cite(
        "threshold",
        "pass=74",
        source_files=[("sdlc_assessor/profiles/data/use_case_profiles.json", 67)],
    )
    out = reg.as_list()
    assert out[0].source_files == [
        ("sdlc_assessor/profiles/data/use_case_profiles.json", 67)
    ]


def test_render_marker_format() -> None:
    assert render_marker(1) == "[1]"
    assert render_marker(42) == "[42]"
