# SDLC Framework v2 Specification

## Purpose

SDLC Framework v2 is a modular repository assessment system designed to evaluate software repositories across multiple use cases without duplicating core logic. It replaces a single overloaded prompt with a composed framework that separates evidence collection, contextual scoring, report rendering, and remediation planning.

The design goals are:

1. Human-readable first output.
2. Evidence-based scoring.
3. Language-agnostic architecture.
4. Modular handling of use case, maturity, and repository archetype.
5. Safe handoff to AI coding assistants for remediation tasks.

## Why v2 exists

The original harness combined five concerns in one artifact:

- repository inspection procedure
- scoring rubric
- output formatting
- comparison workflow
- remediation planning

That design increased prompt collision and made the system harder to calibrate, maintain, and adapt across repository types. v2 decomposes those concerns into stable modules.

## Design principles

### 1. One evidence pipeline
All use cases consume the same normalized evidence object. Evidence collection should not change because the audience changes.

### 2. Contextual scoring
Scoring depends on use case, maturity, and repository archetype. A production service should not be graded like a research prototype. A local CLI should not be punished like a networked service for service-specific controls.

### 3. Language-agnostic schema, language-specific detector packs
All detector packs emit into a common schema. TypeScript, Python, Go, Rust, Java, C#, and other languages can be supported without rewriting the framework.

### 4. Human-readable first, structured internally
The primary output is a human-readable report. The internal representation is structured JSON so the framework remains auditable and composable.

### 5. Hard blockers separated from weighted score
Critical issues should be surfaced as hard blockers instead of being hidden inside a blended score.

## Top-level architecture

```text
assessment_request
  ├── repo_target
  ├── analysis_mode
  │     ├── single_repo
  │     ├── compare
  │     └── remediation_plan
  ├── use_case_profile
  │     ├── engineering_triage
  │     ├── vc_diligence
  │     ├── acquisition_diligence
  │     └── remediation_agent
  ├── maturity_profile
  │     ├── production
  │     ├── prototype
  │     └── research
  ├── repo_archetype
  │     ├── service
  │     ├── library
  │     ├── cli
  │     ├── monorepo
  │     ├── research_repo
  │     ├── sdk
  │     ├── infrastructure
  │     └── internal_tool
  ├── language_packs
  │     ├── common
  │     ├── typescript
  │     ├── python
  │     ├── go
  │     ├── rust
  │     ├── java
  │     └── csharp
  └── output_profile
        ├── human_readable_full
        ├── executive_summary
        ├── comparison_report
        └── remediation_appendix
```

## Core modules

### 1. Classifier
The classifier determines:

- repository archetype
- maturity level
- dominant languages
- deployment surface
- release surface
- network exposure
- packaging model
- confidence of classification

The classifier emits a structured result. The scorer never infers archetype independently.

### 2. Inventory collector
The inventory collector captures quantitative baseline facts:

- file counts
- source lines of code
- test file and test case estimates
- workflow counts
- dependency counts
- commit and release counts
- largest files
- language breakdown

Inventory is descriptive only. It does not score.

### 3. Detector packs
Detector packs search for language-specific and cross-language evidence across:

- type safety and contracts
- error handling
- observability
- input validation
- command execution
- I/O safety
- security posture
- dependency hygiene
- documentation consistency
- release hygiene
- production readiness
- research reproducibility

Each finding must emit:
- statement
- severity
- evidence locations
- confidence
- applicability
- normalized category mapping

### 4. Normalizer
The normalizer transforms raw detector output into the common evidence schema. This is the layer that makes the framework language-agnostic.

### 5. Scorer
The scorer applies:
- base category weights
- use-case profile multipliers
- maturity profile applicability rules
- repository archetype applicability rules
- hard blocker rules
- pass and fail thresholds

### 6. Renderer
The renderer converts scored evidence into a human-readable report. The renderer does not invent evidence or reinterpret findings. It only formats already-scored data.

### 7. Planner
The planner generates a remediation plan from scored findings. It must produce patch-safe instructions using file paths, symbols, anchors, tests, and verification commands.

## Data flow

```text
clone repo
  → classify repo
  → collect inventory
  → run detector packs
  → normalize evidence
  → apply scoring profiles
  → identify hard blockers
  → render report
  → optionally generate comparison view or remediation plan
```

