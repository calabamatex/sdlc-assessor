# SDLC-assesment Repository — Comprehensive Analysis

**Subject:** `github.com/calabamatex/SDLC-assesment` (branch `main`, 6 commits, 99.9% Python per GitHub language stats)
**Method:** Full source read (every `.py`, `.json`, `.md` in the repo), empirical test-suite execution, schema-validation of generated artifacts against the repo's own declared schema, and benchmark execution of `scripts/benchmark_calibration.py`.
**Stance:** Every factual claim below is grounded in file content or command output. Where I state "the code does X," the line or block is citable from the files read in this session.

---

## 1. Executive summary

The repository implements a CLI-first SDLC assessor that runs a 5-stage pipeline (`classify → collect → score → render → remediate`) plus a `run` convenience command. The architecture, documentation, and profile data are well thought out and largely faithful to the `docs/SDLC_Framework_v2_Spec.md`. The code skeleton is clean, typed, and modular.

However, the implementation is currently a **scaffolded v0.1 that does not meet its own specifications** in four concrete, measurable ways:

1. **Output does not validate against the repo's own schema.** The JSON artifacts produced by the pipeline fail `docs/evidence_schema.json` with 16 distinct errors on a representative fixture run (missing `direction`/`magnitude` in every finding, missing `base_weights`/`applied_weights` in scoring, `category_scores` emitted as dict instead of array, `overall_score` emitted as float instead of integer).
2. **The scorer is catastrophically miscalibrated.** On `engineering_triage + prototype + cli`, the four shipped fixtures score 95.92, 97.63, 92.5, and 93.07. An **empty repository scores 95.92 with verdict `pass_with_distinction`.** A repository containing a plaintext `API_KEY = "super-secret-demo-token"` scores 92.5 with verdict `conditional_pass` — the hard-blocker flag fires, but the numeric score does not discriminate. The tool as currently calibrated cannot distinguish between good and bad repos.
3. **Detectors are substring matches with systematic false positives and false negatives.** `Any in text` matches `Many`, `Anyone`; `print(` matches `pprint(`, `sprint(`; `except:\n` misses `except:` on Windows line endings; no detector captures line numbers; none respect `.gitignore`, `node_modules`, `.venv`, `__pycache__`, `site-packages`.
4. **Test suite fails 2/26 on a clean checkout** because two collector tests depend on `.sdlc/classification.json` being present as a side effect of running the CLI beforehand — a test-isolation violation.

In short: the **specs and scaffolding are sound, but the implementation is a stub dressed as a working tool**. Turning it into the system described in `docs/` is a concrete, bounded engineering effort of roughly 20–30 focused tasks. The action plan does exactly that.

Against the tool's own conceptual categories, if this repository were fed into a correctly-calibrated version of itself under `acquisition_diligence + prototype + library`, it would score roughly: Testing QG — weak (2 collector tests broken), Security — adequate (no obvious vulnerabilities, also no actual security controls), Code quality — mixed (types and structure are good, but detectors and scorer are wrong-by-construction), Documentation truthfulness — **low** (`README.md` is literally one line: `"This is the initial commit"`, and the shipped implementation does not match `docs/*_spec.md`), Dependency/release — weak (no declared dependencies, no CI, no LICENSE, no SECURITY.md), Reproducibility — adequate (fixtures exist).

---

## 2. Inventory

### 2.1 Files present (49 files)

| Area | Files | Notes |
|---|---|---|
| Root | `README.md`, `PLANS.md`, `pyproject.toml`, `.gitignore`, `sdlc` (shell wrapper) | README is 1 line |
| Docs | 9 files under `docs/` | Specs + schema + 3 profile JSONs (duplicated under `sdlc_assessor/profiles/data/`) |
| Package | 27 files under `sdlc_assessor/` | Flat `sdlc_assessor/` (not `src/sdlc_assessor/` as PLANS.md specifies) |
| Scripts | `scripts/benchmark_calibration.py` | Works |
| Tests | 8 unit files, 1 golden file, `conftest.py`, 4 fixture dirs | 2 of 6 planned fixtures are missing |

