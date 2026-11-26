# E023 — depth-only GXM proof and original menu Draw

**2026-11-25–26 UTC. VERIFIED on physical Vita 1000:** depth/color/occlusion test **PASS**; original menu objects' Draw events and **Game::init complete at 105 VM instructions**. The revised private **HOWAW1178 / 00.24** presents the actual frame zero: **10 sprite submissions, one rectangle, five batches**. GPU readback has **112 nonblack pixels**, so a complete visible menu is **not established**. Execution then stops honestly at **Window/poll_events**, before the first Game::frame. Native audio output/input and a functional/playable game VPK remain absent. Packages prepared November 25; final log/installed-binary verification November 26 UTC (November 25 owner timezone).

## Corrected depth contract

E022's adapter stopped too early. The pinned [OpenGMK implementation](https://github.com/OpenGMK/OpenGMK/blob/9e4282e6d19f4dd00961811840ddc3e11da6dd5a/gm8emulator/src/render/opengl.rs#L2265) calls `glClear(DEPTH_BUFFER_BIT)` **only when `using_3d` is true**. Its 2D `set_depth` stores zero and depth testing is masked by that mode. The original menu requests no 3D mode. E023 preserves this guard: its menu call logs `using_3d=false gpu_clear=false`. This is a verified no-op contract, not a claimed GPU clear. Enabling 3D remains unsupported.

