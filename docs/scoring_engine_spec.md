# Scoring Engine Specification

## Purpose

The scoring engine consumes normalized evidence and produces:

- category scores
- overall normalized score
- verdict
- score confidence
- hard blockers
- narrative justification

The scoring engine never invents evidence. It only interprets the evidence object.

## Inputs

1. Evidence object conforming to `evidence_schema.json`
2. Use-case profile
3. Maturity profile
4. Repository archetype profile
5. Optional organization-specific policy overrides

## Base weights

| Category | Base Weight |
|---|---:|
| Architecture and design | 15 |
| Code quality and contracts | 15 |
| Testing and quality gates | 15 |
| Security posture | 20 |
| Dependency and release hygiene | 10 |
| Documentation and truthfulness | 10 |
| Maintainability and operability | 10 |
| Reproducibility and research rigor | 5 |

Total base score: 100

## Scoring steps

### Step 1: Resolve applicability
For each category, resolve applicability in this order:

1. maturity profile
2. repo archetype override
3. explicit evidence-driven override if supported by detector output

Result per category:
- applicable
- partially_applicable
- not_applicable

Rules:
- not_applicable categories are removed from denominator
- partially_applicable categories retain weight but may apply softened thresholds

### Step 2: Apply use-case multipliers
Multiply base weights by use-case profile multipliers.

Example:
- base Security posture = 20
- VC diligence multiplier = 1.20
- weighted Security posture = 24

After all multipliers, normalize the applicable category max scores back to 100.

### Step 3: Aggregate findings by category
Each finding contributes positive, negative, or neutral impact.

Each finding must include:
- severity
- confidence
- applicability
- score impact magnitude

Recommended severity baseline:
- info = 0
- low = 1
- medium = 2
- high = 4
- critical = 6

Recommended confidence multiplier:
- high = 1.00
- medium = 0.75
- low = 0.50

Recommended maturity multiplier:
- production = 1.20
- prototype = 0.95
- research = 0.90

Impact formula:
`effective_deduction = severity_weight × confidence_multiplier × maturity_multiplier × score_impact.magnitude_modifier`

Positive findings may recover points, but only if they contain explicit evidence. Absence of failure is not the same as evidence of strength.

### Step 4: Compute raw category score
Start each category at max points. Apply deductions and bounded evidence-based credits.

Rules:
- category score cannot exceed category max
- category score cannot fall below zero
- low-confidence deductions should not dominate category outcome alone
- one severe critical finding can reduce a category sharply but should still be explained narratively

### Step 5: Detect hard blockers
Hard blockers are not simply low scores. They are conditions that materially undermine trust or safety.

Candidate hard blocker rules:
- hardcoded production credential or active secret
- user-controlled command execution without sanitization
- network-facing production repo with no input validation evidence
- release automation able to publish from mutable or unsafe conditions
- fabricated metrics or misleading claims contradicted by repository evidence
- production repo with no tests and no CI

A hard blocker does not force an automatic zero score. It forces explicit blocker surfacing and may force verdict downgrade.

### Step 6: Resolve verdict
Recommended verdict rules:
- Pass with distinction: ≥ threshold and no active hard blockers
- Pass: ≥ threshold and no active critical blocker
- Conditional pass: threshold met but one or more blockers or medium-confidence uncertainty clusters remain
- Fail: below threshold or blocker severity too high

Default thresholds should come from use-case profile.

## Narrative rules

The scoring engine must produce a short justification for each category score:
- 2 to 5 sentences
- cite strongest strengths and most important deductions
- clearly state applicability if reduced or excluded
- avoid generic filler like "overall good quality"

## Anti-gaming rules

1. Feature claims in README do not earn credit unless matched by code or tests.
2. A security control that is opt-in earns less credit than secure-by-default behavior.
3. Test count alone is not enough. The engine should prefer evidence of coverage diversity and CI enforcement when available.
4. A repo with polished docs but weak code should not be over-scored.
5. A prototype should not be punished for lacking production-only infrastructure unless the repo claims production readiness.

## Recommended score confidence logic

### High confidence
Use when:
- strong evidence density
- multiple corroborating signals
- few proxy-only judgments

### Medium confidence
Use when:
- some major findings rely on approximate metrics
- repo classification is clear but coverage of evidence is partial

### Low confidence
Use when:
- limited file access
- unusual repo structure
- major reliance on regex approximations
- ambiguous repo purpose

## Example category summary format

- Category: Security posture
- Applicable: yes
- Score: 11/20
- Summary:
  Boundary validation exists in API entrypoints, but unsafe subprocess execution appears in two user-controlled code paths. CI includes lint and test steps, but no evidence of SAST or secret scanning was found. Because the repo is classified as a production service, the unsafe execution paths materially reduce confidence.

## Output contract

The scoring engine should emit:
- category score objects
- overall score
- verdict
- score confidence
- triggered hard blockers
- short narrative summaries
