# Active work — autonomous continuation from E023

Keep only current work here; historical evidence belongs in EXPERIMENTS.md.

- [ ] E024: audit original input requirements; real Vita controller sampling and held/pressed/released mapping, CPU contracts.
- [ ] Run unchanged Game::frame with the existing event order and clock/pacing; follow actual errors, preserve diagnostics.
- [ ] Verify original animated menu and navigation on hardware when a concrete build exists; record partial coverage explicitly.
- [ ] Implement required graphics operations from actual traces; retain the E020–E023 backend and atlas budget.
- [ ] E025: real native audio output using the existing player/decoder; validate streaming ownership, volume/loop/stop and errors independently where possible.
- [ ] Follow original menu/map/difficulty flow toward Site 117; resolve measured room/file/render/input/audio blockers.
- [ ] Measure frame times, memory, residency and cleanup; add recoverable texture eviction only if requested pages exceed budget.

Current verified baseline: E023 Game::init + original object Draw + one presented frame; next Window/poll_events before Game::frame. No functional game VPK, complete visible menu, native controls or audio output yet. HOWAW1178; direct main; previous builds preserved.
