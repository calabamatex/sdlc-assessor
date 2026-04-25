# SDLC-assesment — Action Plan for AI Coding Agent

**Target repo:** `github.com/calabamatex/SDLC-assesment`
**Companion doc:** `sdlc_assessor_ANALYSIS.md` (same session)
**Schema convention:** Tasks use the repo's own remediation task schema (from `sdlc_assessor/remediation/planner.py` and `docs/remediation_planner_spec.md`): `id, phase, priority, linked_finding_ids, target_paths, anchor_guidance, change_type, rationale, implementation_steps, test_requirements, verification_commands`.
**Agent instructions (read first):**

1. Work tasks in order within each phase. Phases have hard dependencies — do not reorder across phase boundaries.
2. Every task has `verification_commands` that must pass before the task is considered done. Run them. If they fail, fix the task; do not move on.
3. Use stable anchor text in `anchor_guidance`, not line numbers. Line numbers drift; anchors don't.
4. Each task includes a `test_requirements` block. Add or modify the specified tests before or alongside the implementation — never after.
5. Do not batch commits. One logical change per commit with a conventional-commits message (e.g. `fix(scorer): wire missing_ci_is_blocker flag`).
6. When the task says "use AST," use AST. Do not substitute regex. When the task says "schema-validate," use `jsonschema.Draft202012Validator`.
7. After completing a phase, run the full test suite (`pytest -q`) and the schema-validation suite. Both must be clean before the next phase starts.

---

## Milestones

| Milestone | Phases | Outcome |
|---|---|---|
| M1: Credibility baseline | 1–2 | Tests pass, outputs schema-valid, CI runs, basic hygiene files present |
| M2: Contract correctness | 3–5 | Output shape matches schema, scorer honors profile flags, classifier is real |
| M3: Detector quality | 6–7 | AST-based detectors with line numbers, ignore-path discipline, occurrence counts |
| M4: Report quality | 8–9 | Renderer matches template, remediation planner produces patch-safe tasks |
| M5: Calibration and v1 release | 10–11 | Scores discriminate across fixture corpus, v1.0.0 tagged |

---

## Phase 1 — Stop the bleeding

Goal: fix what is definitely broken on a clean checkout. Anyone cloning the repo should get a passing test suite, a readable README, and a license.

### Task SDLC-001
- **id:** SDLC-001
- **phase:** phase_1_stop_the_bleeding
- **priority:** high
- **linked_finding_ids:** analysis §7.1
- **target_paths:** `tests/unit/test_collector_evidence.py`, `tests/conftest.py`
- **anchor_guidance:** The two failing tests reference the literal string `".sdlc/classification.json"` which does not exist on a clean checkout. Replace these with an in-test classification built via `classify_repo(fixture)` and written to `tmp_path`.
- **change_type:** modify_block
- **rationale:** Test isolation violation. Tests must not depend on side effects of other commands. Reproduces as `FileNotFoundError` on `pytest` from a clean clone.
- **implementation_steps:**
  1. In `tests/unit/test_collector_evidence.py`, add a `pytest.fixture` that calls `classify_repo("tests/fixtures/fixture_python_basic")` and writes the JSON to `tmp_path / "classification.json"`.
  2. Replace the hardcoded `".sdlc/classification.json"` in both failing tests with the fixture-provided path.
  3. Do not remove the `test_evidence_detector_registry_plumbing_returns_list` test — it already passes.
- **test_requirements:** Both previously-failing tests must pass on a fresh clone where `.sdlc/` does not exist.
- **verification_commands:**
  - `rm -rf .sdlc && pytest -q tests/unit/test_collector_evidence.py`
  - `pytest -q` → expect `26 passed, 0 failed`

### Task SDLC-002
- **id:** SDLC-002
- **priority:** high
- **target_paths:** `pyproject.toml`
- **anchor_guidance:** The `[project]` table has no `dependencies` and no `[project.optional-dependencies].dev`. Add a `dev` extra with `pytest`, `jsonschema`, `mypy`, `ruff`.
- **change_type:** modify_block
- **rationale:** `pytest` is used by tests but not declared. `jsonschema` will be required by Phase 2 schema-validation tests. Declaring these makes the repo actually installable for contributors.
- **implementation_steps:**
  1. Add to `pyproject.toml`:
     ```toml
     [project.optional-dependencies]
     dev = [
       "pytest>=8.0",
       "jsonschema>=4.20",
       "mypy>=1.10",
       "ruff>=0.5",
     ]
     ```
  2. Add `[tool.setuptools.packages.find]` with `where = ["."]` and `include = ["sdlc_assessor*"]` to make package discovery explicit.
  3. Add `license = { text = "MIT" }` (pending SDLC-003).
  4. Add `readme = "README.md"`.
  5. Add `authors = [{ name = "calabamatex" }]`.
  6. Add `[tool.ruff]` with `line-length = 120` and `target-version = "py312"`.
- **test_requirements:** `pip install -e ".[dev]"` succeeds on a fresh virtualenv.
- **verification_commands:**
  - `python -m venv /tmp/sdlc_venv && /tmp/sdlc_venv/bin/pip install -e ".[dev]"`
  - `/tmp/sdlc_venv/bin/pytest -q`

### Task SDLC-003
- **id:** SDLC-003
- **priority:** high
- **target_paths:** `LICENSE`
- **anchor_guidance:** File does not exist.
- **change_type:** create_file
- **rationale:** Without a license, legally no one can use, fork, or contribute to the code. Public GitHub repos without licenses are "all rights reserved" by default.
- **implementation_steps:**
  1. Confirm intended license with maintainer. Default to MIT if not specified.
  2. Create `LICENSE` with the standard MIT text, year `2026`, copyright holder `calabamatex`.
- **test_requirements:** GitHub's license-detection UI recognizes the file (informational — not a unit test).
- **verification_commands:** `test -f LICENSE && head -1 LICENSE | grep -qi "MIT License"`

