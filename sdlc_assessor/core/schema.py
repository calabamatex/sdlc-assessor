"""Schema loading and lightweight evidence validation for phase 0."""

from __future__ import annotations

from pathlib import Path

from sdlc_assessor.core.io import read_json

REQUIRED_TOP_LEVEL_KEYS = {
    "repo_meta",
    "classification",
    "inventory",
    "findings",
    "scoring",
    "hard_blockers",
}


def _default_schema_path() -> Path:
    repo_docs = Path(__file__).resolve().parents[2] / "docs" / "evidence_schema.json"
    if repo_docs.exists():
        return repo_docs
    return Path(__file__).resolve().parent / "evidence_schema.json"


def load_evidence_schema(schema_path: str | Path | None = None) -> dict:
    if schema_path is None:
        path: Path = _default_schema_path()
    else:
        path = Path(schema_path)
        if not path.is_absolute() and not path.exists():
            candidate = Path(__file__).resolve().parents[2] / path
            if candidate.exists():
                path = candidate
    return read_json(path)


def validate_evidence_top_level(evidence: dict) -> None:
    missing = REQUIRED_TOP_LEVEL_KEYS - set(evidence.keys())
    if missing:
        raise ValueError(f"Missing required evidence keys: {sorted(missing)}")
