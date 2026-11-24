# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | FEASIBILITY STARTED: E018 existing compiler/VM + service adapter ARM ELF/VELF PASS; PC original startup passes the human priority dialog and stops at Process service; native frontend/device execution BLOCKED/UNTESTED; exit gate NOT MET |
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
E018 validates CleanMem's actual contract and real Windows OS effects; Vita explicitly reports the helper's failure value for unsupported Windows working-set operations. Original PC startup reaches 15 VM instructions after the owner's real dialog response, then stops at `set_program_priority`. Next: implement and measure that service through the existing boundary, without adopting upstream's no-op or assuming a Vita process/thread equivalence. P1 audio/full parity and P2 graphics/input/device evidence remain open; no VPK or title ID is assigned. See [ADR-006](DECISIONS.md) and [E018 evidence and hardware diagnostic plan](OPENGMK_CLEANMEM_PROBE.md).
