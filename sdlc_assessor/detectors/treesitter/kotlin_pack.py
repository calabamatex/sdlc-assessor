"""Kotlin detector pack (SDLC-058)."""

from __future__ import annotations

from pathlib import Path

from sdlc_assessor.detectors.treesitter.framework import run_treesitter_pack
from sdlc_assessor.detectors.treesitter.rules.kotlin_rules import (
    KOTLIN_RULES,
    KOTLIN_SUFFIXES,
)


def run_kotlin_detectors(repo_path: Path) -> list[dict]:
    return run_treesitter_pack(
        repo_path,
        language="kotlin",
        suffixes=KOTLIN_SUFFIXES,
        rules=KOTLIN_RULES,
        detector_source="kotlin_pack",
    )


__all__ = ["run_kotlin_detectors"]
