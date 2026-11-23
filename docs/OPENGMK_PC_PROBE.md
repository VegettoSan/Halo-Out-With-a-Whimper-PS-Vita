# OpenGMK PC menu probe — 2026-11-23 UTC

**VERIFIED:** the original, unchanged HOWaW EXE reaches its real main menu in the modified Windows runtime. Firefight, map selection and difficulty selection respond to real input. This is a PC compatibility result, not a Vita build or gameplay-parity claim. See E011–E014 in [EXPERIMENTS.md](EXPERIMENTS.md).

## Reproducible inputs

- Official [OpenGMK source](https://github.com/OpenGMK/OpenGMK), commit `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`. A pristine clone and a separate working clone remain under ignored `local-tools/menu-probe-20261122/`. No prior tool checkout was edited.
- Cargo.lock unchanged: SHA-256 `8a10301053ade07fb5991594b4108024da5c21fb16843c61e59708a31e3428b1`.
- Windows NT 10.0.26200, Rust `1.100.0 (0ef1bc386 2026-11-09)`, Cargo `1.100.0 (3acc79c0c 2026-11-05)`, MSVC tools `14.50.35717`, target `i686-pc-windows-msvc`.
- EXE SHA-256 `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f`; original menu.mp3 supplied beside the copied EXE in `Music/`. No recovered GMK, scripts or resources are edited or recompiled.

MSVC, Windows SDK, CMake and Ninja were already installed. Only missing Rust components, source and Cargo dependencies were obtained. Rust/Cargo homes live inside the ignored checkout tree, installed with `--no-modify-path --profile minimal`; no system PATH setting was changed. `+stable` overrides upstream's 1.77 toolchain pin for this recorded host build; Windows 7 support was not tested.

## Apply the bounded runtime change

In a fresh source **copy** at that commit, apply `patches/opengmk/0001-show-message-ext.patch`, then copy `tools/opengmk/message_dialog.rs` into `gm8emulator/src/game/platform/message_dialog.rs`. `git apply --check` against the pristine source passed. The patch only integrates this Windows backend into the GML builtin; it contains no game GML or proprietary assets. Upstream runtime licensing still applies to its source/integration; no project-wide license or publication authorization is added here.

The backend uses [DialogBoxIndirectParamW](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-dialogboxindirectparamw), a synchronous modal dialog with a disabled owner and its own Windows message loop. The game does not step while the call is waiting. Custom control IDs 101/102/103 map to results 1/2/3, keeping IDCANCEL distinct from the second button. Escape and close map to 0. Empty button slots are omitted without renumbering remaining slots. Creation failures propagate as errors rather than invented choices.

After dismissal the runtime drains owner events and clears keyboard/mouse state using existing input methods, preventing dialog input from carrying into game logic. Text is decoded using the runtime's game encoding; `#` produces a line break. Native Windows layout is used. Exact original message styling, extreme text sizes, held-input edge cases and non-Windows backends remain UNTESTED.

## Build and controlled test

Use an existing x86 MSVC developer environment; add existing CMake/Ninja to the **process** PATH. Point RUSTUP_HOME/CARGO_HOME at the private installation and CARGO_TARGET_DIR at `build/mp`. Set `CMAKE_GENERATOR=Ninja`. No system changes are needed.

```powershell
rustc +stable --edition 2021 --target i686-pc-windows-msvc tools/opengmk/dialog_probe.rs -o build/menu-probe-20261122/dialog_probe.exe
cargo +stable build --locked --release --target i686-pc-windows-msvc -p gm8emulator --manifest-path local-tools/menu-probe-20261122/OpenGMK-work/Cargo.toml
```

Local environment setup and exact executed commands are in ignored `local-tools/menu-probe-20261122/build.cmd` and `reports/local/menu-probe-20261122/commands.txt`. The initial MSBuild-based build failed in libsoundio's CMake compiler check with FTK1011 tracking-file path errors. Switching to existing Ninja and a shorter new build directory succeeded; the failed build and logs were retained.

Before running the game, the standalone dialog probe displayed actual Alpha/Beta/Gamma controls. CUA mouse/keyboard actions produced **1, 2, 3 and Escape=0** in sequence. Each call stayed pending until dismissal; the same byte-identical backend was used in the runtime. The third choice was exercised by Tab/Enter. This tests the actual UI/return path without game files or hard-coded answers.

## Actual game trial

Exact child command: `gm8emulator.exe HOWaW_FirefightDemov1.exe -s`, working directory `recovered/menu-probe-20261122/run-1/`; TEMP/TMP redirected to fresh `recovered/menu-probe-20261122/temp-1/`. The private Python launcher captures PID, start/end UTC, stdout/stderr and exit code. It suppresses only a console window, leaving the game's interactive windows available.

Observed sequence: original three-button priority dialog → logo/title prompt → welcome → first-run player configuration → Save Changes → **main menu (Firefight / Forge / Armory / Exit)** → Firefight map selector → difficulty selector. Actual game-dialog selection was not instrumented; the controlled probe independently established all four returns. Keyboard and mouse interactions worked in the observed route. Alt+F4 closed the runtime with **exit code 0**. No further runtime error was observed.

Private evidence: `reports/local/menu-probe-20261122/{dialog-interactive-stdout.txt,runtime-build-1.txt,runtime-build-2.txt,game-1-stdout.txt,game-1-stderr.txt,game-1-exit.json,input-audit.json}` and `main-menu.png`, `firefight-selector.png`, `difficulty-selector.png`. Screenshots contain proprietary game art and remain ignored; do not upload them.

Modified runtime SHA-256: `02de3629b99b4382030fb2484b8e950be617c5b524643f0ecc976e84a87407a2` (5,335,552 bytes). Controlled-probe binary SHA-256: `3b4132ccd0512884c27ba8ea211fe4d5ec4a859e80af86e06abe6b2de9a92d2c`. Binaries stay under ignored build paths. Source checkout, lockfile and binary identity distinguish this build from the older packaged 0.2.0 used in E007.

## Limits and next experiment

Combat, collisions, enemy behavior, weapon handling, audio output, save persistence after restart and long-run stability remain UNTESTED. There is no measured Vita performance and **no functional VPK**. WinVita remains an alternative; no D3D8 renderer work was performed.

Next high-information experiment: launch one original Firefight arena on PC and record movement, a weapon interaction, enemy spawning, audio and any first failure, using the same immutable EXE and a fresh run directory. Keep fixes in the runtime, preserving original GML.