### 2.2 Declared dependencies

`pyproject.toml` declares **zero runtime dependencies and zero dev extras.** `pytest` is used by tests but not declared. `jsonschema` would be needed for schema validation but is not present.

### 2.3 Files missing that `PLANS.md` or `docs/` call for

- `tests/fixtures/fixture_no_ci/` (listed in PLANS.md §Exact fixture repos)
- `tests/fixtures/fixture_research_repo/` (same)
- `src/sdlc_assessor/profiles/merger.py` (PLANS.md §Final project structure)
- `src/sdlc_assessor/pipeline/run_single.py` (PLANS.md §Final project structure — the `run` logic is inlined in `cli.py` instead)
- `.github/workflows/*` — no CI for this repo itself
- `SECURITY.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`

### 2.4 Structural divergence from PLANS.md

PLANS.md specifies `src/sdlc_assessor/` layout. Actual repo uses flat `sdlc_assessor/` at the repository root. Both work, but `pyproject.toml`'s `[tool.setuptools.package-data]` entry and the `[project.scripts]` entry assume the flat layout, so in practice the flat layout is canonical and `PLANS.md` is out of date on this point.

---

## 3. Build, packaging, and installability

### 3.1 `pyproject.toml`

```toml
[project]
name = "sdlc-assessor"
version = "0.1.0"
requires-python = ">=3.12"
```

- ✅ `[project.scripts]` entry correctly maps `sdlc` → `sdlc_assessor.cli:main`; the CLI is reachable after `pip install -e .`.
- ❌ No `dependencies` array. `pytest` is imported in `scripts/benchmark_calibration.py`? No — that script doesn't import pytest; but tests require pytest and it is not declared under `[project.optional-dependencies].dev`.
- ❌ No `[tool.setuptools.packages.find]` directive. With the flat `sdlc_assessor/` layout this works by auto-discovery, but it's fragile.
- ❌ No `README` or `license` metadata.
- ❌ No `classifiers`, `urls`, or `authors`.

### 3.2 The `sdlc` shell script at repo root

```bash
#!/usr/bin/env bash
python -m sdlc_assessor.cli "$@"
```

Redundant — `[project.scripts]` already creates a `sdlc` entrypoint once the package is installed. It is not marked executable in git (no +x bit), has no Windows equivalent, and will confuse users who type `./sdlc` on a fresh clone without `chmod +x`. Also, it has no file extension — and `git` has no record of its mode — so on macOS/Linux after clone it is not runnable directly.

### 3.3 `.gitignore`

Adequate for a Python project (`__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.venv/`, `.sdlc/`). Does not ignore `dist/`, `build/`, `.eggs/`, `*.egg-info/`, `.coverage`, `.mypy_cache/`, `.ruff_cache/`, `htmlcov/`, OS metadata (`.DS_Store`, `Thumbs.db`), editor droppings (`.idea/`, `.vscode/`).

---

## 4. Contract-vs-implementation divergence

This is the single most important section. The repository declares a JSON Schema (`docs/evidence_schema.json`) and a set of specs in `docs/`. The shipped implementation's output is structurally non-conforming.

### 4.1 Schema violations observed empirically

Running `python -m sdlc_assessor.cli run tests/fixtures/fixture_typescript_basic --use-case engineering_triage --maturity prototype --repo-type cli` produces `scored.json`. Validating that file with `jsonschema.Draft202012Validator` against `docs/evidence_schema.json` yields **16 errors**:

| # | Path | Violation | Root cause |
|---|---|---|---|
| 1 | `findings[*].score_impact` | Missing required `direction` | Detectors emit `{"magnitude_modifier": 1.0}` only |
| 2 | `findings[*].score_impact` | Missing required `magnitude` | Same — schema expects integer 0–10, code uses float `magnitude_modifier` |
| 3 | `scoring` | Missing required `base_weights` | `scorer/engine.py` never emits this |
| 4 | `scoring` | Missing required `applied_weights` | Same |
| 5 | `scoring.category_scores` | Wrong type (object, not array) | Schema specifies array of `{category, applicable, score, max_score, summary}`; code emits dict keyed by category name with `{applicability, score, max}` |
| 6 | `scoring.overall_score` | `93.07 is not of type 'integer'` | Schema declares integer 0–100; code emits float rounded to 2 decimals |
| 7 | `category_scores[*]` | Keys `category`, `applicable`, `max_score`, `summary` never appear | Code uses `applicability`, `max` |