## Analysis modes

### Single repository mode
Produces:
- repo classification
- overall score
- scoring matrix
- strengths
- top risks
- evidence appendix
- optional remediation appendix

### Comparison mode
Produces:
- side-by-side classification
- normalized score matrix
- feature delta
- what repo A can adopt from repo B
- what repo B can adopt from repo A
- relative risk summary

### Remediation mode
Produces:
- sequenced phases
- implementation tasks
- test requirements
- verification commands
- expected score lift
- hard blocker closure mapping

## Scoring philosophy

### The score is a decision aid, not the truth
v2 treats score as a compact summary of evidence. The framework should expose uncertainty when the score is based on proxies or partial evidence.

### Applicability first
Every category is tagged:
- applicable
- partially_applicable
- not_applicable

Not-applicable points are excluded from the denominator.

### Confidence-aware scoring
Each major finding includes confidence:
- high
- medium
- low

Low-confidence findings should not drive large deductions without corroborating evidence.

### Hard blockers
Examples of hard blockers include:
- active hardcoded secrets
- unsafe command execution on user input
- network-exposed code with no input validation
- release automation capable of unsafe publish
- production repo with no tests and no CI
- evidence of fabricated metrics or knowingly misleading claims

Hard blockers are displayed independently from score.

## Recommended base category model

| Category | Base Weight | Purpose |
|---|---:|---|
| Architecture and design | 15 | Cohesion, layering, separation of concerns |
| Code quality and contracts | 15 | Type rigor, validation, error discipline |
| Testing and quality gates | 15 | Test depth, coverage discipline, CI checks |
| Security posture | 20 | Boundary defense, command execution, auth, secrets, unsafe I/O |
| Dependency and release hygiene | 10 | Locking, versioning, release quality |
| Documentation and truthfulness | 10 | Accuracy, consistency, overclaim detection |
| Maintainability and operability | 10 | Logging, graceful behavior, health, maintainability |
| Reproducibility and research rigor | 5 | Reproduction, experiment integrity, artifact clarity |

These are base weights before contextual overlays.

## Profile overlay model

### Use-case profiles change:
- category multipliers
- narrative emphasis
- pass and fail interpretation
- remediation depth
- executive summary style

### Maturity profiles change:
- applicability
- threshold strictness
- required controls
- penalty severity

### Repository archetype profiles change:
- category applicability
- security relevance
- operability relevance
- release expectations
- expected documentation shape

## Report design

Primary report structure:

1. Header
2. Executive summary
3. Repo classification
4. Score and verdict
5. Score breakdown
6. Top strengths
7. Top risks
8. Hard blockers
9. Detailed findings by category
10. Evidence appendix
11. Optional remediation appendix

The report should read clearly for humans without hiding traceability.

## Remediation design rules

The planner must never rely on brittle instructions like exact line numbers alone. It should use:

- exact file paths
- exact symbol names
- search anchors
- before and after snippets
- minimum required tests
- verification commands

The planner may optionally include line numbers as hints, but stable anchors are the canonical mechanism.

## Calibration requirement

The framework must be calibrated against a benchmark set of repositories spanning:

- strong production service
- weak production service
- strong library
- weak library
- strong CLI
- research repo
- monorepo
- intentionally insecure repo
- intentionally misleading repo

Calibration should measure:
- false positives
- false negatives
- scoring drift by language
- scoring drift by repo archetype
- score variance under different use-case profiles

## Minimum viable implementation order

### Phase 1
- evidence schema
- classifier
- inventory collector
- common detector pack
- scorer
- markdown renderer

### Phase 2
- use-case profiles
- maturity profiles
- repo archetype profiles
- remediation planner

### Phase 3
- language-specific detector packs
- comparison mode
- HTML renderer
- benchmark calibration harness

## Guardrails

The framework must avoid:
- grading based on unverifiable claims
- assuming production intent from existence of code alone
- using weak proxies as hard truth without confidence labeling
- rewarding feature presence without corresponding tests when testability is expected
- collapsing critical security issues into a blended score without blocker surfacing

## Success criteria

The framework is successful if it:
- produces consistent reports across analysts
- scores similar repos similarly after normalization
- adapts fairly across repo types
- remains readable to human decision-makers
- can feed AI coding assistants with precise remediation tasks
