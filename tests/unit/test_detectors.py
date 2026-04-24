from pathlib import Path

from sdlc_assessor.detectors.registry import DetectorRegistry
from sdlc_assessor.detectors.tsjs_pack import run_tsjs_detectors


def test_detectors_registry_lists_phase3_detectors() -> None:
    registry = DetectorRegistry()
    assert registry.registered() == ["common", "python_pack", "tsjs_pack"]


def test_detectors_find_probable_secret_fixture_signal() -> None:
    registry = DetectorRegistry()
    findings = registry.run("tests/fixtures/fixture_probable_secret")
    subcats = {f["subcategory"] for f in findings}
    assert "probable_secrets" in subcats


def test_detectors_emit_finding_shape_fields() -> None:
    registry = DetectorRegistry()
    findings = registry.run("tests/fixtures/fixture_probable_secret")
    required = {
        "category",
        "subcategory",
        "severity",
        "statement",
        "evidence",
        "confidence",
        "applicability",
        "score_impact",
        "detector_source",
    }
    assert findings
    assert required.issubset(findings[0].keys())


def test_tsjs_detector_noop_when_no_tsjs_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    assert run_tsjs_detectors(tmp_path) == []


def test_tsjs_detector_handles_invalid_tsconfig_json(tmp_path: Path) -> None:
    (tmp_path / "index.ts").write_text("const x = 1;", encoding="utf-8")
    (tmp_path / "tsconfig.json").write_text("{invalid", encoding="utf-8")
    subcats = {f["subcategory"] for f in run_tsjs_detectors(tmp_path)}
    assert "missing_strict_mode" in subcats


def test_tsjs_detector_parses_strict_with_nonstandard_whitespace(tmp_path: Path) -> None:
    (tmp_path / "index.ts").write_text("const x = 1;", encoding="utf-8")
    (tmp_path / "tsconfig.json").write_text(
        '{"compilerOptions":{"strict":true}}', encoding="utf-8"
    )
    subcats = {f["subcategory"] for f in run_tsjs_detectors(tmp_path)}
    assert "missing_strict_mode" not in subcats
