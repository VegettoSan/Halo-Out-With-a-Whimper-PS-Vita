# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | MINIMUM PROOF PASS: original VM/frames, animated menu, character selection, native input/music and first room6 image on physical Vita with repeatable logs; parity/stability remain P3/P4 work |
| P3 | Functional parity | Real menu and one Firefight arena; controls, audio and persistent state if present, with regression evidence | PARTIAL: menu/customization/native audio and initial original gameplay PASS; E031 native combat lines execute, then cumulative diagnostic cap stops. E032 watchdog/profiling/renderer changes PC/ARM PASS; physical sustained-play comparison pending |
| P4 | Performance and release review | Measured device frametimes/memory, stability, correctness and distribution-rights review | STARTED: native sparse CPU/GPU/display baseline, CPU geometry allocation reduction and full profiler; sustained native budget and release review incomplete |

## Principles
- Keep original source inputs untouched and local; project recovery and public end-user packaging are separate concerns.
- No empty VPK or mock arena counts as gameplay progress.
- Do not fabricate completed phases, FPS or partial completion of decompilation.
- 960x544 and 30 FPS are design targets, not measurements.
- A failed experiment stays FAIL or BLOCKED in docs/EXPERIMENTS.md.
- Owner selects an unused title ID before any VPK packaging and separately approves public distribution.

## Next milestone

Retrieve E032/00.33 baseline log with installed SELF/SFO; archive only the owned baseline diagnostic flag and repeat the same character/room6 route in optimized mode using the same installed binary. Compare full60-frame low/high-object windows and measured GML/renderer/collision/native waits before selecting further changes. E031 physical closure is the cumulative diagnostic cap; E032 per-frame watchdog replacement and renderer optimizations are PC/ARM verified, native correctness/performance pending. Preserve original30Hz simulation and all AI/collisions/events. Pixel reads/dynamic textures and arbitrary graphics states remain explicit boundaries. [Diagnosis, measurements and protocol](OPENGMK_PERFORMANCE_PROBE.md); [pending plan](ACTIVE_PLAN.md).