The C extension separately implements a genuine depth-only primitive, reusing the installed libvita2d clear shaders with an independently owned fragment patch whose color write mask is NONE. It writes far depth with ALWAYS testing, does not request a stencil clear, restores the supported 2D depth state, checks fallible GXM calls and releases its patches before libvita2d teardown. No shader compiler, vitaGL, codec download or SDK modification. [Library lifecycle/shader interface](https://github.com/xerpi/libvita2d/blob/master/libvita2d/source/vita2d.c).

The **32×32 offscreen** test never presents a fixture. It writes near depth/red color; a farther green fragment must fail. After a synchronized readback, the depth-only clear must preserve every color byte and change all 1,024 raw depth words. Finally the same farther green fragment must pass. Force-store/load preserves depth between the three scenes. Physical result: **1,024/1,024 in each check, rc=0, four actual GXM draws, 11,928 / 11,862 µs including waits in the first/revised runs**. This proves the tested primitive, not full 3D compatibility or GPU-only execution time.

## Original execution and renderer additions

Unchanged `Game::init → load_room → Game::draw → Draw/0` now executes **object 0 / instance 108698** and **object 1 / instance 100002** on Vita. Trace instrumentation changes no event ordering. The first native run actually submits room background tiles, additive and normal blending, original sprites and a filled uniform rectangle. **Text and gradient/outline branches have not yet executed**; no menu reconstruction or forced Draw after failed initialization.

Keep E020's RendererTrait, atlas IDs, lazy page uploads and ordered sprite batching. Add filled/gradient color batches and original kernel rectangle/blend dispatch. Original font/alignment/text routines remain in place and use the engine's existing glyph resources. Unsupported outline/other blend factors still stop explicitly. Adapt libvita2d's ONE/ONE additive preset to GM8's SRC_ALPHA/ONE at fragment-program creation; normal blending remains unchanged. Arbitrary blend modes and exact rasterization parity remain unverified.

The revised backend normalizes vertices into libvita2d's fixed shader domain and uses a real GXM viewport for the full **640×325** original view, aspect-fitted to 960×544 at **1.5**, offset **(0,28.25)**. Clip-space clipping bounds tiled geometry to the view. Presentation accepts only matching logical dimensions and an identity logical scaling policy (Fixed 1, Full or Aspect when framebuffer/window dimensions already match). Subviews, rotated views and resized logical windows remain unavailable. Mapping and rectangle fan/color contracts pass on CPU; revised native viewport and presentation execute successfully. Exact clipping/rasterization parity and fractional-alpha additive pixel fidelity remain unverified.

The observed caption gate is an asynchronous **void request**: [Ramen's contract](https://github.com/viriuwu/ramen/blob/ef715f65981f6c96f7f889258ff43b63cb472626/src/window.rs#L152) explicitly allows the OS to ignore it; the cached Windows implementation discards `SetWindowTextW`'s return. The implemented adapter stores the requested caption and logs `native_titlebar=Unavailable os_title_changed=false`. It does not claim a native titlebar change or general Window capability. CPU request/replacement contract passes; size operations remain unavailable. This permits the unchanged Draw to return and Game::init to complete. Only then does the diagnostic present that original frame; it neither calls Draw after an error nor advances Game::frame without the required input/event service. After a two-second diagnostic display hold, the existing process_window_events boundary stops explicitly. The first package's caption failure (exit 1, zero presented frames) remains preserved. The revised package also exits 1 at its new input gate, with clean resource release.

## MP3 reuse, memory and limits

Validation is now integrated into the existing decoded length scan. Every candidate is still actually decoded; finite/count checks and first-frame channel/rate policies remain. No cached hash is treated as decoding success. A dedicated PC comparison against the real streaming player matches **7,130,880 samples, 7,129,724 nonzero, peak 1.0173236, RMS 0.15675603246370387** and rejects invalid/empty data. No E022 registry fixture repeated.

Native scans: **3,639,780 / 3,630,465 µs**, versus E022's two-pass **6,845,926 µs** (about 47% lower observed interval, not a controlled benchmark). Retain the compressed **1,293,667 B**, bounded **9,216 B** PCM scratch and small scan metadata; no full-song PCM allocation. Audio playback remains unavailable.

| Revised physical run | Measured result |
| --- | --- |
| Prepared CPU pixels | 71,602,980 B / 3,003 entries / six atlas descriptions |
| Resident GPU pages | **Two / 33,554,432 B**, loaded on demand, no duplicate upload |
| CPU pixels released / remaining | **30,513,548 / 41,089,432 B** |
| Rust heap live at frame zero / lifetime peak | **64,845,312 / 108,104,996 B**; peak includes original reader |
| Free CDRAM before / after GXM / two pages | **117,440,512 / 94,371,840 / 60,817,408 B** |
| Free user memory before / after GXM | **124,780,544 / 115,343,360 B**; distinct from Rust live heap |
| Startup / frame-zero presentation | **8,284,578 / 14,187 µs**; presentation includes GPU/display waits, not a gameplay frame benchmark |
| GPU calls | **10 total:** four contract draws, one color clear, five original texture/color batches |
| Original frame zero | **One presented frame**, 2,088,960 readback bytes, 112 nonblack pixels; no complete visible menu or displayed FPS claim |
| Cleanup | Rust heap 1,142 B; system-free user/CDRAM/phycont values restored; retained sound released |
| Revised result | Depth, original Draw, Game::init and presentation **PASS**; input/event pump **BLOCKED**, exit 1 |

Rust allocator requests and OS free-memory counters measure different things; they are not a combined CPU/GPU resident-memory total.

A **64 MiB resident atlas budget** prevents attempting all six 16 MiB pages. Exceeding it remains an explicit failure: recoverable eviction/backing storage is not implemented. Original CPU payloads are freed only after successful upload. Full-game fit, gameplay FPS, native input, suspend/resume and audio output remain unproven.

## Reproduction and evidence

Pinned OpenGMK `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`; cached Ramen `ef715f65981f6c96f7f889258ff43b63cb472626`; rmp3 0.3.1/minimp3; Rust/Cargo 1.100.0, Python 3.14.4, MSVC 14.50.35717, existing WSL hard-float VitaSDK GCC 15.2.0. All offline. Installed libvita2d archive SHA-256 remains `c5857b65ea7a93f6ff37f29abd84ed2fe1d6faca9bcf9a83a60e33e110b69e99`; exact library source commit remains unknown.

```text
python tools/opengmk/prepare_draw_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/draw-present-final-20261124/OpenGMK --udon-source local-tools/arena-probe-20261122/udon-work/src/source.rs
python tools/opengmk/prepare_graphics_native.py --output build/depth23-native-v3
python tools/opengmk/audit_vm_probe.py --source local-tools/menu-probe-20261122/OpenGMK --work local-tools/draw-present-final-20261124/OpenGMK --report reports/local/draw-20261124/reuse-present-final.json
cargo build --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --bin caption-contract --manifest-path local-tools/draw-present-final-20261124/OpenGMK/Cargo.toml
cargo build --offline --locked --release -Z build-std=std,panic_abort --target armv7-sony-vita-newlibeabihf -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --manifest-path local-tools/draw-present-final-20261124/OpenGMK/Cargo.toml
```

Exact CPU contract/startup executions retained in the private reports:

```text
build/draw23-tested-host/mp3-scan-contract.exe recovered/mp3-20261124/startup-validated/Music/menu.mp3
build/draw23-host/i686-pc-windows-msvc/release/caption-contract.exe
build/draw23-geometry-tests.exe gradient_rectangle --nocapture
build/draw23-geometry-tests.exe viewport_shader --nocapture
python tools/opengmk/run_vm_probe.py --runtime build/draw23-tested-final/howaw-vm-probe.exe --input-dir recovered/mp3-20261124/startup-validated --experiment draw-20261124 --run-name startup-final --owner-dialog-high --native-priority-contract --expected-service Graphics --expected-operation native_frame_begin --require-persistent --diagnostic-prefix e023
```

Private packaging commands (SDK tools reuse the same WSL path translation):

```text
vita-elf-create build/draw23-present-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.elf build/draw23-present-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.velf
python tools/opengmk/package_priority_probe.py --prepare --experiment E023 --elf build/draw23-present-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.elf --velf build/draw23-present-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.velf --output build/draw23-present-device
python tools/opengmk/package_priority_probe.py --package --experiment E023 --output build/draw23-present-device --title-id HOWAW1178 --app-version 00.24
```

Use the existing E022 WSL linker/ar environment, `RUSTFLAGS=-C target-feature=-neon`, `HOWAW_GRAPHICS_LIB_DIR=build/depth23-native-v3`, separate preserved target directories. Native C: `-mfloat-abi=hard -std=c11 -O2 -Wall -Wextra -Werror`. Geometry: `rustc --edition 2021 --test tools/opengmk/graphics/geometry.rs -o build/draw23-geometry-tests.exe`, run only new `gradient_rectangle` and `viewport_shader` tests. CPU scan comparison binary takes the original MP3 path; caption binary needs no game data. Host VM intentionally stops at Graphics/native_frame_begin after 76 fresh-profile instructions; no GPU is simulated. Desktop default-feature check PASS (27.37 s), reuse audit **22/22**, fresh preparation **202/202 files identical**, original draw.rs equals upstream except diagnostic traces/host guard, Game::frame byte-identical, Cargo.lock unchanged. PC builds PASS 53.12 / 54.97 s, caption contract build 38.20 s, final presentation build 49.71 s; ARM builds PASS 1m24s / 1m17s. Revisions correspond to original Draw instrumentation, the measured caption gate and native viewport/presentation; previous device binaries and tested host snapshots are retained. The caption contract deliberately catches a size-operation error, so its expected panic-hook output is not an uncaught test failure.

Baseline ZIP `423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62`, EXE `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f`, MP3 `e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0`. First VPK `cbc5c31e5969e21494152689c916973e72a52a5b8b2a6c1410720272abed89c3`, installed SELF `80cbc0ca8aa561834f61992d0de0eab17c033e3d4c9fd45400c92fb4ad2e9252`, log `c3f408e5681b04e9575ae2fedad7dc691bbb23cfb4b5826d82e9912c08b97f31`. Revised VPK `a21c90dce7a3175747c36fb240c962944e3758b033d83dbe51b85228f8f9451b`, installed SELF `58c84e2a4a96cf0ef1f3a78e65accc59f007920655fff2992fce74e50e3f5757`, log `2f1bd402cc3062302424a85de12b2c6ea98ad9ae94060bd3fcead24894ed2ced`. Actual presented-frame RGBA SHA-256 `418be68f81353d4c146c15195024f2c62ad339cb0f7f81a525b72bcc565707fd`. Installed SFO/SELF and remote VPK identities verified for both runs; firmware remains unreported. Retrieved INI is byte-identical to E022. No original files embedded in VPK or committed. Private evidence: `reports/local/draw-20261124/`, source copies `local-tools/draw*-20261124/`, preserved builds `build/draw23-*`, `build/depth23-native-*`.

**New recovery zero**; unchanged prior counts: 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms. Route B with original VM and libvita2d/GXM remains best supported. **Next one high-information experiment:** implement real Vita input/event polling, retain the original control behavior through an explicit mapping, then execute the unchanged Game::frame with normal pacing until the menu fade advances or the next actual audio/graphics service stops it. Do not bypass poll_events, synthesize neutral input success, repeat only Draw while skipping Step, or fabricate playback.