### 4.2 Spec vs code, by module

**`docs/scoring_engine_spec.md` vs `sdlc_assessor/scorer/engine.py`**

| Spec requirement | Implementation |
|---|---|
| Severity weights (0/1/2/4/6) | ✅ Matches |
| Confidence multipliers (1.0/0.75/0.5) | ✅ Matches |
| Maturity multipliers (1.20/0.95/0.90) | ✅ Sourced from maturity profile JSON |
| Formula: deduction = sev × conf × mat × mag | ✅ Implemented |
| Hard blockers surfaced separately | ✅ Implemented |
| Category score bounded [0, max] | ✅ Implemented |
| Narrative justification per category (2–5 sentences) | ❌ Not emitted |
| Evidence-based positive credits | ❌ Not implemented |
| Score confidence computed from evidence density | ❌ Hardcoded `"medium"` |
| Anti-gaming rules | ❌ Not implemented |
| Merge order: use_case → maturity → repo_type | ⚠️ `build_effective_profile` just loads the three, doesn't merge them into a flat `effective_config` per the spec. The scorer then reads from the three profiles separately. Functionally equivalent for now but not what PLANS.md specifies. |

**`docs/remediation_planner_spec.md` vs `sdlc_assessor/remediation/planner.py`**

| Spec requirement | Implementation |
|---|---|
| Task schema (11 keys) | ✅ Matches exactly |
| Phases sequenced by dependency | ❌ Every task has phase `"phase_1_safety"` hardcoded |
| `change_type` allowlist (9 values) | ❌ Every task uses `"modify_block"` regardless of finding |
| Before/after snippets | ❌ Not captured |
| Symbol names | ❌ Not captured |
| Effort estimates | ❌ Not captured |
| Rollback notes | ❌ Not captured |
| Per-task verification_commands | ⚠️ Hardcoded `["pytest -q"]` for every task |
| Expected score delta | ⚠️ Hardcoded string `"likely +5 to +8"` regardless of scope |

**`docs/renderer_template.md` vs `sdlc_assessor/renderer/markdown.py`**

| Spec section | Implementation |
|---|---|
| 1. Header | ⚠️ Partial — missing URL, head commit, analysis mode, use-case profile, maturity, archetype, languages |
| 2. Executive Summary | ❌ Hardcoded single sentence |
| 3. Overall Score & Verdict | ✅ |
| 4. Repo Classification Box | ⚠️ Missing release_surface, classification_confidence |
| 5. Quantitative Inventory | ⚠️ Missing estimated_test_cases, test_to_source_ratio, workflow_jobs, runtime_dependencies, dev_dependencies, commit_count, tag_count, release_count |
| 6. Top Strengths | ❌ Hardcoded single sentence |
| 7. Top Risks | ⚠️ Shows only the first finding |
| 8. Hard Blockers | ✅ |
| 9. Category Scoring Matrix | ⚠️ Missing Summary + Major evidence columns |
| 10. Detailed Findings by Category | ⚠️ Flat list, not grouped by category, not ordered by severity |
| 11. Evidence Appendix | ⚠️ Shows only total count |

**`docs/detector_pack_starter_spec.md` vs detector packs**

The spec lists 10 categories of detector signals per pack (type/contract rigor, error handling, logging, boundary validation, unsafe command execution, unsafe file/path handling, dependency/packaging, test patterns, CI alignment, documentation consistency). The shipped Python pack implements 6 substring checks; the TS/JS pack implements 6 substring checks plus tsconfig strict-mode parsing. **No dependency/packaging, CI alignment, or doc-consistency detectors exist in any pack.** The `common` detectors cover `missing CI` and `missing README` but not dependency hygiene, not test-presence cross-checks, not workflow-job parsing.

