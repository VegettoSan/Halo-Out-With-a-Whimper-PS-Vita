# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | FEASIBILITY STARTED: E016 real reader/parser ARM ELF/VELF PASS; complete VM, native frontend and device execution BLOCKED/UNTESTED; exit gate NOT MET |
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
E016 closes PC persistence for the UI-selected helmet/character; audio continuity and full parity remain P1 gaps. Route B remains the priority (ADR-004). Next: separate the existing compiler/VM's host services sufficiently to compile original scripts/events and execute real startup to its modal request, measuring the first unsupported service and heap peak. Reader/parser compilation and ELF/VELF conversion have passed; do not repeat them without a new change or claim the P2 exit gate met. Attach native graphics/input/audio to that original-logic path before packaging; no empty VPK, assigned title ID or device performance claim.
