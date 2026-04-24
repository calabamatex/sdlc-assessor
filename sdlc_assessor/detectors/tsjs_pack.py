"""TypeScript/JavaScript-specific detectors."""

from __future__ import annotations

import json
import re
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
            (r"as\s+any", "as_any", "medium", "`as any` detected."),
            (r"console\.[a-zA-Z_]+\(", "console_usage", "low", "console.* usage detected."),
            (r"catch\s*\(?.*?\)?\s*\{\s*\}", "empty_catch", "medium", "Empty catch block detected."),
            (r"JSON\.parse\(", "json_parse", "medium", "JSON.parse usage detected."),
            (r"\bexec\(", "exec_usage", "high", "exec usage detected."),
            (r"\bexecSync\(", "exec_sync_usage", "high", "execSync usage detected."),
        ]

        for pattern, subcat, severity, statement in checks:
            if re.search(pattern, text):
                findings.append(
                    {
                        "category": "code_quality_contracts",
                        "subcategory": subcat,
                        "severity": severity,
                        "statement": statement,
                        "evidence": [{"path": str(p)}],
                        "confidence": "medium",
                        "applicability": "applicable",
                        "score_impact": {"direction": "negative", "magnitude": 3},
                        "detector_source": "tsjs_pack",
                    }
                )

    tsconfig = repo_path / "tsconfig.json"
    strict_enabled = False
    if tsconfig.exists():
        try:
            cfg = json.loads(tsconfig.read_text(encoding="utf-8", errors="ignore"))
            strict_enabled = bool(cfg.get("compilerOptions", {}).get("strict", False))
        except Exception:
            strict_enabled = False

    if not strict_enabled:
        findings.append(
            {
                "category": "code_quality_contracts",
                "subcategory": "missing_strict_mode",
                "severity": "medium",
                "statement": "TypeScript strict mode not enabled.",
                "evidence": [{"path": str(tsconfig if tsconfig.exists() else Path('tsconfig.json'))}],
                "confidence": "high",
                "applicability": "applicable",
                "score_impact": {"direction": "negative", "magnitude": 3},
                "detector_source": "tsjs_pack",
            }
        )

    return findings
