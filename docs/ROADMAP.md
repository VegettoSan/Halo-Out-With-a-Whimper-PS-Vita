# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | PARTIAL: E020 useful graphics retained; E021 38-instruction original startup + persistent INI on physical Vita, blocked at sound_replace before Draw. Native input/audio/original menu incomplete; full exit gate NOT MET |
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
E021 resolves the priority boundary using reviewed original failure semantics and implements real confined file/INI services. PC and Vita reach 38 instructions and stop at Audio/sound_replace; native profile persisted and was independently retrieved. Next: prove actual ARM MP3 decoding/handle registration and correct Deferred/None ownership, then resume original startup. Keep E020 renderer; view/state/rectangles/gradients/text/blend/presentation and input/audio still gate the menu. No partial-init draw, gameplay FPS or full-game memory fit is established. See [E021](OPENGMK_STARTUP_SERVICES_PROBE.md).