### Task SDLC-004
- **id:** SDLC-004
- **priority:** high
- **target_paths:** `README.md`
- **anchor_guidance:** Current content is literally the single line `This is the initial commit`.
- **change_type:** update_docs
- **rationale:** The README is the first surface for anyone encountering the repo. A one-line README undermines `documentation_truthfulness` — the same category this tool is supposed to assess.
- **implementation_steps:**
  1. Replace with a README covering: what this tool is (one paragraph pointing at `docs/SDLC_Framework_v2_Spec.md`), install (`pip install -e ".[dev]"`), quickstart (a `sdlc run` example against `tests/fixtures/fixture_python_basic`), CLI reference table (6 subcommands), profiles summary (4 use-cases × 3 maturity × 8 repo-types), link to `docs/`, link to `PLANS.md`, license line.
  2. Do not invent features. Describe only what currently works. If something is planned-but-not-built, put it in a "Roadmap" section with an explicit "not yet implemented" tag.
- **test_requirements:** None.
- **verification_commands:** `wc -l README.md` returns ≥ 50.

### Task SDLC-005
- **id:** SDLC-005
- **priority:** high
- **target_paths:** `.github/workflows/ci.yml`
- **anchor_guidance:** File does not exist.
- **change_type:** add_workflow
- **rationale:** No automated validation exists. Also, the tool itself flags missing-CI as a finding — self-hosting this check is table-stakes credibility.
- **implementation_steps:**
  1. Create `.github/workflows/ci.yml` with jobs: `test` (ubuntu-latest, Python 3.12), `lint` (ruff), `typecheck` (mypy), `schema-validate` (runs the schema-validation test added in Phase 2).
  2. Trigger on `push` and `pull_request` to `main`.
  3. Cache pip by `pyproject.toml` hash.
- **test_requirements:** CI green on a dummy PR.
- **verification_commands:**
  - `yamllint .github/workflows/ci.yml` (after `pip install yamllint`)
  - Push a branch; confirm Actions UI shows green.

