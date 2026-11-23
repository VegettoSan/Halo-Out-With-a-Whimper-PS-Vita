# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery PASS; modified OpenGMK real PC menu/interaction PASS; WinVita loader PASS only; exact vendor patch and PC combat fidelity remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | NOT STARTED |
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
Continue P1: run one original Firefight arena on PC and record movement, a weapon interaction, enemy spawning, audio and the first failure if any. The missing-dialog experiment now passes with a real original menu and interaction (ADR-002, E014). Route B remains the research priority; P2 has not started. No phase advancement to native Vita is implied by a Windows PC menu.
