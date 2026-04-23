# SDLC Framework v2 Package

This package contains a modular redesign of the original SDLC repository assessment harness.

## Files

- `SDLC_Framework_v2_Spec.md`  
  Master architecture specification.

- `evidence_schema.json`  
  Canonical internal schema for repository evidence, findings, scoring, and blockers.

- `profiles/use_case_profiles.json`  
  Use-case overlays for engineering triage, VC diligence, acquisition diligence, and remediation-agent workflows.

- `profiles/maturity_profiles.json`  
  Maturity overlays for production, prototype, and research repositories.

- `profiles/repo_type_profiles.json`  
  Repository archetype overlays for service, library, CLI, monorepo, research repo, SDK, infrastructure, and internal tool.

- `scoring_engine_spec.md`  
  Scoring and verdict logic, including applicability and blocker behavior.

- `renderer_template.md`  
  Human-readable-first report template.

- `remediation_planner_spec.md`  
  Patch-safe remediation planner specification.

- `detector_pack_starter_spec.md`  
  Starter design for language-specific detector packs.

## Suggested implementation order

1. Lock the evidence schema.
2. Implement classifier and inventory collector.
3. Implement scorer against schema.
4. Implement Markdown renderer.
5. Add profile overlays.
6. Add remediation planner.
7. Add language detector packs.
8. Add comparison mode and HTML renderer.
9. Calibrate against benchmark repositories.