### Task SDLC-006
- **id:** SDLC-006
- **priority:** medium
- **target_paths:** `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- **anchor_guidance:** Files do not exist.
- **change_type:** create_file
- **rationale:** Standard OSS governance. `SECURITY.md` is especially apt given the tool checks for it.
- **implementation_steps:**
  1. `SECURITY.md` — disclosure policy, contact email, supported versions.
  2. `CONTRIBUTING.md` — how to run tests, how to add a detector, how to add a profile.
  3. `CHANGELOG.md` — Keep-a-Changelog format, v0.1.0 entry describing current state, v0.2.0-unreleased header.
- **test_requirements:** None.
- **verification_commands:** `test -f SECURITY.md && test -f CONTRIBUTING.md && test -f CHANGELOG.md`

---

## Phase 2 — Contract conformance

Goal: the output JSON validates against `docs/evidence_schema.json`. Every finding has `direction` and `magnitude`. `scoring.category_scores` is an array, not a dict. `overall_score` is an integer.

### Task SDLC-007
- **id:** SDLC-007
- **priority:** high
- **target_paths:** `tests/unit/test_schema_conformance.py` (new)
- **anchor_guidance:** File does not exist.
- **change_type:** add_tests
- **rationale:** No test currently checks output against the declared schema. This test enforces the contract and will fail until SDLC-008 through SDLC-012 are done. That is the point — failing tests drive the fix.
- **implementation_steps:**
  1. Create `tests/unit/test_schema_conformance.py`.
  2. For each fixture in `[fixture_empty_repo, fixture_python_basic, fixture_probable_secret, fixture_typescript_basic]`, run the full pipeline in `tmp_path`, load `evidence.json` and `scored.json`, and validate each with `jsonschema.Draft202012Validator` against `docs/evidence_schema.json`.
  3. Test asserts `list(validator.iter_errors(payload)) == []` with a helpful error message listing violations.
- **test_requirements:** The test must exist and must initially fail against the current implementation. It will turn green once Tasks 008–012 land.
- **verification_commands:** `pytest -q tests/unit/test_schema_conformance.py` (expected to fail now; expected to pass by end of Phase 2).

### Task SDLC-008
- **id:** SDLC-008
- **priority:** high
- **target_paths:** `sdlc_assessor/detectors/common.py`, `python_pack.py`, `tsjs_pack.py`
- **anchor_guidance:** Every finding emits `"score_impact": {"magnitude_modifier": X}`. The schema requires `score_impact: {direction: "positive"|"negative"|"neutral", magnitude: int 0-10}`.
- **change_type:** modify_block
- **rationale:** Schema violations 1–12 in analysis §4.1.
- **implementation_steps:**
  1. For every detector finding, replace `"score_impact": {"magnitude_modifier": X}` with `"score_impact": {"direction": "negative", "magnitude": int_0_to_10, "rationale": "<short reason>"}`.
  2. Keep `magnitude_modifier` as an **additional** key if the scorer still uses it (it does), or refactor the scorer (SDLC-009) to read `magnitude / 10.0` as the modifier.
  3. Magnitude mapping: info→1, low→2, medium→4, high→7, critical→10.
- **test_requirements:** `pytest tests/unit/test_schema_conformance.py` makes progress (fewer errors).
- **verification_commands:** `pytest -q tests/unit/test_schema_conformance.py -k "probable_secret"` passes for `score_impact` errors.

### Task SDLC-009
- **id:** SDLC-009
- **priority:** high
- **target_paths:** `sdlc_assessor/scorer/engine.py`
- **anchor_guidance:** Lines `scored["scoring"] = { ... "category_scores": category_scores ... }` where `category_scores` is a dict keyed by category name.
- **change_type:** modify_block
- **rationale:** Schema requires `category_scores` as an array of objects with `{category, applicable, score, max_score, summary, key_findings}`. Also schema requires `base_weights`, `applied_weights`, and integer `overall_score`.
- **implementation_steps:**
  1. Emit `category_scores` as a list: `[{"category": c, "applicable": applicability[c] != "not_applicable", "score": int(round(v["score"])), "max_score": int(round(v["max"])), "summary": "<2-5 sentence narrative>", "key_findings": [<top-3 finding ids by deduction magnitude>]} for c, v in category_scores.items()]`.
  2. Add `"base_weights": BASE_WEIGHTS` to the scoring block.
  3. Add `"applied_weights": weighted_max` to the scoring block.
  4. Cast `overall_score` to `int(round(final_score))` for schema conformance. Preserve a `overall_score_precise` float field for internal use.
  5. Preserve backward compatibility by keeping the old dict form under `scoring.legacy_category_scores` if anything downstream reads it. (Check: only `renderer/markdown.py` does. Update SDLC-015 in Phase 4 to match the new shape.)
- **test_requirements:** Schema-conformance test passes for `scoring` block.
- **verification_commands:** `pytest -q tests/unit/test_schema_conformance.py`

### Task SDLC-010
- **id:** SDLC-010
- **priority:** high
- **target_paths:** `sdlc_assessor/scorer/engine.py`
- **anchor_guidance:** Narrative summary per category is required by `docs/scoring_engine_spec.md §Narrative rules` (2-5 sentences).
- **change_type:** modify_symbol
- **rationale:** The renderer template §9 requires a "Summary" column, and the schema requires `summary` as a required field on each `category_scores` entry.
- **implementation_steps:**
  1. Write a `_build_category_summary(category, applicability, deductions_by_cat, findings_in_cat, maturity)` helper.
  2. Template: `"{applicability_statement}. {strongest_finding_statement}. {count_of_other_findings} other findings contributed {secondary_deductions:.1f} points of deduction. {calibration_note_if_score_is_bounded_at_max}."`
  3. Do not invent evidence — if `findings_in_cat` is empty, the summary should say "No findings in this category; full points retained."
- **test_requirements:** Renderer test verifies the summary field is non-empty for categories with findings.
- **verification_commands:** `pytest -q tests/golden/`

### Task SDLC-011
- **id:** SDLC-011
- **priority:** high
- **target_paths:** `sdlc_assessor/core/schema.py`, `sdlc_assessor/core/__init__.py`
- **anchor_guidance:** `validate_evidence_top_level` only checks key presence, not full schema. Add a `validate_evidence_full(payload)` that uses `jsonschema`.
- **change_type:** modify_symbol
- **rationale:** Phase 2 requires conformance by construction. The CLI should optionally validate on write.
- **implementation_steps:**
  1. Add `validate_evidence_full(payload, schema_path=None) -> list[str]` returning a list of human-readable error messages (empty list = valid).
  2. Gate behind an optional import of `jsonschema`. If not installed, fall back to `validate_evidence_top_level` with a warning.
  3. Call `validate_evidence_full` at the end of `score_evidence` in dev/debug mode (env var `SDLC_STRICT=1`) and raise if errors exist. Production mode silently passes.
- **test_requirements:** Unit tests for both the schema-pass and schema-fail path.
- **verification_commands:** `pytest -q tests/unit/test_core_schema.py`

### Task SDLC-012
- **id:** SDLC-012
- **priority:** high
- **target_paths:** `sdlc_assessor/core/schema.py`, `pyproject.toml`
- **anchor_guidance:** `_default_schema_path` probes `docs/evidence_schema.json` relative to `__file__`. This works in editable installs but breaks in wheels.
- **change_type:** modify_symbol
- **rationale:** `pyproject.toml` already declares `package_data` for `sdlc_assessor.core = ["evidence_schema.json"]` but the file at `sdlc_assessor/core/evidence_schema.json` is not committed. When built as a wheel and installed elsewhere, schema loading will fail.
- **implementation_steps:**
  1. Copy `docs/evidence_schema.json` to `sdlc_assessor/core/evidence_schema.json`.
  2. Add a pre-commit hook or CI check that enforces byte-equality between the two copies (a simple `sha256sum` compare step).
  3. Make `_default_schema_path` prefer the package-local copy first, falling back to `docs/` only when running from the source tree.
- **test_requirements:** `test_core_can_load_schema_from_default_when_cwd_is_elsewhere` still passes, plus a new test that installs the package and loads schema from the installed location.
- **verification_commands:**
  - `pytest -q tests/unit/test_core_schema.py`
  - `pip install . --target /tmp/wheel_test && cd /tmp/wheel_test && python -c "from sdlc_assessor.core.schema import load_evidence_schema; load_evidence_schema()"`

---

## Phase 3 — Wire up what's declared

Goal: fields that already exist in profile JSONs but are ignored by code get honored. No new features — just connecting data that is already in the repository to code that claims to use it.

### Task SDLC-013
- **id:** SDLC-013
- **priority:** high
- **target_paths:** `sdlc_assessor/scorer/blockers.py`, `sdlc_assessor/scorer/engine.py`
- **anchor_guidance:** `maturity_profiles.json` has `"missing_ci_is_blocker": true` for production and `"missing_tests_and_missing_ci_can_trigger_blocker": true`. Neither field is read anywhere.
- **change_type:** modify_symbol
- **rationale:** Declared-but-ignored configuration is a trust-erosion pattern. The data says "production repos missing CI should be blockers" and the code silently disagrees.
- **implementation_steps:**
  1. Change `detect_hard_blockers(findings, maturity_profile=None, inventory=None)` signature.
  2. If `maturity_profile.get("missing_ci_is_blocker")` and any finding has `subcategory == "missing_ci"`, emit a hard blocker.
  3. If `maturity_profile.get("missing_tests_and_missing_ci_can_trigger_blocker")` and missing_ci finding exists AND inventory reports `test_files == 0`, emit a hard blocker with title `"Missing tests and CI on production-profile repository"`.
  4. Update `score_evidence` to pass `maturity_profile` and `inventory` into `detect_hard_blockers`.
- **test_requirements:**
  - New test: production-profile missing-CI repo produces a blocker.
  - New test: prototype-profile missing-CI repo does not produce this blocker.
- **verification_commands:** `pytest -q tests/unit/test_scorer_blockers.py`

### Task SDLC-014
- **id:** SDLC-014
- **priority:** high
- **target_paths:** `sdlc_assessor/classifier/engine.py`
- **anchor_guidance:** Line 23: `for p in repo_path.rglob("*.ts")`.
- **change_type:** modify_block
- **rationale:** The rglob pattern matches only `.ts`; the suffix check allows 4 extensions. A JS-only or TSX-only repo is invisible to the TS/JS pack.
- **implementation_steps:**
  1. Replace with a single loop over the full rglob, checking suffix set membership.
  2. Exclude `node_modules`, `.git`, `dist`, `build`, `.next`, `coverage`, `.venv`, `__pycache__`, `.mypy_cache`, `.ruff_cache` from iteration (hardcoded exclusion set — respect for `.gitignore` is a separate task, SDLC-020).
  3. Also detect Go (`.go`), Rust (`.rs`), Java (`.java`), C# (`.cs`) — record but do not yet dispatch packs (packs for those languages are not yet implemented).
- **test_requirements:**
  - Test with a pure-JS fixture (add `fixture_javascript_basic`) — must include `typescript_javascript` pack.
  - Test with a pure-TSX fixture — same.
  - Test with a vendored `node_modules` — must NOT treat that as the repo's own code.
- **verification_commands:** `pytest -q tests/unit/test_classifier.py`

### Task SDLC-015
- **id:** SDLC-015
- **priority:** high
- **target_paths:** `sdlc_assessor/renderer/markdown.py`
- **anchor_guidance:** `for cat, data in scoring.get("category_scores", {}).items():` treats `category_scores` as a dict.
- **change_type:** modify_symbol
- **rationale:** After SDLC-009, `category_scores` is a list. The renderer will break.
- **implementation_steps:**
  1. Change the iteration to handle the new list-of-dicts shape with keys `category, applicable, score, max_score, summary`.
  2. Maintain backward compatibility: if `category_scores` is a dict (old shape), convert it inline for one release. Log a deprecation warning.
- **test_requirements:** Existing `test_report_contains_required_sections` passes with the new shape. Add a test with the old shape to verify back-compat.
- **verification_commands:** `pytest -q tests/golden/`

### Task SDLC-016
- **id:** SDLC-016
- **priority:** medium
- **target_paths:** `sdlc_assessor/classifier/engine.py`
- **anchor_guidance:** All 7 non-language fields return `"unknown"` with confidence 0.2.
- **change_type:** modify_symbol
- **rationale:** `docs/SDLC_Framework_v2_Spec.md §Classifier` lists required outputs. The scorer depends on `repo_archetype`, and the user is forced to supply it via `--repo-type`. A real classifier makes `--repo-type` optional.
- **implementation_steps:**
  1. **Archetype:** `Dockerfile`/`docker-compose.yml` + web framework imports → `service`. `pyproject.toml` with `[project.scripts]` entry AND no server imports → `cli`. `pyproject.toml` with `[project]` but no entry scripts, and a `src/` or package layout → `library`. Multiple `pyproject.toml` / `package.json` in subdirectories → `monorepo`. `notebooks/` or `*.ipynb` dominant → `research_repo`. `terraform/`, `*.tf`, `ansible/`, `helm/` → `infrastructure`. Default `unknown` only if no signal.
  2. **Network exposure:** grep for `fastapi`, `flask`, `django`, `express`, `http.ListenAndServe`, `actix-web`, `socket.bind`, `.listen(`. True if any match.
  3. **Release surface:** `published_package` if pyproject has `name`/`version` and `.github/workflows/release.yml` or `publish.yml` exists. `deployable_service` if Dockerfile. `research_only` if archetype is `research_repo`. Else `internal_only`.
  4. **Maturity:** `production` if CI exists AND tests exist AND pyproject has `name`+`version`. `prototype` if README exists but no CI. `research` if notebooks dominate.
  5. **Classification confidence:** `0.9` if 3+ signals agree, `0.6` if 2, `0.3` if 1, `0.2` fallback.
  6. **Deployment surface:** `networked` if network_exposure, `package_only` if library, `local_only` if cli, else `unknown`.
- **test_requirements:** For each of the 8 repo archetypes, add a minimal fixture and a test asserting the classifier picks the right archetype with confidence ≥ 0.3.
- **verification_commands:** `pytest -q tests/unit/test_classifier.py`

### Task SDLC-017
- **id:** SDLC-017
- **priority:** medium
- **target_paths:** `sdlc_assessor/cli.py`
- **anchor_guidance:** `score` and `run` subcommands use `--use-case`, `--maturity`, `--repo-type` as `required=True`.
- **change_type:** modify_symbol
- **rationale:** Once the classifier is real (SDLC-016), these should default from the classifier output. The user should be able to override but not forced to supply them.
- **implementation_steps:**
  1. Make `--maturity` and `--repo-type` optional. Default to the values from `classification.json`.
  2. `--use-case` stays required (it expresses intent, not fact).
  3. Emit a line to stderr: `using maturity=prototype (from classifier), repo-type=cli (from classifier)` when defaulted.
- **test_requirements:** CLI integration test with only `--use-case`.
- **verification_commands:** `python -m sdlc_assessor.cli run tests/fixtures/fixture_python_basic --use-case engineering_triage --out-dir /tmp/out && jq '.scoring.verdict' /tmp/out/scored.json`

### Task SDLC-018
- **id:** SDLC-018
- **priority:** medium
- **target_paths:** `sdlc_assessor/profiles/data/*.json`, `docs/*.json`
- **anchor_guidance:** Profile JSONs exist in both `docs/` and `sdlc_assessor/profiles/data/`. The loader reads only `sdlc_assessor/profiles/data/`.
- **change_type:** modify_block
- **rationale:** Duplicated source of truth is a drift-prone anti-pattern and the exact kind of thing this tool should flag in other repos.
- **implementation_steps:**
  1. Decide on canonical location: `sdlc_assessor/profiles/data/`.
  2. Delete the `docs/*.json` profile copies.
  3. Update `docs/README.md` to point at `sdlc_assessor/profiles/data/`.
  4. Add a test that fails if `docs/*.json` profile files are reintroduced without being symlinked to the canonical location.
- **test_requirements:** New test: `test_no_duplicate_profile_jsons` asserts that each profile-name exists in exactly one location.
- **verification_commands:** `pytest -q tests/unit/test_profiles_loader.py`

---

## Phase 4 — Detector quality

Goal: detectors use AST (for Python), regex-with-boundaries (for TS/JS), respect `.gitignore` + standard ignore dirs, capture line numbers + counts, and produce schema-conforming evidence.

### Task SDLC-019
- **id:** SDLC-019
- **priority:** high
- **target_paths:** `sdlc_assessor/detectors/python_pack.py`
- **anchor_guidance:** All six checks use `pattern in text` substring matching.
- **change_type:** replace_unsafe_pattern
- **rationale:** Analysis §5.2. Substring matching produces wrong-in-both-directions results. Python's built-in `ast` module makes this trivial to do correctly and lets us emit line numbers.
- **implementation_steps:**
  1. For each `.py` file: `tree = ast.parse(source, filename=str(p))` wrapped in try/except `SyntaxError` (log and skip).
  2. `ast.walk(tree)`:
     - `ast.ExceptHandler` with `node.type is None` → bare except (line `node.lineno`).
     - `ast.ExceptHandler` with `isinstance(node.type, ast.Name) and node.type.id == "Exception"` → broad except.
     - `ast.Call` with `func` name ending in `subprocess` and any keyword `shell=True` → `subprocess_shell_true`. Detect via `ast.keyword(arg='shell', value=ast.Constant(value=True))`.
     - `ast.Call` with `func.id == "print"` → `print_usage`. Count occurrences per file; emit one finding per file with `count`.
     - `ast.Name(id="Any")` inside annotations (subscript of `typing`) OR `ast.Attribute(value=Name("typing"), attr="Any")` → `any_usage`.
     - Comment regex for `# type: ignore` (AST does not preserve comments).
  3. Emit each finding with full schema: `evidence: [{path, line_start, line_end, snippet: source_lines[line-1:line+1], match_type: "exact", count: N}]`.
  4. Respect ignore dirs: wrap the file-finding loop in a helper that filters `.git`, `.venv`, `venv`, `__pycache__`, `node_modules`, `site-packages`, `build`, `dist`, `.eggs`, `*.egg-info`.
- **test_requirements:**
  - Fixture file with `"# print("` in a comment — no finding.
  - Fixture file with `pprint(x)` — no `print_usage` finding.
  - Fixture file with `shell = True` in a string — no finding.
  - Fixture file with 3 `print()` calls — one finding with `count: 3`.
- **verification_commands:** `pytest -q tests/unit/test_detectors.py`

### Task SDLC-020
- **id:** SDLC-020
- **priority:** high
- **target_paths:** `sdlc_assessor/detectors/tsjs_pack.py`
- **anchor_guidance:** Substring matches `"as any"`, `"console."`, `"catch {}"`, `"JSON.parse("`, `"exec("`, `"execSync("`.
- **change_type:** replace_unsafe_pattern
- **rationale:** Analysis §5.3. For TS/JS we don't have AST out-of-the-box, but regex with word boundaries fixes most false positives.
- **implementation_steps:**
  1. Strip comments and string literals before scanning. A minimal regex-based stripper is enough for v1 (block comments `/*...*/`, line comments `//...`, string literals `'...'` `"..."` `` `...` ``).
  2. Use `\bexec\s*\(` and `\bexecSync\s*\(` to avoid matching `execa(`, `nexec(`.
  3. `catch\s*(?:\(\s*(?:\w+|_)\s*\))?\s*\{\s*\}` for truly empty catch — also flags `catch (e) {}`.
  4. For tsconfig: use `json5` library (add to deps) or strip comments with regex before `json.loads`. Honor `"extends"` chain up to 3 levels.
  5. Downgrade `JSON.parse` severity from `medium` to `info` unless the parsed input is unguarded by a try/catch in surrounding scope. For v1, just demote it — the AST-free scope check is Phase 5 work.
- **test_requirements:**
  - Fixture with `catch (e) {}` — one empty_catch finding.
  - Fixture with `execa("tool")` — no exec finding.
  - Fixture with strict mode inherited via `extends` — no missing_strict_mode finding.
- **verification_commands:** `pytest -q tests/unit/test_detectors.py`

### Task SDLC-021
- **id:** SDLC-021
- **priority:** high
- **target_paths:** `sdlc_assessor/detectors/common.py`
- **anchor_guidance:** Three separate traversals; no ignore-path filter; reads every file as text.
- **change_type:** modify_block
- **rationale:** Analysis §5.1. Performance cliff on any real repo, plus false positives from vendored code.
- **implementation_steps:**
  1. Introduce `_walk_repo_files(repo_path, ignore_dirs=DEFAULT_IGNORES, max_file_size=5_000_000)`. Default ignores: `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`, `site-packages`, `build`, `dist`, `.eggs`, `*.egg-info`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.next`, `target` (Rust).
  2. Single-pass traversal in `run_common_detectors`: secrets + large files + committed artifacts all in one loop.
  3. Binary detection: open file and check for null bytes in first 8 KB. Skip secret scanning for binaries (but still count them toward large_files).
  4. Respect `.gitignore` if present: use `pathspec` library (add to deps) to parse and filter.
  5. Update `README.md`/`SECURITY.md` detection to include `.github/`, `docs/`, `Readme.rst`, `README`, `README.txt`.
  6. Add per-match line numbers to the secrets finding.
  7. Cap file-read at `max_file_size`; if exceeded, emit a `large_files` finding and skip secret scan on that file.
- **test_requirements:**
  - Fixture with a vendored `node_modules/leftpad/index.js` containing `API_KEY = "x"` — no finding (ignored).
  - Fixture with a 200-byte file containing `api_key = "abc"` — one finding with `line_start`.
  - Fixture with `.github/SECURITY.md` present — no missing_security_md finding.
  - Fixture with a 200 MB binary — no OOM, one large_files finding, no secret scan attempted.
- **verification_commands:** `pytest -q tests/unit/test_detectors.py -v`

### Task SDLC-022
- **id:** SDLC-022
- **priority:** medium
- **target_paths:** `tests/fixtures/fixture_no_ci/`, `tests/fixtures/fixture_research_repo/`
- **anchor_guidance:** Directories do not exist. PLANS.md §Exact fixture repos lists them.
- **change_type:** create_file
- **rationale:** Closes the gap PLANS.md specified but never built.
- **implementation_steps:**
  1. `fixture_no_ci/`: a minimal Python package structure with a README, `main.py`, `tests/test_main.py`, but no `.github/workflows/`. Used to test `missing_ci` blocker in production mode.
  2. `fixture_research_repo/`: a notebook (`analysis.ipynb`), a `requirements.txt`, a `README.md` describing an experiment, no tests, no CI. Used to test research maturity profile.
  3. Update `scripts/benchmark_calibration.py` FIXTURES list to include both.
- **test_requirements:** Benchmark runs and emits scores for both new fixtures.
- **verification_commands:** `python scripts/benchmark_calibration.py | jq '[.[] | .fixture]'` includes both new fixtures.

---

## Phase 5 — Renderer + remediation faithfulness

Goal: the Markdown report matches `docs/renderer_template.md` and the remediation plan uses the full schema from `docs/remediation_planner_spec.md`.

### Task SDLC-023
- **id:** SDLC-023
- **priority:** medium
- **target_paths:** `sdlc_assessor/renderer/markdown.py`
- **anchor_guidance:** Hardcoded strings `"This report summarizes repository evidence, scoring, and blocker status."` and `"Evidence collection and scoring pipeline executed."` in §2 and §6.
- **change_type:** modify_symbol
- **rationale:** Renderer template §2 requires 2–4 paragraphs covering 5 specific points; §6 requires 3–5 strengths each with file + line + reason.
- **implementation_steps:**
  1. §2 Executive Summary: build from `scoring.verdict`, `scoring.overall_score`, top 3 findings by severity × confidence × magnitude, `classification.repo_archetype`, `classification.classification_confidence`.
  2. §6 Top Strengths: derive from categories with `score == max_score` (full points). For each such category, state the applicability and the detector breadth. If no category is at full points, say so explicitly rather than inventing praise.
  3. §7 Top Risks: top 5 findings ordered by `severity_weight × confidence_multiplier`. Each with severity, statement, evidence path, confidence.
  4. §10: group by category, sort critical → high → medium → low → info.
  5. §4 Classification Box: include `release_surface`, `classification_confidence`.
  6. §5 Inventory: all 11 fields from schema, show `n/a` for missing.
- **test_requirements:** Golden test expanded to check all 11 sections render and §6 does not invent unbacked strengths.
- **verification_commands:** `pytest -q tests/golden/`

### Task SDLC-024
- **id:** SDLC-024
- **priority:** medium
- **target_paths:** `sdlc_assessor/remediation/planner.py`
- **anchor_guidance:** `phase = "phase_1_safety"` hardcoded; `change_type = "modify_block"` hardcoded; `verification_commands = ["pytest -q"]` hardcoded.
- **change_type:** modify_symbol
- **rationale:** Remediation planner spec §Change types allows 9 values; §Phase summary requires sequenced phases; §Verification command should match the fix type.
- **implementation_steps:**
  1. Map `subcategory` → `change_type`:
     - `probable_secrets` → `tighten_validation` + `update_docs` (rotate secret, document)
     - `missing_ci` → `add_workflow`
     - `missing_readme` → `update_docs`
     - `missing_security_md` → `create_file`
     - `committed_artifacts` → `remove_artifact`
     - `shell=True`, `exec(`, `execSync(` → `replace_unsafe_pattern`
     - `bare_except`, `broad_except_exception` → `modify_symbol`
     - `any_usage`, `type_ignore` → `tighten_validation`
     - `print_usage`, `console_usage` → `modify_block`
     - `missing_strict_mode` → `tighten_validation`
     - `json_parse` → `tighten_validation`
     - `empty_catch` → `modify_block`
  2. Phase assignment by dependency: security blockers → `phase_1_security`; validation/type safety → `phase_2_contracts`; tests → `phase_3_tests`; CI/hygiene → `phase_4_ci`; docs → `phase_5_docs`.
  3. Per-change-type `verification_commands`: `add_workflow` → `yamllint .github/workflows/ && act -n` (or gh-cli dry-run); `replace_unsafe_pattern` in TS → `npm test -- --grep <symbol>`; in Python → `pytest -k <module>`.
  4. Emit `effort` estimate XS/S/M/L/XL from a small lookup table.
  5. Emit `expected_score_delta` per-task based on deduction weight × confidence × maturity.
- **test_requirements:** Remediation test expanded: assert `change_type` is in the 9-value allowlist, assert `phase` is one of 5 declared phases, assert `verification_commands` is non-trivial.
- **verification_commands:** `pytest -q tests/unit/test_remediation.py`

### Task SDLC-025
- **id:** SDLC-025
- **priority:** medium
- **target_paths:** `sdlc_assessor/remediation/markdown.py`
- **anchor_guidance:** Each task renders every key as `f"- {key}: {task.get(key)}"` — unreadable for list-valued keys.
- **change_type:** modify_block
- **rationale:** Output is currently `- implementation_steps: ['step1', 'step2', 'step3']` which is a raw Python list repr in a Markdown file.
- **implementation_steps:**
  1. Render list-valued keys (`implementation_steps`, `test_requirements`, `verification_commands`, `linked_finding_ids`, `target_paths`) as nested Markdown lists.
  2. Render `anchor_guidance` and `rationale` as prose paragraphs, not as a single-line key/value.
  3. Group tasks by phase with `## Phase 1 — Security` headers.
- **test_requirements:** Remediation markdown test asserts nested lists are present and no `'['` or `'{'` appears in the rendered output (Python repr smell check).
- **verification_commands:** `pytest -q tests/unit/test_remediation.py`

---

## Phase 6 — Scorer calibration

Goal: the scorer discriminates. Fixture scores span at least 40 points. Empty-repo does not earn distinction. Probable-secret fixture scores below `pass_threshold`.

### Task SDLC-026
- **id:** SDLC-026
- **priority:** high
- **target_paths:** `sdlc_assessor/scorer/engine.py`, `sdlc_assessor/profiles/data/maturity_profiles.json`
- **anchor_guidance:** Every fixture scores ≥ 92 — see benchmark output in analysis §6.1.
- **change_type:** modify_block
- **rationale:** The scorer's arithmetic is correct, but the weights are too small relative to category maxes. Three medium findings deduct ~6 points on a 100-point scale — not enough.
- **implementation_steps:**
  1. Raise severity weights: info 0, low 2 (from 1), medium 5 (from 2), high 10 (from 4), critical 20 (from 6).
  2. Reduce confidence dampening: high 1.0, medium 0.9 (from 0.75), low 0.7 (from 0.5).
  3. Add a "missing essentials" flat penalty for production+ repos: missing CI → -10, missing README → -8, missing tests → -15. These are evidence-backed penalties, not new findings.
  4. Introduce calibration targets in `docs/calibration_targets.md`: empty repo → ≤ 40, basic-hello-world → 55–70, probable-secret → 30–50 (conditional_pass at best), minor-issues-repo → 70–85, production-grade-repo → ≥ 85.
  5. Add `scripts/calibration_check.py` that asserts fixture scores fall within their target bands. Run in CI.
- **test_requirements:** Calibration check passes. `fixture_empty_repo` scores ≤ 40 under any use-case profile with maturity `production`.
- **verification_commands:** `python scripts/benchmark_calibration.py && python scripts/calibration_check.py`

### Task SDLC-027
- **id:** SDLC-027
- **priority:** medium
- **target_paths:** `sdlc_assessor/scorer/engine.py`
- **anchor_guidance:** `score_confidence = "medium"` hardcoded.
- **change_type:** modify_symbol
- **rationale:** Spec `docs/scoring_engine_spec.md §Recommended score confidence logic` specifies evidence-density-driven computation.
- **implementation_steps:**
  1. Compute `evidence_density = len(findings) / max(inventory.source_files, 1)`.
  2. Compute `proxy_ratio = len([f for f in findings if f.confidence == "medium"]) / max(len(findings), 1)`.
  3. Compute `classification_confidence = classification.classification_confidence`.
  4. Rules:
     - high: `classification_confidence >= 0.7 AND proxy_ratio <= 0.3 AND evidence_density >= 0.1`
     - low: `classification_confidence <= 0.3 OR proxy_ratio >= 0.7`
     - medium: otherwise
- **test_requirements:** Unit test with three evidence states producing the three confidence levels.
- **verification_commands:** `pytest -q tests/unit/test_scorer_blockers.py`

### Task SDLC-028
- **id:** SDLC-028
- **priority:** medium
- **target_paths:** `sdlc_assessor/scorer/blockers.py`
- **anchor_guidance:** Hard-blocker logic currently only fires on `subcategory == "probable_secrets"` or `severity == "critical"`.
- **change_type:** modify_symbol
- **rationale:** `docs/scoring_engine_spec.md §Step 5` lists 6 blocker rules; only 2 are implemented.
- **implementation_steps:**
  1. Add blocker rule: `shell=True` or `exec(`/`execSync(` with user-controlled argument in a repo classified `service` with `network_exposure=True` → `unsafe_command_execution` blocker.
  2. Add blocker rule: production maturity + missing CI + no tests (uses SDLC-013 logic).
  3. Add blocker rule: committed `*.pem`, `*.key`, `id_rsa` → `committed_credential` blocker.
  4. Distinguish blocker severity: `critical` vs `high`. Verdict logic (SDLC-029) uses this.
- **test_requirements:** Each new rule has a fixture + test.
- **verification_commands:** `pytest -q tests/unit/test_scorer_blockers.py`

### Task SDLC-029
- **id:** SDLC-029
- **priority:** medium
- **target_paths:** `sdlc_assessor/scorer/engine.py`
- **anchor_guidance:** Verdict logic treats all blockers as equivalent.
- **change_type:** modify_block
- **rationale:** Spec: "Pass: ≥ threshold and no active **critical** blocker." High blockers should allow `conditional_pass`, not force `fail`.
- **implementation_steps:**
  1. `critical_blockers = [b for b in blockers if b["severity"] == "critical"]`
  2. `has_critical = bool(critical_blockers)`
  3. Verdict tree:
     - `pass_with_distinction` if score ≥ distinction AND no blockers
     - `pass` if score ≥ pass AND no critical blockers (high blockers allowed with a note)
     - `conditional_pass` if score ≥ pass AND has critical blockers OR score < pass AND has no blockers
     - `fail` otherwise
- **test_requirements:** Test matrix of (score_above_threshold × has_high_blocker × has_critical_blocker) → expected verdict.
- **verification_commands:** `pytest -q tests/unit/`

---

## Phase 7 — CI, release, and polish

### Task SDLC-030
- **id:** SDLC-030
- **priority:** medium
- **target_paths:** `sdlc`
- **anchor_guidance:** Shell wrapper at repo root duplicates `[project.scripts]` entry.
- **change_type:** remove_artifact
- **rationale:** Redundant; not marked executable in git; no Windows equivalent.
- **implementation_steps:** Delete the file. Update README install instructions to use `pip install -e ".[dev]"` and call `sdlc` directly.
- **verification_commands:** `test ! -f sdlc && which sdlc` (after install).

### Task SDLC-031
- **id:** SDLC-031
- **priority:** medium
- **target_paths:** `.github/workflows/release.yml`
- **anchor_guidance:** File does not exist.
- **change_type:** add_workflow
- **rationale:** Release hygiene. Without a reproducible release process, `release_surface` claims are not verifiable.
- **implementation_steps:** Tag-triggered workflow that builds wheel/sdist, runs tests, publishes to PyPI via trusted publishing, attaches artifacts to GitHub Release.
- **verification_commands:** Dry-run on a test tag.

### Task SDLC-032
- **id:** SDLC-032
- **priority:** low
- **target_paths:** `.pre-commit-config.yaml`, `pyproject.toml`
- **anchor_guidance:** No pre-commit configuration exists.
- **change_type:** create_file
- **rationale:** Catches style / type / schema issues before they reach CI.
- **implementation_steps:** Configure ruff (lint + format), mypy, and the new schema-validation check as pre-commit hooks.
- **verification_commands:** `pre-commit run --all-files`.

### Task SDLC-033
- **id:** SDLC-033
- **priority:** low
- **target_paths:** `PLANS.md`
- **anchor_guidance:** Specifies `src/sdlc_assessor/` layout and a `pipeline/run_single.py` module that don't exist.
- **change_type:** update_docs
- **rationale:** `documentation_truthfulness`. The plan and the code have drifted.
- **implementation_steps:** Update §Final project structure to reflect actual flat `sdlc_assessor/` layout and the fact that `run` is inlined in `cli.py`. Note the decision to inline.
- **verification_commands:** Manual review.

### Task SDLC-034
- **id:** SDLC-034
- **priority:** low
- **target_paths:** Repo rename
- **anchor_guidance:** Repo is named `SDLC-assesment` (typo).
- **change_type:** update_docs
- **rationale:** Search-discoverability and professionalism.
- **implementation_steps:** Rename to `sdlc-assessor`. GitHub auto-redirects old URL. Update any internal docs that reference the old name.
- **verification_commands:** `curl -sI https://github.com/calabamatex/SDLC-assesment` returns 301 redirect after rename.

### Task SDLC-035
- **id:** SDLC-035
- **priority:** low
- **target_paths:** `sdlc_assessor/__init__.py`, `pyproject.toml`
- **anchor_guidance:** No `__version__` exposed.
- **change_type:** modify_symbol
- **rationale:** Consumers importing the package cannot programmatically check version.
- **implementation_steps:** Add `__version__ = "0.1.0"` to `sdlc_assessor/__init__.py`. Bump in `pyproject.toml` in sync. Add a test asserting they match.
- **verification_commands:** `python -c "import sdlc_assessor; print(sdlc_assessor.__version__)"`.

---

## Phase 8 — Beyond v1 (suggested, not required for v1.0.0)

- **Language packs:** Go, Rust, Java, C#, Kotlin. Each needs its own detector pack and parser strategy. Roughly 1–2 tasks per language for a minimal pack, more for production quality.
- **Real SAST integration:** offload to `semgrep`, `bandit`, `eslint`, `ruff`, `cargo-audit`. Cache results. Emit their findings into the common schema instead of reinventing them.
- **Dependency graph:** pull `requirements.txt`, `package-lock.json`, `Cargo.lock` into an inventory.dependency_graph object. Feed into a real `dependency_release_hygiene` category.
- **Git history detectors:** commit signing, co-author coverage, bus-factor, CODEOWNERS coverage, force-push incidents (from reflog where available).
- **Comparison mode:** `sdlc compare repo_a repo_b --use-case vc_diligence`. PLANS.md §Deferred already marks this as post-v1.
- **HTML renderer:** PLANS.md §Deferred.
- **Remote profile distribution:** signed profile packs.
- **LLM-backed narrative generation:** Use the Anthropic API (already embedded in the subject's workflow) to generate category narratives from findings. Keeping deterministic path as default.

---

## Quick-start execution contract for the agent

```bash
# Sanity before starting
git checkout -b remediation-phase-1
pip install -e ".[dev]"  # will fail until SDLC-002 is applied

# Per task:
#   1. Read the task block
#   2. Apply implementation_steps
#   3. Run verification_commands
#   4. git add -p && git commit -m "<conventional commit>" 
#   5. Only move on if verification commands exit 0

# After each phase:
pytest -q
python scripts/benchmark_calibration.py > /tmp/bench_after_phase_N.json
python scripts/calibration_check.py  # once SDLC-026 lands

# Before merging:
ruff check .
mypy sdlc_assessor/
pytest -q --cov=sdlc_assessor --cov-report=term-missing
```

## Expected score delta (for the tool assessing itself, after all phases)

Using the tool as an acquisition-diligence pass on `library` + `production` maturity:

- Phase 1 complete: +15–20 points (tests pass, README present, license, CI)
- Phases 2–3 complete: +10–15 points (schema conformance, declared-but-unused flags honored)
- Phases 4–5 complete: +10–15 points (detectors correct, renderer complete)
- Phase 6 complete: net effect on this repo's own score likely mild — the calibration changes affect *other* repos more than this one — but surfaces remaining work accurately
- Phase 7 complete: +5 polish points

**Expected v1.0.0 self-score under `acquisition_diligence + production + library`: 75–85**, depending on whether all suggested Phase 8 items (semgrep integration, dep graph) land.

Anything above 90 after Phase 7 should be treated as a calibration warning sign, not a success — the tool should not rate itself a distinction until the Phase 8 substantive detectors land.
