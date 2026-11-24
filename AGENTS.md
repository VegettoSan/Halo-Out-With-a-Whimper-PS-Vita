# Mandatory rules for Codex and contributors — HOWaW PS Vita

**Scope: entire repository.** Read README, docs/TECHNICAL_AUDIT.md, docs/PORTING_STRATEGY.md, docs/ROADMAP.md, docs/EXPERIMENTS.md, docs/TOOLS.md, then docs/CODEX_FIRST_TASK.md or the current owner task.

## Goal
- Prioritize reuse of original Halo: Out With a Whimper Firefight EXE, GameMaker game data and GML logic. **Do not rewrite mechanics from scratch** unless measured evidence rules out reuse and the owner authorizes the scope change.
- Evaluate (A) x86 PE/Win32 translation, (B) GameMaker data/GML recovery plus compatible Vita runtime, and (C) static recompilation. None is established as compatible. Avoid premature architecture decisions.
- Prefer native VitaSDK if viable; avoid requiring Mono, IL2CPP or mandatory kernel plugins by default.
- Preserve original gameplay, objects, rooms, sprite animation, collisions, enemies, weapons, input behavior, audio, timing and menus as far as technical evidence allows.
- Do not import game assets or proprietary components from other VegettoSan projects.

## Strict preservation and privacy
- Never delete, overwrite, edit in place, normalize or relocate original ZIP, EXE, music, extracted resources, recovered GML, backups, toolchains or other repositories. Work from copies.
- Operate inside this checkout. Read external local tools only when necessary; don't modify external projects or machine/system settings without explicit approval.
- Keep game files in ignored local original/, recovered/, private/, local-tools/; keep private logs in reports/local/ and builds in build/.
- NEVER commit original EXE/ZIP/MP3, decompiled GML, recovered sprites/sounds, protected code, proprietary SDKs, signing secrets, private paths, third-party binaries or unlicensed VPKs. Inspect staged files before each commit; never use git add -f on ignored data.
- This repository is currently PUBLIC. Treat all GitHub commits, issues, pull requests and CI artifacts as publicly visible. Sanitize logs and examples.
- No public game or asset distribution without rights review and owner approval.

## Evidence discipline
- Mark each claim VERIFIED (direct artifact/test), INFERRED (reasoned but not proven), or UNTESTED (not checked). A matching PE marker is not proof of GameMaker runner version, resource recovery or game compatibility.
- Every experiment must list UTC date, input SHA-256, exact tool version and command, environment, hypothesis, measured result, PASS/FAIL/BLOCKED, evidence link/path and next discriminating test in docs/EXPERIMENTS.md.
- Compilation success != boot; boot != menus; menus != gameplay; emulator != physical Vita; CPU frame completion != displayed FPS.
- Limit noisy diagnostic output and avoid speculative performance claims. Initial 960x544 and 30 FPS are DESIGN TARGETS, not achieved metrics.
- Never falsify results, fabricate VPK success or silently remove an unsuccessful experiment.

## Efficient Codex Plus / Sol 6.1 high workflow
1. Read existing repo and inventory local tools before downloading or installing anything. Internet only when resolving a specific missing fact, dependency or incompatibility.
2. For each major hypothesis, choose a small, low-cost experiment with clear PASS/FAIL criteria; stop repeating the same failed action without new evidence.
3. Prefer static PE analysis first. Before running unknown downloaded tools or legacy game binaries, evaluate trust and use an isolated environment if appropriate.
4. Make minimal reversible patches with focused commits. Do not bulk delete older builds, backups, originals or unrelated work. Work directly on `main`; do not create branches unless the owner explicitly requests one.
5. Do not build a new VPK unless a concrete executable prototype and diagnostic goal justify a device test.
6. Avoid multiple repetitive build cycles and token-heavy exploratory rewriting. Summarize findings concisely and reuse documented evidence.
7. Advance technical phases only when evidence satisfies docs/ROADMAP.md; the owner explicitly approves publication, licensing, destructive actions and scope changes.
8. Confirm the local ignored ZIP hash before decompilation. A different build is a different baseline; record rather than silently replace.

## PS Vita specifics
- Vita is ARMv7, while provided EXE is PE32 x86. Running it requires translation/adaptation; copying EXE into VPK is not enough.
- Document input mapping, display scaling, renderer (especially possible D3D8), audio, memory, frame pacing, suspend/resume and save paths when a prototype exists.
- Owner selected `HOWAW1178` for the E019 private diagnostic. Do not reuse an ID from Hungry Shark or HaloCEVita. Any different packaging identity requires owner selection.
- For the current diagnostic the owner explicitly selected automatic High/button 3 (`--owner-dialog-high`). Preserve/log this specific policy; do not call it manual UI or use it to fake other unavailable services. Keep the prior manual/first-device evidence.
- Test on physical Vita for real device conclusions; record environment and measurements. Reuse prior Vita projects only as technical references with license review.

## End-of-session summary (required)
Report: verified facts; files changed; exact tests and outcomes; recovered resource counts (or zero/not attempted); blockers; best supported architectural choice or remaining uncertainty; next one high-information experiment. Explicitly state when no functional VPK exists.