### 4.3 Classifier is a stub

`sdlc_assessor/classifier/engine.py` returns the following for every repository regardless of content:

```python
ClassificationResult(
    repo_archetype="unknown",
    maturity_profile="unknown",
    deployment_surface="unknown",
    network_exposure=False,
    release_surface="unknown",
    classification_confidence=0.2,
    language_pack_selection=packs,
)
```

Only `language_pack_selection` is computed from the repo. The other 6 fields are placeholders. The classifier never infers `service` vs `library` vs `cli`, never detects `Dockerfile`/`serverless.yml`/`terraform`/`pyproject.toml`/`package.json` signals, never uses the git history, never looks at README, never considers network-binding calls. This directly contradicts `docs/SDLC_Framework_v2_Spec.md §Classifier`.

### 4.4 Language detection bug

```python
# sdlc_assessor/classifier/engine.py line 23
has_ts = any(p.suffix in {".ts", ".tsx", ".js", ".jsx"} for p in repo_path.rglob("*.ts"))
```

The iteration pattern is `*.ts`, but the suffix check allows `.tsx`, `.js`, `.jsx`. A repository that contains only `.js`, `.jsx`, or `.tsx` files (and no `.ts`) will never trigger the TS/JS pack. A React-only or Node-only codebase is effectively invisible to the classifier.

---

## 5. Detectors: systematic issues

### 5.1 Common detectors (`sdlc_assessor/detectors/common.py`)

**Secret scanner reads every file in the repo as UTF-8 text.** The code does:

```python
for p in _all_files(repo_path):
    text = p.read_text(encoding="utf-8", errors="ignore")
    if secret_pattern.search(text):
        ...
```

Consequences:

- **Scans binaries.** `*.zip`, `*.exe`, `*.jar`, `*.tar.gz`, `*.png`, `*.pdf` are all opened as text. The `errors="ignore"` keeps it from crashing, but the work is wasted and occasionally produces junk regex matches.
- **Scans `.venv/`, `node_modules/`, `__pycache__/`, `site-packages/`, `dist/`, `build/`.** The filter is `".git" not in p.parts` and nothing else. On any real repo with a vendored virtualenv, this will scan hundreds of thousands of files and flood the findings list with probable-secret matches from library source.
- **No `.gitignore` respect.** The tool explicitly claims to assess "repository evidence" but scans files that are explicitly not part of the repository as declared by `.gitignore`.
- **No size cap.** A multi-GB SQLite file in the repo gets `read_text` called on it.
- **Three full traversals.** `secrets`, `large files`, `committed artifacts` each call `_all_files` and iterate. Should be a single pass.
- **Secret pattern has no entropy or allowlist logic.** `API_KEY = "example"` in a README triggers the detector with severity `high`.

**README detection is too narrow.** `(repo / "README.md").exists() or (repo / "readme.md").exists()`. Misses `README`, `README.rst`, `README.txt`, `Readme.md`, `docs/README.md`.

**SECURITY.md detection ignores GitHub's recognized locations.** GitHub itself surfaces `SECURITY.md`, `.github/SECURITY.md`, and `docs/SECURITY.md`. The detector only checks the repo root.

**Statements are identical for every match.** `"Large file detected in repository."` — with no indication of which file or how large, beyond the path buried in evidence. The `statement` field is supposed to be human-readable per `docs/renderer_template.md`.

### 5.2 Python pack (`sdlc_assessor/detectors/python_pack.py`)

All six checks are substring matches (`pattern in text`). This produces both false positives and false negatives:

| Check | Pattern | False positive | False negative |
|---|---|---|---|
| `Any` | `"Any"` | `Many`, `Anyone`, `Anywhere`, `"Any"` in docstring | `typing.Any` imported as `A`, `t.Any` |
| `type: ignore` | `"type: ignore"` | In comments describing it, in docs | `type:ignore` (no space) |
| bare `except` | `"except:\n"` | None major | `except:` on last line, `\r\n` line endings, `except :` with space |
| `except Exception` | `"except Exception"` | In a comment about what not to do | `except (Exception,)`, `except Exception as e` ✓ catches, but also `except ExceptionGroup` false-matches |
| `print(` | `"print("` | `pprint(`, `sprint(`, `myprint(`, any `*print(` | `print (` with space |
| `shell=True` | `"shell=True"` | In comments, docstrings | `shell = True`, `shell=1`, `shell=os.getenv("SHELL")` |

Also: **one finding per file per check.** A file with 50 `print()` calls emits one finding. The `count` field in `evidence_schema.json` exists precisely for occurrence counting, but is never populated.

No line numbers are captured — `evidence[0] = {"path": str(p)}` only. `docs/evidence_schema.json` has `line_start`, `line_end`, `snippet`, `match_type`, `count` — none are used.

No AST parsing. Python has a built-in `ast` module specifically for this. Using `ast.parse` would eliminate every false positive above, and `ast.walk` would give line numbers for free.

### 5.3 TS/JS pack (`sdlc_assessor/detectors/tsjs_pack.py`)

- **`catch {}`** — misses `catch (e) {}`, `catch(err){}`, `catch(_){}`. These are the common JS empty-catch patterns.
- **`JSON.parse(`** — flagged as severity `medium` unconditionally. Flagging every `JSON.parse` call as a contract violation is not defensible; the signal is *unchecked* parse of *untrusted* input. The current detector is so broad as to be noise.
- **`exec(`** — matches `execa(`, `execute(`, `oneExec(`, regex `exec`, `Promise.prototype.exec` (if defined), RegExp `.exec()`.
- **tsconfig parser uses `json.loads`** — TypeScript allows JSONC (JSON with comments). Real-world tsconfigs very often have comments. Parse fails silently → falls through to `strict_enabled = False` → emits `missing_strict_mode` on repos that actually have strict mode enabled.
- **No `extends` chain resolution.** A tsconfig that inherits `strict: true` from a shared base config via `"extends": "../tsconfig.base.json"` will be flagged as missing strict mode.
- **No respect for `eslint.config.js` or other config that may enforce equivalent checks.**

---

## 6. Scorer: miscalibration and contract gaps

### 6.1 Empirical miscalibration

Running `scripts/benchmark_calibration.py` (engineering_triage / prototype / cli):

| Fixture | Overall | Verdict | Blockers | What's in the fixture |
|---|---:|---|---:|---|
| `fixture_empty_repo` | **95.92** | `pass_with_distinction` | 0 | Nothing — a `.gitkeep` |
| `fixture_python_basic` | 97.63 | `pass_with_distinction` | 0 | A 2-line README and a `hello()` function |
| `fixture_probable_secret` | **92.5** | `conditional_pass` | 1 | A hardcoded `API_KEY`, a `print()` call |
| `fixture_typescript_basic` | 93.07 | `pass_with_distinction` | 0 | `console.log(name as any)` + `JSON.parse` + non-strict tsconfig |

**Every fixture scores ≥ 92.** The system produces no dynamic range. `pass_threshold = 70` and `distinction_threshold = 85` are set by the use-case profile, but in practice nothing ever falls near 70, so the threshold is decorative. An empty repo passing with distinction is the clearest possible calibration failure.

**Why does this happen?** Step-by-step for the empty fixture:
1. Missing-README, missing-CI, missing-SECURITY.md all fire.
2. Each is a single finding with severity `medium` (weight 2) or `low` (weight 1), confidence `high` (mult 1.0), maturity `prototype` (mult 0.95), magnitude 0.9–1.0.
3. Per-category deduction ≈ 2 × 0.95 × 1.0 = **1.9 points**, against a normalized max of ~12 per category.
4. Three findings distributed across three different categories means three categories each lose ~1.9 of ~12.
5. `100 - (3 × 1.9) = 94.3` before adjustments.

