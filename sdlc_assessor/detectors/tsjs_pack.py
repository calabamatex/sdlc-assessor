"""TypeScript/JavaScript-specific detectors for Phase 3."""

from __future__ import annotations

import json
from pathlib import Path


TSJS_GLOBS = ["*.ts", "*.tsx", "*.js", "*.jsx"]


def _iter_tsjs(repo_path: Path):
    for pattern in TSJS_GLOBS:
        for p in repo_path.rglob(pattern):
            yield p


def run_tsjs_detectors(repo_path: Path) -> list[dict]:
    findings: list[dict] = []

    tsjs_files = list(_iter_tsjs(repo_path))
    if not tsjs_files:
        return findings

    for p in tsjs_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        checks = [
            ("as any", "as_any", "medium", "`as any` detected."),
            ("console.", "console_usage", "low", "console.* usage detected."),
            ("catch {}", "empty_catch", "medium", "Empty catch block detected."),
            ("JSON.parse(", "json_parse", "medium", "JSON.parse usage detected."),
            ("exec(", "exec_usage", "high", "exec usage detected."),
            ("execSync(", "exec_sync_usage", "high", "execSync usage detected."),
        ]
        for pattern, subcat, severity, statement in checks:
            if pattern in text:
                findings.append(
                    {
                        "category": "code_quality_contracts",
                        "subcategory": subcat,
                        "severity": severity,
                        "statement": statement,
                        "evidence": [{"path": str(p)}],
                        "confidence": "medium",
                        "applicability": "applicable",
                        "score_impact": {"magnitude_modifier": 0.8},
                        "detector_source": "tsjs_pack",
                    }
                )

    tsconfig = repo_path / "tsconfig.json"
    if tsconfig.exists():
        strict_enabled = False
        try:
            cfg = json.loads(tsconfig.read_text(encoding="utf-8", errors="ignore"))
            strict_enabled = bool(cfg.get("compilerOptions", {}).get("strict", False))
        except json.JSONDecodeError:
            strict_enabled = False
        if not strict_enabled:
            findings.append(
                {
                    "category": "code_quality_contracts",
                    "subcategory": "missing_strict_mode",
                    "severity": "medium",
                    "statement": "TypeScript strict mode not enabled.",
                    "evidence": [{"path": str(tsconfig)}],
                    "confidence": "high",
                    "applicability": "applicable",
                    "score_impact": {"magnitude_modifier": 0.9},
                    "detector_source": "tsjs_pack",
                }
            )

    return findings
