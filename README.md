# Halo: Out With a Whimper — PS Vita (research port)

> **Native menu diagnostic verified on physical Vita 1000.** E025 runs the original animated menu with right-stick/X navigation and audible native music, confirmed by the owner. Original VM, events, resources and 30 Hz room timing are preserved. E026 verifies full-screen mapping and active-scene clears; level entry now requests a fifth atlas beyond the prior64MiB limit. E027 tests bounded main-RAM overflow textures. Playable Firefight and complete compatibility remain unverified. Private HOWAW1178 builds only; no game files are distributed here. [Measurements and pending work](docs/OPENGMK_RUNTIME_PROGRESS.md).

This repository documents research toward a native PlayStation Vita adaptation of the Windows *Halo: Out With a Whimper — Firefight Demo*. **Primary goal: reuse the original executable/data/game logic wherever technically possible, not recreate the game from scratch.**

## Verified input facts

An owner-supplied `HOWaW_FirefightDemov1.zip` was inspected *statically* (not executed).
- ZIP SHA-256: `423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62`
- Contains `HOWaW_FirefightDemov1.exe` (18,142,424 bytes, PE32 Intel x86; SHA-256 `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f`) and `Music/menu.mp3`.
- Nine PE sections; ~16.13 MB of trailing data (overlay). Contains classic GameMaker-related strings and `D3DX8.dll` marker.
- **GameMaker 8.0 format is verified** by loading signatures, version header and strict recovery; exact vendor patch/build remains unknown. No original editor project is included in the ZIP.
- Recovered existing entries: 693 sprites, 128 sounds, 181 scripts, 233 objects, 845 object events and 15 rooms. Runtime-only dialog/INI adaptations now support the real PC menu and basic original Site 117 gameplay with unchanged game data. Full fidelity and Vita compatibility remain unproven; see [E015](docs/OPENGMK_FIREFIGHT_PROBE.md).

See [technical audit](docs/TECHNICAL_AUDIT.md) for evidence and uncertainty.

## Paths under evaluation

1. **x86 EXE translation + Win32 / DirectX adaptation:** investigate feasibility using [D2Vita](https://github.com/Franckrst/D2Vita) as a *reference*, not a drop-in solution.
2. **Recover GameMaker data/GML and use a compatible runtime:** study [GM8Decompiler](https://github.com/OpenGMK/GM8Decompiler) and [OpenGMK](https://github.com/OpenGMK/OpenGMK); confirm exact runner version first.
3. **Static x86-to-ARM recompilation:** expensive fallback, to be justified by evidence.

**Route B is currently best supported by PC arena and native menu evidence; full-game Vita compatibility is still unproven.** The Vita ARMv7 processor cannot directly launch a Windows x86 EXE.

## Start with Codex (Plus / Sol 6.1 high)

1. Clone this repository.
2. Put a legitimately obtained copy of `HOWaW_FirefightDemov1.zip` in local `original/` (Git-ignored, never upload).
3. Run `python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip`.
4. Ask Codex: **"Read AGENTS.md, then execute docs/CODEX_FIRST_TASK.md. Record verified results and do not build an empty VPK."**

## Project documents

- [AGENTS.md](AGENTS.md): mandatory Codex rules, scope, preservation, efficiency, reporting.
- [docs/CODEX_FIRST_TASK.md](docs/CODEX_FIRST_TASK.md): first bounded technical session.
- [docs/PORTING_STRATEGY.md](docs/PORTING_STRATEGY.md): alternatives and evidence needed.
- [docs/ROADMAP.md](docs/ROADMAP.md): phase objectives and exit tests.
- [docs/TECHNICAL_AUDIT.md](docs/TECHNICAL_AUDIT.md): facts, hashes and unknowns.
- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md): research log.
- [docs/TOOLS.md](docs/TOOLS.md): local tool inventory and external references.
- [docs/OPENGMK_NATIVE_PROBE.md](docs/OPENGMK_NATIVE_PROBE.md): E016 persistence, real ARM build evidence, memory estimates and native adapter plan.
- [docs/OPENGMK_VM_PROBE.md](docs/OPENGMK_VM_PROBE.md): E017 original compiler/VM, explicit native service boundaries and reproducible startup test.
- [docs/OPENGMK_CLEANMEM_PROBE.md](docs/OPENGMK_CLEANMEM_PROBE.md): E018 audited helper contract, real human dialog, PC/ARM evidence and next native-service gate.
- [docs/OPENGMK_PRIORITY_PROBE.md](docs/OPENGMK_PRIORITY_PROBE.md): E019 process/thread priority, persistent diagnostics and first physical Vita VM execution.
- [docs/OPENGMK_GRAPHICS_PROBE.md](docs/OPENGMK_GRAPHICS_PROBE.md): E020 native renderer, authentic-resource hardware test, memory/batching measurements and original-menu integration gates.
- [docs/OPENGMK_STARTUP_SERVICES_PROBE.md](docs/OPENGMK_STARTUP_SERVICES_PROBE.md): E021 verified priority failure contract, persistent PC/Vita INI services and exact Game Start audio gate.
- [docs/OPENGMK_MP3_PROBE.md](docs/OPENGMK_MP3_PROBE.md): E022 existing-codec reuse, real PC/Vita MP3 replacement, memory/ownership proof and original Draw/depth-clear gate.
- [docs/ASSET_POLICY.md](docs/ASSET_POLICY.md): files never to upload.
- [config/port_identity.json](config/port_identity.json): title ID unassigned.

## Local layout

```text
original/          # game ZIP/EXE (ignored)
recovered/         # unpacked data / decompiled code (ignored)
local-tools/       # third-party tool binaries (ignored)
reports/local/     # private full logs (ignored)
build/             # generated binaries/VPK (ignored)
vita/              # eventual original Vita adapter source
tools/             # shareable audit scripts
docs/              # public, sanitized evidence and plans
```

This independent fan research is not affiliated with Microsoft, Halo's rights holders, or the original fangame creators. No proprietary game files are hosted here. Distribution of a playable port requires a separate rights review.
