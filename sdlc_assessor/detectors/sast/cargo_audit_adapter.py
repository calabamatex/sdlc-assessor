"""cargo-audit SAST adapter (SDLC-059).

Wraps ``cargo audit --json`` to surface RustSec advisories against the
``Cargo.lock`` in the assessed repo. Each advisory becomes a finding under
``dependency_release_hygiene`` (or ``security_posture`` for high-severity
CVEs) tagged with the advisory ID.

The adapter has stricter-than-default ``should_run`` semantics: we only
invoke the binary when a ``Cargo.lock`` exists, since cargo-audit refuses
to run without one.
"""

from __future__ import annotations

import json
from pathlib import Path

from sdlc_assessor.detectors.sast.framework import (
    SASTAdapter,
    SASTResult,
    register_adapter,
)

# RustSec advisory severity (informational, low, medium, high, critical) →
# our schema. cargo-audit emits CVSS-derived severity strings.
_CVSS_SEVERITY = {
    "informational": "info",
    "low": "low",
    "medium": "medium",
    "high": "high",
    "critical": "critical",
}


class CargoAuditAdapter(SASTAdapter):
    tool_name = "cargo-audit"
    ecosystems = ("rust",)
    detector_source = "sast.cargo_audit"
    timeout_seconds = 90

    def should_run(self, repo_path: Path) -> bool:
        # cargo-audit needs a Cargo.lock; without one it errors rather than
        # returning empty.
        return (repo_path / "Cargo.lock").exists() and super().should_run(repo_path)

    def build_command(self, repo_path: Path) -> list[str]:
        return [
            self.tool_name,
            "audit",
            "--json",
            "--quiet",
            "--file",
            str(repo_path / "Cargo.lock"),
        ]

    def parse_output(self, stdout: str, stderr: str, returncode: int) -> list[SASTResult]:
        if not stdout.strip():
            return []
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return []
        out: list[SASTResult] = []

        # cargo-audit's JSON shape: {vulnerabilities: {list: [...]}, ...}
        vulnerabilities = (data.get("vulnerabilities") or {}).get("list") or []
        for entry in vulnerabilities:
            advisory = entry.get("advisory") or {}
            package = entry.get("package") or {}
            advisory_id = advisory.get("id") or "RUSTSEC-UNKNOWN"
            cvss_severity_raw = advisory.get("severity") or "medium"
            severity = _CVSS_SEVERITY.get(cvss_severity_raw.lower(), "medium")
            category = "security_posture" if severity in {"high", "critical"} else "dependency_release_hygiene"
            title = advisory.get("title") or "RustSec advisory"
            description = advisory.get("description") or ""
            package_name = package.get("name", "?")
            package_version = package.get("version", "?")
            statement = (
                f"{advisory_id}: {title} "
                f"({package_name} {package_version})"
            )
            rationale = description.strip().splitlines()[0] if description else statement
            cve = advisory.get("aliases", [])
            tags = [f"advisory:{advisory_id}"]
            if isinstance(cve, list):
                for alias in cve:
                    if isinstance(alias, str) and alias.startswith("CVE-"):
                        tags.append(f"cve:{alias}")
            out.append(
                SASTResult(
                    subcategory=f"cargo_audit_{advisory_id.lower().replace('-', '_')}",
                    severity=severity,
                    category=category,
                    statement=statement,
                    path="Cargo.lock",
                    rationale=rationale,
                    confidence="high",
                    rule_id=advisory_id,
                    tags=tags,
                )
            )

        # cargo-audit also reports unmaintained / unsound / yanked crates
        # under top-level keys.
        for warn_kind in ("warnings",):
            warnings_block = data.get(warn_kind) or {}
            if not isinstance(warnings_block, dict):
                continue
            for kind, items in warnings_block.items():
                if not isinstance(items, list):
                    continue
                for entry in items:
                    advisory = entry.get("advisory") or {}
                    package = entry.get("package") or {}
                    advisory_id = advisory.get("id") or f"rust_{kind}"
                    package_name = package.get("name", "?")
                    title = advisory.get("title") or kind.replace("_", " ").title()
                    statement = (
                        f"{advisory_id}: {title} ({package_name})"
                    )
                    out.append(
                        SASTResult(
                            subcategory=f"cargo_audit_warning_{kind}",
                            severity="low",
                            category="dependency_release_hygiene",
                            statement=statement,
                            path="Cargo.lock",
                            rationale=advisory.get("description", statement),
                            confidence="medium",
                            rule_id=advisory_id,
                            tags=[f"warning:{kind}", f"advisory:{advisory_id}"],
                        )
                    )

        return out


register_adapter(CargoAuditAdapter())


__all__ = ["CargoAuditAdapter"]
