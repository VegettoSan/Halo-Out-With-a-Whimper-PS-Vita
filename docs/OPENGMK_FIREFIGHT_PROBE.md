# E015 — original Firefight arena on PC

**Follow-up:** [E016](OPENGMK_NATIVE_PROBE.md) now verifies full-process restart persistence for EVA helmet/Elite character using the same E015 runtime. Audio remains partial (underrun notifications recur); no new audio or INI patch was made. The historical E015 observations/limitations below are retained.

**2026-11-23 UTC. Result: basic gameplay PASS, complete compatibility audit PARTIAL.** The original first arena (Site 117) loads and can be played through OpenGMK without editing EXE, GMK, GML or recovered assets. The owner supplied live keyboard/mouse input while the agent observed the game and collected process/audio diagnostics. Persistence after a full restart remains UNTESTED because physical Escape stopped computer control during the live trial.

## What actually worked

| System | Evidence and assessment |
| --- | --- |
| Arena load | VERIFIED visible original Site 117 arena, original class selection, HUD, scenery and gameplay. Normal and Easy were entered. |
| Movement / jump | VERIFIED by owner live test; movement/camera displacement observed. Early agent key attempts were often rejected during concurrent owner input and are not counted as successful inputs. |
| Aim / weapon fire | VERIFIED owner input, visible projectiles/muzzle flashes and ammo consumption (e.g. 292 → 228 during Easy). No synthetic GML or scripted gameplay replacement. |
| Enemies | VERIFIED spawn, movement, hostile projectiles, vehicles and combat activity. Full AI/parity against the proprietary runner is UNTESTED. |
| Collisions / damage | VERIFIED by owner test for ground/wall collisions and jumping; agent observed damage overlay/shield changes, death and respawn in Normal. Collision-mask parity is UNTESTED. |
| Pause / resume | VERIFIED Escape pause, frozen scene, generated `pause.sav`, Resume returning to combat. HUD elapsed time can include paused wall time; no timing-parity claim. |
| Return route | VERIFIED pause Exit → original postgame report; owner subsequently opened Armory. No runtime panic along that route. |
| Audio | Signal VERIFIED using the runtime PID's Core Audio session meter; owner heard music/UI sounds with cuts initially, then reported cuts no longer noticeable during later gameplay. Intermittent issue remains PARTIAL, not a proven audio fix. |
| Customization | Initial helmet cycling and incorrect default colors diagnosed; runtime INI adapter makes original startup defaults visible, giving a stable default helmet and expected colors. No sprite/frame override. |
| Persistence after restart | UNTESTED. The corrected INI exists with game-generated settings before close; that is not a restart test. |

## Reuse, isolation and commands

The first run reused E013's runtime, SHA-256 `02de3629b99b4382030fb2484b8e950be617c5b524643f0ecc976e84a87407a2`. Fresh copied EXEs retain SHA-256 `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f`; original music is copied alongside them. The original ZIP/EXE/music and recovered GMK were hash-checked again and remain unchanged. No new extraction occurred.

Isolation is by fresh working directory, process-local TEMP/TMP/APPDATA/LOCALAPPDATA/USERPROFILE and private logs, **not a VM**. The new launcher samples Windows process memory every 0.5 seconds and records PID, input/runtime hashes and exit status. It never injects player input or modifies game data.

```powershell
python tools/opengmk/run_pc_probe.py --runtime build/mp/i686-pc-windows-msvc/release/gm8emulator.exe --game-dir recovered/arena-probe-20261122/run-1 --report-dir reports/local/arena-probe-20261122/run-1 --temp-dir recovered/arena-probe-20261122/temp-1
build/arena-probe-20261122/audio_session_meter.exe 8652 5
```

