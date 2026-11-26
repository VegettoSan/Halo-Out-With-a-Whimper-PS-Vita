# Active work — autonomous continuation from E023

Keep only current work here; historical evidence belongs in EXPERIMENTS.md.

- [x] E024 code/PC: input audit, real Ctrl/Touch bindings and pressed/held/released mapper; CPU contract PASS, ARM build PASS. Physical sampling/analog transitions and >180 original frames PASS; splash/fade seen by owner. Touch/button navigation still pending.
- [x] E024: normal Game::frame/Step/Draw flow runs on Vita; next actual gate Audio/sound_loop(140).
- [x] E025: original animated menu + right-stick/X navigation and music heard on Vita. Partial options/control coverage; touch still unverified.
- [ ] Implement required graphics operations from actual traces; retain the E020–E023 backend and atlas budget.
- [x] E025: native music/SFX output with original mixer/players; CPU contracts, ARM/desktop and Vita output/cleanup PASS. Routine telemetry buffered, error checkpoints durable.
- [ ] E026: real level selection reaches room loading; fix active-scene color clear, full-display mapping and camera translation. CPU contracts/ARM PASS; 00.27 transferred and device test pending. Continue to next actual level blocker.
- [ ] Measure frame times, memory, residency and cleanup; add recoverable texture eviction only if requested pages exceed budget.

Current verified baseline: E025 original animated menu, right-stick/X navigation and audible music on physical Vita; normal frames execute. Level entry stops at active-scene color clear. Functional private menu diagnostic exists; playable Firefight remains unverified. HOWAW1178; direct main; previous builds preserved.

Owner preference: fill the physical display in E026. 60fps requested; original room simulation30Hz verified. Preserve Step/Draw semantics; do not claim60 through duplicate frames or silently speed up GML.
