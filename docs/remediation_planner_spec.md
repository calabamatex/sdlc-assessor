# Remediation Planner Specification

## Purpose

The remediation planner converts scored findings into an implementation plan suitable for execution by an AI coding assistant or engineer.

The output should be patch-safe, sequenced, and testable.

## Core rule

Do not rely on exact line numbers as the primary anchor. Use stable instructions:

- exact file path
- exact symbol name where possible
- anchor text or search pattern
- before snippet
- after snippet
- required tests
- verification command

Line numbers may be included as hints, but they are secondary.

## Inputs

1. Evidence object
2. Scored findings
3. Hard blockers
4. Use-case profile
5. Repository archetype
6. Maturity profile

## Output structure

### 1. Phase summary
Each phase should include:
- phase number
- title
- purpose
- dependency notes
- expected score lift
- hard blocker closure impact

### 2. Task list
Each task must include:
- task id
- priority
- finding ids addressed
- exact file path(s)
- exact symbol(s) if known
- anchor text
- change type
- rationale
- implementation instructions
- minimum test requirements
- verification command
- rollback note if relevant

### 3. Execution summary
Provide:
- phase count
- task count
- estimated effort
- new test count
- blocker closure count
- expected score delta

### 4. Verification checklist
A shell-oriented checklist that confirms the work.

## Change types

Allowed change types:
- create_file
- modify_symbol
- modify_block
- add_tests
- add_workflow
- update_docs
- remove_artifact
- tighten_validation
- replace_unsafe_pattern

## Task template

### Task
- Task ID: SEC-01
- Priority: High
- Finding IDs: [F-SEC-004, F-SEC-009]
- File paths:
  - `src/cli/runCommand.ts`
  - `tests/cli/runCommand.test.ts`
- Symbols:
  - `runCommand`
- Anchor text:
  - `exec(userInput)`
- Change type:
  - replace_unsafe_pattern
- Rationale:
  User-controlled command execution is present. The function interpolates external input into shell execution.
- Implementation instructions:
  1. Replace shell-string execution with argument-array execution.
  2. Introduce input allowlist validation before execution.
  3. Return structured errors for rejected commands.
- Before snippet:
  ```ts
  exec(`tool ${userInput}`)
  ```
- After snippet:
  ```ts
  execFile("tool", [validatedInput])
  ```
- Minimum tests:
  - reject invalid argument
  - allow safe argument
  - preserve expected success path
- Verification command:
  `npm test -- runCommand`
- Rollback note:
  If external dependency behavior differs, revert only the argument-array conversion and keep input validation layer.

## Planning rules

1. Order phases by dependency.
   Example:
   - foundational utilities
   - validation and error types
   - risky call-site migration
   - test expansion
   - CI hardening
   - docs update

2. Close hard blockers early.
3. Group related changes when they share a utility or validation layer.
4. Include tests for every safety-critical modification.
5. Prefer targeted fixes before broad refactors unless architecture is the blocker.
6. Estimate effort conservatively.

## Effort model

Suggested bands:
- XS: under 1 hour
- S: 1 to 3 hours
- M: 3 to 6 hours
- L: 6 to 12 hours
- XL: 12 plus hours

## Expected score lift model

The planner should estimate score lift in bounded language:
- likely +2 to +4
- likely +5 to +8
- likely blocker closure with limited score lift
- likely confidence improvement more than raw score improvement

## Verification checklist rules

The final checklist should include:
- tests
- lint or static analysis
- build
- security check if relevant
- docs validation if docs changed
- CI dry-run equivalent if feasible

## Output quality rules

The planner must avoid:
- "update as appropriate"
- "refactor for cleanliness"
- "improve tests"
- unspecified file targets
- vague remediation without a verification command

Every task should be executable without requiring the implementer to infer the missing objective.
