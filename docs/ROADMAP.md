# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | PARTIAL: E023 original Draw/Game::init and one real presented frame PASS on Vita; next Window/poll_events before Game::frame. Complete visible menu, native input/audio output and gameplay incomplete; exit gate NOT MET |
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

E023's actual GXM depth/color/occlusion proof passes, and original menu objects Draw and Game::init complete at 105 instructions. One authentic first frame is presented, but its 112 nonblack pixels do not establish a complete visible menu. Next implement actual Vita input/event polling with an explicit control mapping, then execute the unchanged Game::frame with normal pacing to advance the original fade and discover its next real service. Do not skip the pump, fake input/audio, or repeat only Draw in place of Step. Native audio output, text/gradient/outline branch coverage, pixel parity, suspend/resume and full-game memory fit remain open. [E023](OPENGMK_DRAW_PROBE.md).
