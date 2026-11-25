# Roadmap — evidence gates, not a promise of deliverables

| Phase | Goal | Minimum exit evidence | Current status |
| --- | --- | --- | --- |
| P0 | Archive/PE audit, baseline, tools | Hash+CRC, safe input layout, static PE features | COMPLETE: E001–E003; original hashes preserved, local tools inventoried |
| P1 | Recover/evaluate runtime approaches | Exact runner identification, extraction attempt, Win32/import cost and an A/B decision supported by tests | ADVANCED/PARTIAL: recovery, PC menu/basic arena and E016 restart profile persistence PASS; exact vendor patch/full fidelity and intermittent audio remain open |
| P2 | Native Vita proof of concept | True execution of recovered/original game logic, useful graphics, basic input and repeatable logs | PARTIAL: E020 original VM prefix + authentic engine-resource graphics on physical Vita 1000, persistent GPU/memory/timing evidence; startup, input/audio and original-menu execution remain BLOCKED; full exit gate NOT MET |
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
E020 adds an initial libvita2d/GXM `RendererTrait` backend to the same Game/atlas path and renders the authentic logo on Vita 1000. Owner observation, installed binary, GPU readback, a single cached 16 MiB page, released CPU payloads and bounded timing agree. Native startup remains at E019's 15-instruction Process stop. Next: verify the original priority failure/void contract and its honest native representation, then resume unchanged startup. File/save, window/input/audio, view/primitive/text/blend coverage and working-set residency gate the original menu. No gameplay, displayed FPS or full-game memory fit is established. See [E020](OPENGMK_GRAPHICS_PROBE.md).