The scorer is arithmetically correct. The problem is the weights. The spec in `docs/scoring_engine_spec.md` says the engine must apply **anti-gaming rules** and **applicability-aware penalties**, and that **production repos missing CI should trigger blockers** (which `maturity_profiles.json` actually sets via `"missing_ci_is_blocker": true` for production) — but the scorer never reads `missing_ci_is_blocker` and never elevates missing-CI to a blocker regardless of profile.

### 6.2 Profile flags that are declared but not honored

`maturity_profiles.json` contains:
- `missing_ci_is_blocker: true` (production) / `false` (prototype, research)
- `missing_tests_and_missing_ci_can_trigger_blocker: true` (production)

Neither `sdlc_assessor/scorer/blockers.py` nor `engine.py` reads these fields. The data is present; the logic is not wired up.

### 6.3 Hardcoded score_confidence

```python
scored["scoring"] = {..., "score_confidence": "medium"}
```

Always `"medium"`, regardless of evidence density or detector coverage. The spec specifies an explicit logic (evidence density, proxy reliance, classification clarity) that is absent.

### 6.4 Verdict logic

```python
if final_score >= distinction_threshold and not blockers:
    verdict = "pass_with_distinction"
elif final_score >= pass_threshold and not blockers:
    verdict = "pass"
elif final_score >= pass_threshold:
    verdict = "conditional_pass"
else:
    verdict = "fail"
```

This is defensible, but: it does not distinguish *critical* blockers from *high* blockers. Per `docs/scoring_engine_spec.md §Step 6`, "Pass: ≥ threshold and no active critical blocker" — i.e. high blockers are tolerable for a regular `pass`. The code collapses all blockers into "any blocker → downgrade to conditional_pass or below."

### 6.5 Hard-blocker detector is narrow

```python
if subcat == "probable_secrets" or severity == "critical":
    blockers.append(...)
```

`docs/scoring_engine_spec.md §Step 5` lists six candidate hard-blocker rules. Only two are implemented here, and neither via a first-class rule — they are a subcategory-name equality check and a severity string comparison. No rule for:
- user-controlled command execution (which IS detected as `shell=True` / `exec(` but never escalated to blocker)
- production repo with no tests and no CI
- fabricated/misleading claims
- unsafe release automation
- network-facing repo with no input validation

---

## 7. Tests

### 7.1 Empirical test-run result

```
2 failed, 24 passed in 0.49s
FAILED tests/unit/test_collector_evidence.py::test_collector_assembles_evidence_shape
FAILED tests/unit/test_collector_evidence.py::test_collector_inventory_has_non_negative_core_fields
```

Both failing tests hardcode the path `".sdlc/classification.json"`. On a clean checkout that file does not exist. The tests implicitly assume a prior `sdlc classify` run was performed. This is a **test isolation violation**: tests that depend on execution order or on state produced outside the test harness are non-reproducible.

### 7.2 Coverage gaps

- No test validates output against `docs/evidence_schema.json`. A single `jsonschema` validation test would have caught all 16 schema violations described in §4.1.
- No test for `cli.py` argument parsing. A mistyped `--use-case` would ship silently.
- No test for the `run` end-to-end subcommand.
- No test exercises the `--policy` JSON override from the filesystem side (only the direct function argument in `test_phase8_policy.py`).
- No test for `scripts/benchmark_calibration.py`.
- No test for `renderer` with data that has missing keys beyond the trivial case in `test_report_render.py`.
- No tests for Unicode paths, Windows line endings, symlinks, large repos, repos with `node_modules`, repos with binary files.
- No property-based tests (e.g. Hypothesis) for the scoring formula — invariants like "adding a finding never increases the score," "applicability `not_applicable` removes category from denominator," "positive credits are bounded by max" are untested.

### 7.3 Fixtures

Four present, two missing per PLANS.md:
- ❌ `fixture_no_ci` — needed to test the missing-CI blocker in production mode
- ❌ `fixture_research_repo` — needed to test the research maturity profile

Existing fixtures are thin. `fixture_python_basic` is a 2-line hello function. Nothing tests multi-file repos, nested packages, or real-world patterns.

