# E022 — real MP3 replacement, native decode and original Draw entry

**2026-11-25 UTC / 2026-11-24 America/Bogota. VERIFIED:** `sound_replace(140, Music/menu.mp3, 3, true)` succeeds after actual decoding and valid asset registration on PC and physical Vita 1000. The unchanged original VM reaches **`Game::draw`**, with **76 instructions for a new profile / 65 for the existing profile**. Native execution then stops explicitly at **Graphics/clear_zbuf**, before object Draw events or a displayed menu. **Audio output remains unimplemented; no playback is claimed.** Private **HOWAW1178 / 00.23** installed SELF, log, input hashes and cleanup verified. No functional/playable game VPK exists.

## Contract and implementation

The [original GM8 manual](https://documentation.help/Game-Maker-8/409_02_sounds.html) describes replacement of an existing sound, freeing the old resource and returning whether replacement succeeded; kind 3 selects multimedia playback and preload requests loading into memory. OpenGMK's existing implementation returns 0 on file/decode failure and 1 on successful replacement, but includes a non-None branch documented only against a GM8.1 bug. Applying that branch to E021's **Deferred** assets would clear pending data and invent success without decoding.

E022 uses the original argument conversion/arity validation. It reads the actual MP3, constructs and validates a real player, then assigns `FileType::Mp3` to the existing slot, preserving its identity/name and updating requested kind/preload metadata. **Deferred, None and an existing Mp3 are handled explicitly.** Missing files, unsupported formats and invalid streams return 0; nonexistent IDs/invalid arity remain errors. A failed candidate does not become a valid handle. Successful replacement drops the previous owned resource. **INFERRED defensive failure policy:** retain the old asset until a candidate is valid; exact vendor failure-side ownership is not established by the manual or this test. No x86 original runner startup or original GML/resource edit was required.

Registration represents decoded/validated media ready for the player, **not a started output stream or physical audio-memory upload**. All unimplemented playback/volume/output operations remain explicit service stops. No sound is marked playing, no native sink/mixer is fabricated, and no silence generator substitutes for the game audio. An actual playback request has not yet been reached in this startup prefix.

## Reuse and memory ownership

- Reuse OpenGMK's pinned `game/audio/mp3.rs` and cached **rmp3 0.3.1 / minimp3**. Preserve its first-frame sample-rate policy, channel-change filtering, length scan, refill/reset and sample delivery. No new codec was written.
- Copy only udon's pure `Source` interface/types into the ignored build tree, removing its unused constants-module declaration. Do not pull in udon's unconditional **libsoundio** dependency or desktop session/mixer. Target dependency tree contains rmp3, libc **0.2.185** and build-time cc **1.2.60**; no udon/libsoundio native frontend. Cargo.lock unchanged; all dependencies already cached.
- Scalar minimp3 float output is selected for this native path; desktop explicitly retains its prior SIMD feature. Windows-hosted cc-rs invokes the existing hard-float WSL GCC linker wrapper as its compiler, plus the authored shell-free WSL ar wrapper. No SDK/cache source modification, download or install.
- Two bounded player ownership fixes: zero-initialize the existing PCM scratch allocation; store encoded bytes as `Arc<Box<[u8]>>` to share the original allocation without a full compressed-buffer copy. Box the player inside the handle so its decoder state does not inflate every unrelated Sound enum value. Clones share encoded storage, with independent player state as upstream.
- Retain **1,293,667 compressed bytes**, one **9,216-byte PCM frame buffer**, decoder state/metadata; validation uses another temporary 9,216-byte output array. **28,523,520 bytes of full-song float PCM are not retained.** This does not claim the entire decoder consumes only 9 KiB.

The inherited constructor scans/decode-counts the stream, and the diagnostic validation then drains the actual player once to verify finite output/counts and signal statistics before resetting it. This deliberate two-pass proof costs startup time; it is not a final load-latency target. Combining validation with the inherited scan is a future optimization, not a measured improvement in E022.

## Actual original startup and first graphical gate

The first PC discovery decoded/registered the original sound and reached an unconditional `get_pixels` in `load_room`, even with **no FFmpeg recorder**. That readback was consumed only inside the later recorder check. The patch narrows the existing outer condition to an active recorder; real recording retains its original readback/write path. No fabricated pixels are returned, no room/GML step is skipped, and recording itself is not newly tested.

The normal `load_room` path now calls the original `Game::draw`. Host mode returns a structured **Graphics/native_frame_begin** error because GXM is unavailable; no software/mock frame is accepted as rendering. Native mode starts the real existing libvita2d scene and accepts the actual full-frame, unrotated **640×325** view. The minimal E020 extension records aspect-fit mapping to 960×544: scale **1.5**, offset **(0,28.25)**. Other view configurations remain explicit unsupported operations. Coordinate math is tested; visible sprite scaling/pixel parity under this new mapping is **UNTESTED**.

The original room then requires **`clear_zbuf` while preserving colour**. That operation is still unimplemented. Its existing fallible call site returns an explicit Graphics error instead of claiming a clear or aborting through an unsupported void trait method. It does not proceed into original object Draw events. Error cleanup ends the unpresented scene, waits for GPU completion and releases resources; it does not swap/present an incomplete frame. No manual Draw follows failed initialization, and no fictitious menu or repeated logo fixture runs.

## Measured PC and physical Vita result

| Measurement | PC / Vita evidence |
| --- | --- |
| Original MP3 SHA-256 | Both `e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0` |
| Input / channels / sample rate | **1,293,667 B / 2 / 44,100 Hz** |
| Samples per channel / interleaved PCM samples | **3,565,440 / 7,130,880** |
| Signal summary | Both **7,129,724 nonzero samples**, peak **1.0173236**, RMS **0.15675603246370387**; matching summaries do not prove bitwise PCM identity |
| Decode/validation interval | PC **145,353 µs** in the validated fresh-profile run; Vita **6,845,926 µs**, including the two-pass proof |
| VM progress | PC fresh **76 instructions / 28 calls**; PC restart and Vita existing profile **65 / 17** |
| Original Draw | Entered via `Game::init` → `load_room` → `Game::draw`; no forced call after an error |
| Native GXM/view | Init rc=0; actual visible view `(0,0,640,325) → (0,0,640,325)`, angle 0; aspect mapping logged |
| Native result | `clear_zbuf: SERVICE_UNAVAILABLE/Graphics`, cleanup `Ok(())`, **exit 2** |

Owner reported a black screen for a while, then closure. Retrieved/validated **2026-11-25 03:10:40 UTC**: log SHA-256 `1edfea65e21127b470137a621f8e1a3296f1e9eb52376b3f31ecc861ddf5d382`, installed SFO HOWAW1178/00.23 and SELF match. No panic/allocation-failure marker. The initial wait contains **6.846 seconds of real decode validation**; the black screen is not evidence that the menu rendered. Firmware unreported; same owner Vita 1000 as prior tests. The existing E021 INI is byte-identical after exit; its original branch explains the shorter instruction count.

| Native memory/timing boundary | Measured value |
| --- | --- |
| Requested Rust heap during decode / at graphics stop | **96,276,382 / 95,334,326 B** |
| Lifetime requested Rust peak / exit live | **108,104,996 / 1,130 B**; peak remains in original reader preparation |
| System free user before GXM → after init → exit | **124,780,544 → 115,343,360 → 124,780,544 B** |
| System free CDRAM before → after init → exit | **117,440,512 → 94,371,840 → 117,440,512 B**; 22 MiB init delta |
| Free physical-contiguous memory | **27,262,976 B**, queries rc=0 |
| GPU textures / page uploads / sprite submissions / presented frames | **0 / 0 / 0 / 0**; GXM fixed buffers are separate |
| Startup interval through the real stop | **9,260,294 µs**, including decoder, file/diagnostic I/O and GXM initialization; not FPS |

The compressed handle logs its last shared owner being released. GXM resources return to the recorded free-memory baseline after ending the unpresented scene. This supports **one-launch cleanup**, not extended stability or whole-game fit. Rust request counters exclude C/stack/allocator/GPU overhead; system pools are not additive budgets. All 3,003 texture entries / 71,602,980 CPU pixel bytes remain pending, with no six-page GPU residency attempt.

## Exact tools, tests and failures

Same offline Rust/Cargo **1.100.0**, Python **3.14.4**, x86 MSVC toolset **14.50.35717**, WSL hard-float VitaSDK GCC **15.2.0** as E021. Use fresh output/run directories and its explicit private homes/scalar/no-LTO/no-strip/WSL-linker environment. Set ARM `CC_armv7_sony_vita_newlibeabihf` to the existing GCC wrapper and `AR_armv7_sony_vita_newlibeabihf` to a private `.cmd` invoking `tools/opengmk/vita_wsl_ar.py`; retain `HOWAW_GRAPHICS_LIB_DIR` from E020. Exact wrappers, C flags/output and dependency tree are preserved privately.

```powershell
python tools/opengmk/prepare_mp3_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/mp3-final-20261124/OpenGMK --udon-source local-tools/menu-probe-20261122/cargo/git/checkouts/udon-0ad808fdc3b6d4f6/1ae3cdc/src/source.rs
cargo build --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --bin mp3-contract-probe --manifest-path local-tools/mp3-final-20261124/OpenGMK/Cargo.toml
build/mp322-tested-host/mp3-contract-probe.exe COPIED_IGNORED_EXE
python tools/opengmk/run_vm_probe.py --runtime build/mp322-tested-host/howaw-vm-probe.exe --input-dir recovered/native-probe-20261123/pc-profile --run-name NEW --experiment mp3-20261124 --owner-dialog-high --native-priority-contract --expected-service Graphics --expected-operation native_frame_begin --require-persistent --diagnostic-prefix e022
cargo check --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --lib --manifest-path local-tools/mp3-final-20261124/OpenGMK/Cargo.toml
cargo build --offline --locked --release -Z build-std=std,panic_abort --target armv7-sony-vita-newlibeabihf -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --manifest-path local-tools/mp3-final-20261124/OpenGMK/Cargo.toml
```

**PASS:** independent registry contract (no original VM instructions) covers invalid arity/ID, missing/invalid MP3, Deferred/None/Mp3 success, old-handle retention on failure, shared encoded ownership and release. Only new viewport math test run (**1/1**, old tests filtered). VM/source reuse **22/22**, existing player matches only the declared portability/ownership patch, fresh preparation **200/200 identical**, Cargo.lock unchanged. Default desktop check **30.47s**; first real ARM decoder/VM build **1m29s**, ELF32 ARM EABI5 hard-float/Thumb-2, VELF PASS. No old logo, arena or priority fixture repeated.

**Failures/discoveries retained:** initial host compile failed on a missing `audio` namespace, corrected qualified path; next build PASS **36.62s**. Discovery reached missing `get_pixels` (76 instructions) instead of its expected audio-loop stop. After the unused-readback correction, host reached native frame initialization and stopped rather than emulating GXM. A host validation overlapped linking and caused Windows executable replacement **FAIL / access denied**; compilation/execution were separated and completed binaries copied before testing. Final registry/Draw build **37.67s**, frame-guard revision **37.67s**, final bin-only layout build **4.08s**. Expected host/native differences are documented, not presented as full host graphics validation.

Private package: SDK `vita-elf-create INPUT.elf OUTPUT.velf`; packager `--prepare --experiment E022 --elf INPUT.elf --velf OUTPUT.velf --output build/mp322-device`, then `--package --experiment E022 --output build/mp322-device --title-id HOWAW1178 --app-version 00.23`. **Only SELF/SFO**, CRC and remote/installed identity verified, no game data embedded. ELF **4,771,180 B**, SHA-256 `a4c4d2535642b30a7affc4712e57d88e3d457b1613aff9177bf11523808da7f6`; VELF **5,629,838 B**, `b73343578b20e00b076b14836f0e312496d3518a92340827f966c02f787855ee`; VPK **2,312,622 B**, `f0863469ab21b1771712c93f6617b803678da2e59ea092c8db313698b4fac51a`; installed SELF `65f7e47fdc1a0a1101793868aa5787ac0ebc6950c4e4e5f7d02ad91027ec7088`.

Evidence: ignored `reports/local/mp3-20261124/` build attempts, decoder contracts, startup captures, dependencies, source/ownership audits, package/FTP and device log/SELF/SFO/profile; source copies under `local-tools/mp3*-20261124/`, private builds `build/mp322-*`. ZIP/EXE/MP3/GMK/GML and E015/E021 artifacts remain unchanged. **New recovery zero**; previous 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms preserved.

**Result:** PASS real PC/ARM MP3 decode and valid replacement; PASS original engine Draw entry and bounded cleanup; BLOCKED depth-only clear, subsequent original menu object drawing and native audio output. Route B with the reused OpenGMK player/VM and E020 libvita2d/GXM backend remains best supported. **Next one high-information experiment:** implement a real GXM depth-only clear that preserves colour, verify that invariant, and resume this same original Draw to its next actual operation. Do not claim a presented menu or audible audio until independently observed.
