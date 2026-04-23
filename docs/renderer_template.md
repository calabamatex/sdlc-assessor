# Human-Readable Report Template

Use this template for the primary report output. The output may be rendered as Markdown or HTML, but the structure should remain stable.

---

## 1. Header

- Project name
- Repository URL
- Analysis date
- Default branch
- Head commit
- Analysis mode
- Use-case profile
- Maturity profile
- Repository archetype
- Dominant language(s)

## 2. Executive Summary

Write 2 to 4 short paragraphs covering:
- what the repo appears to be
- whether the repo is credible relative to its claims
- where the main strengths are
- where the highest risks are
- whether the final verdict is stable or confidence-limited

## 3. Overall Score and Verdict

Display:
- overall score
- applicable max score
- verdict
- score confidence

Recommended verdict badges:
- Pass with distinction
- Pass
- Conditional pass
- Fail

## 4. Repo Classification Box

Include:
- repository archetype
- maturity profile
- deployment surface
- release surface
- classification confidence

## 5. Quantitative Inventory

Display a compact stats row or table:
- source files
- source LOC
- test files
- estimated test cases
- test-to-source ratio
- workflow files
- workflow jobs
- runtime dependencies
- dev dependencies
- commit count
- tag count
- release count

## 6. Top Strengths

List 3 to 5 strengths.
Each strength must cite evidence:
- file path
- line range or exact count
- why it matters

## 7. Top Risks

List 3 to 5 risks.
Each risk must include:
- severity
- short title
- why it matters
- evidence
- likely impact

## 8. Hard Blockers

If none exist, explicitly state that no hard blockers were triggered.

If blockers exist, display:
- blocker title
- severity
- why it is a blocker
- evidence refs
- what would close it

## 9. Category Scoring Matrix

For each category show:
- category name
- applicability
- score
- max score
- short summary
- strongest supporting evidence
- major deductions

Recommended columns:
| Category | Applicable | Score | Max | Summary | Major evidence |

## 10. Detailed Findings by Category

Group findings under each category.

Per finding include:
- severity
- statement
- evidence bullets
- confidence
- rationale

Order:
- critical
- high
- medium
- low
- info

## 11. Evidence Appendix

Provide:
- complete evidence references
- counts by detector
- proxy-based findings explicitly labeled as approximate

## 12. Optional Comparison Section

Only in comparison mode:
- side-by-side overall score
- normalized category matrix
- relative strengths
- adoption opportunities
- confidence caveats

## 13. Optional Remediation Appendix

Only in remediation mode:
- phase summary
- prioritized tasks
- expected score lift
- verification checklist

---

## Writing rules

1. Human-readable first.
2. Do not lead with raw JSON.
3. Do not inflate strengths without evidence.
4. Use explicit statements rather than vague praise.
5. Distinguish between missing evidence and evidence of absence.
6. If the repo purpose is unclear, say so explicitly.
7. If a major judgment relies on proxy metrics, say so explicitly.
