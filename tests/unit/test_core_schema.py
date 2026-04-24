import os

from sdlc_assessor.core.schema import load_evidence_schema, validate_evidence_top_level


def test_core_can_load_docs_schema() -> None:
    schema = load_evidence_schema()
    assert schema["title"] == "SDLC Framework v2 Evidence Schema"


def test_core_can_load_schema_from_relative_docs_path_outside_cwd(tmp_path) -> None:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        schema = load_evidence_schema("docs/evidence_schema.json")
        assert schema["title"] == "SDLC Framework v2 Evidence Schema"
    finally:
        os.chdir(original)


def test_core_can_load_schema_from_default_when_cwd_is_elsewhere(tmp_path) -> None:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        schema = load_evidence_schema()
        assert schema["title"] == "SDLC Framework v2 Evidence Schema"
    finally:
        os.chdir(original)


def test_core_validate_evidence_top_level_passes() -> None:
    evidence = {
        "repo_meta": {},
        "classification": {},
        "inventory": {},
        "findings": [],
        "scoring": {},
        "hard_blockers": [],
    }
    validate_evidence_top_level(evidence)


def test_core_validate_evidence_top_level_fails_on_missing() -> None:
    evidence = {
        "repo_meta": {},
        "classification": {},
    }
    try:
        validate_evidence_top_level(evidence)
    except ValueError as exc:
        assert "Missing required evidence keys" in str(exc)
    else:
        raise AssertionError("Expected validation failure")
