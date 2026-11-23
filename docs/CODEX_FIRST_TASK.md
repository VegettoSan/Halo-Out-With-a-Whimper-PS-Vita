# Codex task 01 — high-information Phase P0/P1 probe

**Target:** Sol 6.1, high thinking, Plus session. Read `AGENTS.md` first and obey repository rules. This is a **research + evidence task, not a VPK task**.

Owner's private input will be at `original/HOWaW_FirefightDemov1.zip`. Do not upload it to GitHub.

## Objective
Determine which approach gives maximum actual reuse of the original game: (A) Win32/x86 executable translation like D2Vita, (B) recover GameMaker GML/game data and use compatible native runtime like OpenGMK, or (C) static x86->ARM recompilation. Do not preselect a path.

## Work sequence
1. Inventory repository and previously installed local tools. Read audit and strategy. Verify baseline with `python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip`. Stop and document if owner ZIP differs. Keep originals immutable.
2. On a private copy, identify the **exact GameMaker runner version** with supporting binary signatures, offsets/imports or other credible evidence. Do not claim 'GameMaker 8' merely from strings.
3. Inspect Windows imports, PE overlay and real dependency candidates (Win32, D3D8, DirectDraw, DirectSound etc). Record actual findings, not presumed API usage.
4. Choose and attempt one compatible decompiler or extraction method. Validate outputs by inventorying objects, rooms, scripts, events, sprites, sounds, fonts; if extraction fails, record exact failure and test only one well-motivated fallback.
5. Evaluate A's loader/API feasibility via minimal static or isolated proof, and B's recovered game/runner compatibility. Compare resource fidelity, engineering cost, license constraints, CPU/memory implications.
6. If justified, implement a **small reproducible genuine interaction proof** (not a fake loading screen). No series of speculative VPKs. Do not claim real Vita performance from PC/editor results.
7. Update docs/TECHNICAL_AUDIT.md, docs/EXPERIMENTS.md, docs/PORTING_STRATEGY.md, docs/DECISIONS.md and docs/ROADMAP.md with concise evidence, PASS/FAIL/BLOCKED and next decision. Commit only shareable files after reviewing staged diff.

## Execution efficiency
- Reuse local tools; download only missing required dependencies from trusted sources.
- Prioritize one discriminating test per hypothesis; stop if blocked and name the blocking API/format.
- Avoid token-heavy loops, unrelated refactors and deleting backups.
- Keep raw dumps, recovered GML, original game assets and binaries inside ignored local folders.

## Final report
Give verified counts/findings, exact command, failed hypotheses, selected/favored approach *only if justified*, updated paths, what works in PC versus Vita (or is untested), and **one next actionable experiment**. State explicitly if no VPK or recovered gameplay exists.
