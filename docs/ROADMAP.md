# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | MINIMUM PROOF PASS: original VM/frames, animated menu, character selection, native input/music and first room6 image on physical Vita with repeatable logs; parity/stability remain P3/P4 work |
| P3 | Functional parity | Real menu and one Firefight arena; controls, audio and persistent state if present, with regression evidence | PARTIAL: menu/customization/native audio and first arena image; E030 first gameplay/movement/shader PASS; enemy-fire line-width stops. E031 family/timing implementation awaits hardware combat |
| P4 | Performance and release review | Measured device frametimes/memory, stability, correctness and distribution-rights review | NOT STARTED |

## Principles
- Keep original source inputs untouched and local; project recovery and public end-user packaging are separate concerns.
- No empty VPK or mock arena counts as gameplay progress.
- Do not fabricate completed phases, FPS or partial completion of decompilation.
- 960x544 and 30 FPS are design targets, not measurements.
- A failed experiment stays FAIL or BLOCKED in docs/EXPERIMENTS.md.
- Owner selects an unused title ID before any VPK packaging and separately approves public distribution.

## Next milestone

E029 original rooms6/16 render and advance countdowns with real input/music. General culling/debug/pool fixes pass hardware; both next stop at per_vertex_tint. E030 native corner-color shader and initial gameplay/movement PASS; next enemy-fire line-width stop. E031/00.32 general line/circle family and separated GPU/display timings pass eleven geometry/service/PC/ARM checks and transfer verification. Retrieve native combat logs, verify shapes and choose performance work from actual timing; synchronized reads/dynamic textures remain explicit next families, without map-specific bypasses. Measured room windows~50ms exceed30Hz budget; split VM CPU/GPU/display costs before claiming performance. Preserve original30Hz logic; sustained play/60FPS remain unverified. [Evidence and graphics audit](OPENGMK_RUNTIME_PROGRESS.md); [pending plan](ACTIVE_PLAN.md).
