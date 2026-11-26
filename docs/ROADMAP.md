# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | MINIMUM PROOF PASS: original VM/frames, animated menu, character selection, native input/music and first room6 image on physical Vita with repeatable logs; parity/stability remain P3/P4 work |
| P3 | Functional parity | Real menu and one Firefight arena; controls, audio and persistent state if present, with regression evidence | PARTIAL: menu/customization/native audio and first arena image; sustained arena play blocked. E029 general debug/pool/cull corrections await device test |
| P4 | Performance and release review | Measured device frametimes/memory, stability, correctness and distribution-rights review | NOT STARTED |

## Principles
- Keep original source inputs untouched and local; project recovery and public end-user packaging are separate concerns.
- No empty VPK or mock arena counts as gameplay progress.
- Do not fabricate completed phases, FPS or partial completion of decompilation.
- 960x544 and 30 FPS are design targets, not measurements.
- A failed experiment stays FAIL or BLOCKED in docs/EXPERIMENTS.md.
- Owner selects an unused title ID before any VPK packaging and separately approves public distribution.

## Next milestone

E028 character selection works on Vita and room6 presents its first original image before stopping at debug output. Room16 reaches its Draw but exhausts the temporary vertex pool. E029/00.30 supplies real debug logging, conservative clip rejection across all rooms and a measured1MiB temporary pool, retaining64MiB CDRAM+32MiB mapped-main atlas caps. PC/ARM checks pass and VPK transfer is verified; retrieve both native runs, verify original room Step/Draw/input and pool metrics, then resolve the next actual general service. No map-specific bypass, stable Firefight or60FPS claim. Preserve original30Hz simulation. [Evidence](OPENGMK_RUNTIME_PROGRESS.md); [pending plan](ACTIVE_PLAN.md).