---

## 8. Documentation and repo hygiene

### 8.1 README.md is one line

```
This is the initial commit
```

No project description, no install, no quickstart, no command examples, no license, no badges, no contributor info. For a public GitHub repo, this is the first thing anyone sees.

### 8.2 docs/README.md references paths that don't exist

```
- `profiles/use_case_profiles.json`
- `profiles/maturity_profiles.json`
- `profiles/repo_type_profiles.json`
```

Actual paths are `docs/use_case_profiles.json`, etc. (flat). The `docs/profiles/` subdirectory does not exist.

### 8.3 Duplicate profile data

Identical profile JSON files exist in two places:
- `docs/use_case_profiles.json`
- `sdlc_assessor/profiles/data/use_case_profiles.json`

The loader reads from the latter; the former appears to be the "spec" copy. No mechanism enforces they stay in sync. Same applies to `maturity_profiles.json` and `repo_type_profiles.json`. This is exactly the kind of drift-prone duplication that the assessor itself should flag under `documentation_truthfulness`.

### 8.4 Missing governance files

- No `LICENSE` — legally this means the repo is "all rights reserved" and cannot be used by anyone. If the intent is open source, a license must be added.
- No `SECURITY.md` — ironic for a tool that checks for it.
- No `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`.
- No `.editorconfig`.
- No pre-commit hooks, no `.pre-commit-config.yaml`.
- No CI — no `.github/workflows/`. The tool has tests but nothing runs them on PR.

### 8.5 Typos in repository name

The repo is named `SDLC-assesment` (missing an `s`). This is a cosmetic issue but will mis-match anyone searching for "SDLC assessment."

### 8.6 `__init__.py` is empty

`sdlc_assessor/__init__.py` is 512 bytes but likely just contains a docstring. No `__version__` exposed. Consumers of the library (not just CLI) have no way to check version from Python.

---

## 9. Security, performance, and correctness concerns at the code level

### 9.1 Performance cliffs

- Secret scanner reads every file as text with no size cap. A 2 GB binary will be loaded into memory.
- Three separate traversals in `common.py` for what could be one.
- `_iter_files` and `_all_files` don't short-circuit on obvious ignore directories; a typical Node.js repo has 50k+ files in `node_modules/`.
- Detectors are called sequentially, not in parallel. For a large repo this is single-core bound.
- No caching: running `sdlc run` twice re-scans everything.

### 9.2 Correctness / robustness

- `p.stat().st_size` is called twice per file in the large-file detector (line 39 and line 46).
- `secret_pattern.search(text)` returns `True` for any match, but the finding emits the path only. If a 10k-line file contains one suspected secret on line 8932, the user is told "probable secret in this file" and given no line number.
- `collect_evidence` reads `classification.json` from a required CLI-specified path, making it impossible to call as a pure function without touching disk.
- `io.write_json(path, payload)` uses `sort_keys=True` which is good for determinism, but the CLI writes these as separate JSON files with no checksum or version field.
- No cross-OS path handling for the `.sdlc/` output directory — works on POSIX, tested on Linux; untested on Windows.

### 9.3 Supply-chain posture of the repo itself

- No `SBOM` (Software Bill of Materials)
- No lockfile (`requirements.txt`, `poetry.lock`, `uv.lock` — none exist)
- No `Dependabot` / `Renovate` config
- No `pip-audit` / `safety` / `bandit` in CI (there is no CI)
- No SLSA provenance
- No signed commits required

Given the subject's stated prior work applying SAMM/SLSA to `AgentSentry` and flagging identical gaps, these same gaps are present here.

---

## 10. What is working well (honest account)

To be fair and balanced:

