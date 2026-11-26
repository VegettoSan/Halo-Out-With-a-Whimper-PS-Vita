# Active work — autonomous continuation from E023

Keep only current work here; historical evidence belongs in EXPERIMENTS.md.

- [x] E024 code/PC: input audit, real Ctrl/Touch bindings and pressed/held/released mapper; CPU contract PASS, ARM build PASS. Physical sampling/analog transitions and >180 original frames PASS; splash/fade seen by owner. Touch/button navigation still pending.
- [x] E024: normal Game::frame/Step/Draw flow runs on Vita; next actual gate Audio/sound_loop(140).
- [x] E025: original animated menu + right-stick/X navigation and music heard on Vita. Partial options/control coverage; touch still unverified.
- [ ] Implement required graphics operations from actual traces; retain the E020–E023 backend and atlas budget.
- [x] E025: native music/SFX output with original mixer/players; CPU contracts, ARM/desktop and Vita output/cleanup PASS. Routine telemetry buffered, error checkpoints durable.
- [x] E026: real level selection reaches room loading; fix active-scene color clear, full-display mapping and camera translation. CPU/ARM/Vita clear and full-display PASS. Next atlas page2 exceeds existing64MiB cap; room6 not rendered yet.
- [ ] E027: bounded32MiB GPU-mapped main-RAM overflow, retaining64MiB CDRAM; PC contracts/ARM PASS,00.28 transferred. Measure actual level/customization path, full frame-window distributions, pool residency and cleanup; no speculative eviction.

Current verified baseline: E025 original animated menu, right-stick/X navigation and audible music on physical Vita; normal frames execute. E026 level entry passes active color clear and stops at fifth atlas request. Customization failure separately owner-reported, trace pending. Functional private menu diagnostic exists; playable Firefight remains unverified. HOWAW1178; direct main; previous builds preserved.

Owner preference: fill the physical display in E026. 60fps requested; original room simulation30Hz verified. Preserve Step/Draw semantics; do not claim60 through duplicate frames or silently speed up GML.
