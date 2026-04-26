"""C# detector pack (SDLC-057)."""

from __future__ import annotations

from pathlib import Path

from sdlc_assessor.detectors.treesitter.framework import run_treesitter_pack
from sdlc_assessor.detectors.treesitter.rules.csharp_rules import (
    CSHARP_RULES,
    CSHARP_SUFFIXES,
)


def run_csharp_detectors(repo_path: Path) -> list[dict]:
    return run_treesitter_pack(
        repo_path,
        language="csharp",
        suffixes=CSHARP_SUFFIXES,
        rules=CSHARP_RULES,
        detector_source="csharp_pack",
    )


__all__ = ["run_csharp_detectors"]
