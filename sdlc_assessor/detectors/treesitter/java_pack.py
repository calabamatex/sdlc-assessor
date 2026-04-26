"""Java detector pack (SDLC-056) — runs ``JAVA_RULES`` via the tree-sitter framework."""

from __future__ import annotations

from pathlib import Path

from sdlc_assessor.detectors.treesitter.framework import run_treesitter_pack
from sdlc_assessor.detectors.treesitter.rules.java_rules import JAVA_RULES, JAVA_SUFFIXES


def run_java_detectors(repo_path: Path) -> list[dict]:
    return run_treesitter_pack(
        repo_path,
        language="java",
        suffixes=JAVA_SUFFIXES,
        rules=JAVA_RULES,
        detector_source="java_pack",
    )


__all__ = ["run_java_detectors"]