The meter is original diagnostic source compiled with the existing MSVC/Windows SDK, not a new dependency. It reads only matching process audio sessions and does not record other apps or change volume. A nonzero meter proves a signal, not audible fidelity; see the [Core Audio meter definition](https://learn.microsoft.com/en-us/windows/win32/coreaudio/peak-meters).

## Concrete runtime correction: INI write visibility

**VERIFIED source/artifact findings:** the game writes startup profile values, checks file existence and reopens the profile without calling `ini_close`. Previous OpenGMK held writes in memory until explicit close and did not create the file. With no visible profile, original globals remained at zero; the preview requests selection-minus-one, so zero becomes animated subframe -1. Selecting a real helmet through Armory made the preview stable even in the old runtime, discriminating this from a sprite-atlas extraction failure.

**INFERRED classic-runner behavior:** the EXE imports `WritePrivateProfileStringA` and `GetPrivateProfileStringA`. A private native Windows reference test confirmed that the write creates a visible file and an immediate read returns the value without a close call; [Microsoft documents creation on write](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-writeprivateprofilestringa). This supports the compatibility adapter but is not a trace of the original runner's exact implementation.

`patches/opengmk/0002-classic-ini-write-through.patch` persists `ini_write_string` and `ini_write_real` while retaining the active INI data. It does not fake `file_exists`, force a helmet value or change GML. **VERIFIED corrected run:** the original startup creates its INI with the expected default selection; the preview is stable and colored, and the owner reports normal appearance/gameplay. Compatibility of every other INI edge case is UNTESTED.

A new working source copy retains OpenGMK base `9e4282e6d19f4dd00961811840ddc3e11da6dd5a` plus the prior modal patch. The existing Cargo cache was copied to a separate `udon-work` for diagnostics; the cache, earlier source and runtime were preserved. No downloads/reinstalls. The Cargo patch changes only udon/libsoundio-sys from pinned git source `1ae3cdce620acdaa7996315c05a98a0f12ed8745` to matching local copies; no package-version updates.

Build: `cargo build --offline --release --target i686-pc-windows-msvc -p gm8emulator --manifest-path local-tools/arena-probe-20261122/OpenGMK-work/Cargo.toml`, via private existing-toolchain setup. First build failed on Rust's explicit-reference requirement in newly added diagnostic code; references were corrected and the next build passed in 1m22s. Runtime SHA-256 `5d8f24087ad253952910964a967cccf9a4ad9939769c202ee859629cf0253f6e` (5,344,768 bytes). Cargo.lock SHA-256 `a1c7ea1fe3601e66c4c182dcf0702d82c4eda5c1c28101cd6b8c63b8524107e0`.

## Audio: measured, not declared fixed

`0003-udon-audio-diagnostics.patch` adds opt-in underrun counts and callback CPU-duration maxima. It adds a diagnostic latency request; **the tested WASAPI3 backend returned 22 ms for both requested 10 and 80 ms**, so that knob did not demonstrate a buffer-size correction. Callback time is not game frame time.

- Reference run 2: 109 cumulative underrun notifications, maximum reported callback duration 326 microseconds.
- Run 3's captured snapshot: one cumulative notification over 968 memory samples (about eight minutes), callback maximum 3,259 microseconds. Owner reports audio no longer noticeably cutting. Different live workloads mean this is not a controlled proof of an audio fix or speed improvement.
- A possible stale writable-count branch was investigated, **not patched speculatively**. `audio_recovery_probe.rs` deliberately stalls its producer for 120 ms. It continued generating samples afterward: PASS.
- A stronger test suspends only that audio-only fixture for 200 ms, never the game. It provoked one underrun, then sample generation rose from 259,776 to 547,776: PASS, exit 0. Thus a persistent unrecoverable-starvation hypothesis was not demonstrated.

Exact controlled-test command:

```powershell
python tools/opengmk/check_audio_recovery.py --probe build/ap/i686-pc-windows-msvc/release/examples/audio_recovery_probe.exe --report-dir reports/local/arena-probe-20261122/audio-fault-before
```

This leaves the first intermittent audio report open for a reproducible stress/load test. Default audio latency remains the original 10-ms request. No silence stub, constant success return, codec replacement or rewritten audio gameplay logic was introduced.

## Memory and measurement limits

| Run | Process peak working set | Maximum sampled private bytes | Scope |
| --- | ---: | ---: | --- |
| 1, E013 runtime | 269,475,840 B (~257 MiB) | 201,584,640 B (~192 MiB) | Menu, Normal arena, deaths, pause/report/Armory; exited 0 |
| 2, INI + audio diagnostics | 270,225,408 B (~258 MiB) | 201,056,256 B (~192 MiB) | Short audio reference; exited 0 |
| 3, INI + audio diagnostics | 250,900,480 B (~239 MiB) | 191,336,448 B (~182 MiB) | Snapshot during manual Easy gameplay; process still open at evidence capture |

These are Windows process counters. Working-set trimming by the included helper, differing scenarios, GPU allocations and sampling affect interpretation. They do not establish Vita RAM fit, a memory optimization or displayed FPS. **Reliable game frame times/displayed FPS were not measured.** No VPK or Vita-device test exists.

## Private evidence and next gate

`reports/local/arena-probe-20261122/` retains per-run logs, memory samples, audio readings, both build attempts, native INI reference, audio-recovery results, source/binary hashes, owner observations and local screenshots. No proprietary screenshot, INI/save, recovered GML or binary is committed. Physical Escape ended CUA; no further input or forced game closure followed. The launcher can capture exit when the owner closes the game.

**Assessment INFERRED:** this is a credible initial PC gameplay base for planning the native OpenGMK backend. It does not establish full original-runner fidelity or ARM/Vita portability. No WinVita renderer work was performed. Next high-information test: close/restart the corrected runtime with a UI-selected profile and verify that selection persists, then repeat a short audio stress test if cuts return. This session does not mark the native Vita phase complete or package a VPK.
