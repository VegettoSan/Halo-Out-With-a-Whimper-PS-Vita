# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | MINIMUM PROOF PASS: original VM/frames, animated menu, character selection, native input/music and first room6 image on physical Vita with repeatable logs; parity/stability remain P3/P4 work |
| P3 | Functional parity | Real menu and one Firefight arena; controls, audio and persistent state if present, with regression evidence | PARTIAL: menu/customization/native audio and initial original gameplay PASS; E032 physical baseline/optimized each2700frames/exit0 with real combat/input/audio; former diagnostic cap corrected. Stable full arena/parity still incomplete |
| P4 | Performance and release review | Measured device frametimes/memory, stability, correctness and distribution-rights review | STARTED: native full-window CPU/GPU-wait/display comparison and bounded stability PASS; collision bottleneck and30Hz budget FAIL, release review incomplete |

## Principles
- Keep original source inputs untouched and local; project recovery and public end-user packaging are separate concerns.
- No empty VPK or mock arena counts as gameplay progress.
- Do not fabricate completed phases, FPS or partial completion of decompilation.
- 960x544 and 30 FPS are design targets, not measurements.
- A failed experiment stays FAIL or BLOCKED in docs/EXPERIMENTS.md.
- Owner selects an unused title ID before any VPK packaging and separately approves public distribution.

## Next milestone

E032 baseline/optimized same-binary physical comparison completed:2700 original frames/exit0 both, former cumulative cap removed, queue wait~38µs optimized, no audio/native-memory failure. Early arena~50→43.6ms p50; heavy combat~100ms remains outside30Hz budget and collision helpers/GML dominate. E033 cached-box candidate PC/ARM/differential contracts pass; not included in installed00.33 and no second VPK generated. Next measure per-method collision mix/rejection rate and native probe overhead, then select the next faithful measured optimization. Preserve dynamic state/event order, original30Hz VM and all AI/collisions/resources. [Full evidence/protocol](OPENGMK_PERFORMANCE_PROBE.md); [pending plan](ACTIVE_PLAN.md).
