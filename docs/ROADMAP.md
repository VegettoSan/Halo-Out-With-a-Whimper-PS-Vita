# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | PARTIAL: E022 original MP3 decode/registration and Game::draw entry on physical Vita, blocked at clear_zbuf before object Draw/presentation. E020 useful graphics reused; native input/audio output/menu incomplete; exit gate NOT MET |
| P3 | Functional parity | Real menu and one Firefight arena; controls, audio and persistent state if present, with regression evidence | NOT STARTED |
| P4 | Performance and release review | Measured device frametimes/memory, stability, correctness and distribution-rights review | NOT STARTED |

## Principles
- Keep original source inputs untouched and local; project recovery and public end-user packaging are separate concerns.
- No empty VPK or mock arena counts as gameplay progress.
- Do not fabricate completed phases, FPS or partial completion of decompilation.
- 960x544 and 30 FPS are design targets, not measurements.
- A failed experiment stays FAIL or BLOCKED in docs/EXPERIMENTS.md.
- Owner selects an unused title ID before any VPK packaging and separately approves public distribution.

## Next milestone
E022 resolves MP3 replacement with actual PC/Vita decode and asset ownership, reaching original Game::draw at 76 new-profile / 65 existing-profile instructions. Native view setup passes; the next measured operation is a depth-only clear that preserves colour. Implement and verify that clear, then resume the same Draw to its next real request. Object drawing, state/shapes/text/blend/presentation, input and native audio output remain open; no gameplay FPS or full-game memory fit. See [E022](OPENGMK_MP3_PROBE.md).
