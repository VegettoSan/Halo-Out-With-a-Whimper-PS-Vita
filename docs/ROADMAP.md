# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | PARTIAL: E025 original animated menu, normal frames, right-stick/X navigation and audible native music PASS on Vita. Full controls/stability and arena remain pending; complete exit gate NOT MET |
| P3 | Functional parity | Real menu and one Firefight arena; controls, audio and persistent state if present, with regression evidence | PARTIAL: native menu/navigation/music; PC basic arena previously tested, native arena still blocked |
| P4 | Performance and release review | Measured device frametimes/memory, stability, correctness and distribution-rights review | NOT STARTED |

## Principles
- Keep original source inputs untouched and local; project recovery and public end-user packaging are separate concerns.
- No empty VPK or mock arena counts as gameplay progress.
- Do not fabricate completed phases, FPS or partial completion of decompilation.
- 960x544 and 30 FPS are design targets, not measurements.
- A failed experiment stays FAIL or BLOCKED in docs/EXPERIMENTS.md.
- Owner selects an unused title ID before any VPK packaging and separately approves public distribution.

## Next milestone

E025's original menu is visible, animated and navigable on physical Vita, with audible native music and real Step/Draw timing. E026 tests the actual active-scene color/depth clear required by the first room transition, full physical display mapping and camera translation. Retrieve that log, then fix its next actual service or residency limit before claiming a rendered arena. Preserve original30 Hz simulation; measure complete-frame distributions before selecting performance work. Touch, all options/controls, suspend/resume, full-game fit and playable Firefight remain open. [Compact evidence](OPENGMK_RUNTIME_PROGRESS.md); [current pending plan](ACTIVE_PLAN.md).