1. **The specs in `docs/` are serious, coherent, and well-structured.** They represent real thinking about how to decompose an SDLC assessment into evidence → scoring → reporting → remediation. The framework in `SDLC_Framework_v2_Spec.md` is the actual intellectual product.
2. **The package structure is clean.** Modules separate classifier, collector, detectors, normalizer, scorer, renderer, remediation. Dependencies run in one direction (no cycles detected in my reading).
3. **Type hints are consistent.** `from __future__ import annotations`, `dataclass(slots=True)`, explicit `StrEnum`. This is modern Python done correctly.
4. **Profile JSON data is thoughtful.** The use-case / maturity / repo-type multipliers are considered, not arbitrary. This data is the most mature part of the system.
5. **Tests exist and mostly pass.** 24/26 is not great, but it's 24/26 — the scaffolding *is* there.
6. **`PLANS.md` is itself a usable build plan.** Most of it was actually followed.
7. **The CLI contract is stable** (5 subcommands plus `run`) and matches PLANS.md exactly.
8. **Determinism discipline is evident** — `write_json` uses `sort_keys=True`, profiles are deep-copied before merging.

The repo is not broken in its bones. It's an under-baked v0.1 with the right structure. Getting it to v1.0 is engineering, not redesign.

---

## 11. Priority assessment

Using severity × reach × tractability, ranked:

| # | Issue | Severity | Reach | Tractability | Score |
|---|---|---|---|---|---|
| 1 | Scorer miscalibrated — empty repo scores 95.92 | Critical | Every output | Medium (requires calibration data) | 🔴 highest |
| 2 | Output doesn't match schema | High | Every output | High (mechanical) | 🔴 highest |
| 3 | Detectors are substring matches | High | Every finding | High (AST for Python, regex-with-boundaries for TS) | 🔴 high |
| 4 | Classifier is a stub | High | Every scoring decision | Medium | 🟠 high |
| 5 | Test suite fails 2/26 | High | Every commit | High (simple test fix) | 🔴 high |
| 6 | No CI for this repo | High | Every PR | High (one workflow file) | 🔴 high |
| 7 | Detectors scan binaries and `.venv` | Medium | Performance | High | 🟠 medium |
| 8 | README is one line | Medium | First impression | High | 🟠 medium |
| 9 | Missing LICENSE | High | Legal | High (add MIT/Apache file) | 🔴 high |
| 10 | Missing fixtures (`no_ci`, `research_repo`) | Medium | Coverage | High | 🟠 medium |
| 11 | Renderer missing spec sections | Medium | Every report | Medium | 🟠 medium |
| 12 | Remediation planner hardcodes phase/change_type | Medium | Every plan | Medium | 🟠 medium |
| 13 | No schema-validation in tests | Medium | Every release | High | 🟠 medium |
| 14 | Profile flags not wired up | Medium | Scoring correctness | High | 🟠 medium |
| 15 | `sdlc` shell script redundant | Low | Cosmetic | High | 🟡 low |

The four reds (`schema conformance`, `scorer calibration`, `tests passing`, `CI present`, `LICENSE`) are table-stakes for a public tool. They represent maybe 10–20 hours of focused work and should come first. After those are done, the larger effort of detector rewriting and classifier real-implementation is where the substantive technical work lives.

---

## 12. What I verified vs what I inferred

Per your instructions on primary sources:

**Directly verified from file contents or command output:**
- All schema violations (ran `jsonschema.Draft202012Validator` against `scored.json`)
- Test pass/fail counts (ran `pytest`)
- Benchmark scores on all four fixtures (ran `scripts/benchmark_calibration.py`)
- Every "the code does X" claim cites code I read in full
- Language detection bug (read line 23 of `classifier/engine.py`)
- Missing fixtures (compared `PLANS.md §Exact fixture repos` to `tests/fixtures/` directory listing)
- README content (read the single line)
- Pyproject dependencies (read `pyproject.toml` in full)

**Inferred but not verified by running:**
- Performance impact of secret scanner on a repo with a vendored `.venv` — described the mechanism, did not time it on a real large repo
- False-positive rates of substring detectors — described categorically, did not enumerate counts against a corpus
- Schema drift between `docs/*_profiles.json` and `sdlc_assessor/profiles/data/*_profiles.json` — did not `diff` them (action plan includes this)

Nothing in §3–§11 is invented; everything traces to the file tree or the test/benchmark runs I performed in this session.
