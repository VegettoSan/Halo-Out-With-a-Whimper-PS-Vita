# Active work — autonomous continuation from E023

Keep only current work here; historical evidence belongs in EXPERIMENTS.md.

- [x] E024 code/PC: input audit, real Ctrl/Touch bindings and pressed/held/released mapper; CPU contract PASS, ARM build PASS. Physical sampling/analog transitions and >180 original frames PASS; splash/fade seen by owner. Touch/button navigation still pending.
- [x] E024: normal Game::frame/Step/Draw flow runs on Vita; next actual gate Audio/sound_loop(140).
- [ ] Verify original animated menu and navigation on hardware when a concrete build exists; record partial coverage explicitly.
- [ ] Implement required graphics operations from actual traces; retain the E020–E023 backend and atlas budget.
- [ ] E025: native output implementation + reuse of original mixer/WAV/resampler/MP3; CPU PCM/mixer/stop/concurrent-log contract PASS. ARM/hardware pending. Buffer routine telemetry; preserve durable panic/exit/checkpoints to address measured log stalls.
- [ ] Follow original menu/map/difficulty flow toward Site 117; resolve measured room/file/render/input/audio blockers.
- [ ] Measure frame times, memory, residency and cleanup; add recoverable texture eviction only if requested pages exceed budget.

Current verified baseline: E023 Game::init + original object Draw + one presented frame; next Window/poll_events before Game::frame. No functional game VPK, complete visible menu, native controls or audio output yet. HOWAW1178; direct main; previous builds preserved.
