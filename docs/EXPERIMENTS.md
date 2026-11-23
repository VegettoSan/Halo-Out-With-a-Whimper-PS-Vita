# Experiments and findings

Record **every meaningful attempt, including failures**. Do not mark a test PASS on the basis of a plan or apparent compatibility.

## E000 — Initial static archive / PE audit

- **Date:** 2026-11-22 UTC (date of owner-supplied inspection)
- **Input:** HOWaW_FirefightDemov1.zip, SHA-256 `423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62`.
- **Method:** Python ZIP/PE static read; header/section/marker analysis, no game execution.
- **Expected:** determine architecture and basic archive integrity.
- **Observed:** CRC pass, PE32 x86, nine PE sections, GameMaker-related marker strings; no separate source project.
- **Result:** PASS for static format identification only. Exact runner build/compatibility: UNTESTED.
- **Evidence:** docs/TECHNICAL_AUDIT.md and reproducible tools/inspect_input.py.
- **Next:** identify exact GameMaker runner version and verify extractor compatibility.

## Template (copy for E001+)

```markdown
### E001 — <one hypothesis>
- Date (UTC):
- Input hashes:
- Environment/tool version:
- Exact command/config:
- Hypothesis and PASS/FAIL rule:
- Observed outcome:
- Result: PASS / FAIL / BLOCKED
- Sanitized evidence:
- What changed / what's still unknown:
- Next discriminating test:
```
