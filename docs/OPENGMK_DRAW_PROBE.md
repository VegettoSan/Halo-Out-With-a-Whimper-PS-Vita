# E023 — depth-only GXM proof and original menu Draw

**2026-11-25 UTC / 2026-11-24 America/Bogota. VERIFIED:** physical Vita 1000 passes the real depth/color/occlusion contract and executes the original menu objects' Draw events. First private HOWAW1178 / 00.24 reaches **105 VM instructions**, then stops at `Window/set_title` before presentation. The original data and VM are retained. A follow-up caption/presentation test is being validated; no visible menu, working input, audio output or playable game VPK is claimed.

## Corrected depth contract

E022's adapter stopped too early. The pinned [OpenGMK implementation](https://github.com/OpenGMK/OpenGMK/blob/9e4282e6d19f4dd00961811840ddc3e11da6dd5a/gm8emulator/src/render/opengl.rs#L2265) calls `glClear(DEPTH_BUFFER_BIT)` **only when `using_3d` is true**. Its 2D `set_depth` stores zero and depth testing is masked by that mode. The original menu requests no 3D mode. E023 preserves this guard: its menu call logs `using_3d=false gpu_clear=false`. This is a verified no-op contract, not a claimed GPU clear. Enabling 3D remains unsupported.

The C extension separately implements a genuine depth-only primitive, reusing the installed libvita2d clear shaders with an independently owned fragment patch whose color write mask is NONE. It writes far depth with ALWAYS testing, preserves stencil, restores the supported 2D depth state, checks fallible GXM calls and releases its patches before libvita2d teardown. No shader compiler, vitaGL, codec download or SDK modification. [Library lifecycle/shader interface](https://github.com/xerpi/libvita2d/blob/master/libvita2d/source/vita2d.c).

The **32×32 offscreen** test never presents a fixture. It writes near depth/red color; a farther green fragment must fail. After a synchronized readback, the depth-only clear must preserve every color byte and change all 1,024 raw depth words. Finally the same farther green fragment must pass. Force-store/load preserves depth between the three scenes. Physical result: **1,024/1,024 in each check, rc=0, four actual GXM draws, 11,928 µs including waits**. This proves the tested primitive, not full 3D compatibility or GPU-only execution time.

## Original execution and renderer additions

Unchanged `Game::init → load_room → Game::draw → Draw/0` now executes **object 0 / instance 108698** and **object 1 / instance 100002** on Vita. Trace instrumentation changes no event ordering. The first native run actually submits room background tiles, additive and normal blending, original sprites and a filled uniform rectangle. **Text and gradient/outline branches have not yet executed**; no menu reconstruction or forced Draw after failed initialization.

Keep E020's RendererTrait, atlas IDs, lazy page uploads and ordered sprite batching. Add filled/gradient color batches and original kernel rectangle/blend dispatch. Original font/alignment/text routines remain in place and use the engine's existing glyph resources. Unsupported outline/other blend factors still stop explicitly. Adapt libvita2d's ONE/ONE additive preset to GM8's SRC_ALPHA/ONE at fragment-program creation; normal blending remains unchanged. Arbitrary blend modes and exact rasterization parity remain unverified.

The follow-up normalizes vertices into libvita2d's fixed shader domain and uses a real GXM viewport for the full **640×325** original view, aspect-fitted to 960×544 at **1.5**, offset **(0,28.25)**. Clip-space clipping bounds tiled geometry to the view. Presentation accepts only matching logical dimensions and an identity logical scaling policy (Fixed 1, Full or Aspect when framebuffer/window dimensions already match). Subviews, rotated views and resized logical windows remain unavailable. Mapping and rectangle fan/color contracts pass on CPU; physical pixel parity remains unverified.

The observed caption gate is an asynchronous **void request**: [Ramen's contract](https://github.com/viriuwu/ramen/blob/ef715f65981f6c96f7f889258ff43b63cb472626/src/window.rs#L152) explicitly allows the OS to ignore it; the cached Windows implementation discards `SetWindowTextW`'s return. The follow-up stores the requested caption and logs `native_titlebar=Unavailable os_title_changed=false`. It does not claim a native titlebar change or general Window capability. CPU request/replacement contract passes; size operations remain unavailable.

## MP3 reuse, memory and limits

Validation is now integrated into the existing decoded length scan. Every candidate is still actually decoded; finite/count checks and first-frame channel/rate policies remain. No cached hash is treated as decoding success. A dedicated PC comparison against the real streaming player matches **7,130,880 samples, 7,129,724 nonzero, peak 1.0173236, RMS 0.15675603246370387** and rejects invalid/empty data. No E022 registry fixture repeated.

First native scan: **3,639,780 µs**, versus E022's two-pass **6,845,926 µs** (46.8% lower observed interval, not a controlled benchmark). Retain the compressed **1,293,667 B**, bounded **9,216 B** PCM scratch and small scan metadata; no full-song PCM allocation. Audio playback remains unavailable.

| First physical run | Measured result |
| --- | --- |
| Prepared CPU pixels | 71,602,980 B / 3,003 entries / six atlas descriptions |
| Resident GPU pages | **Two / 33,554,432 B**, loaded on demand, no duplicate upload |
| CPU pixels released / remaining | **30,513,548 / 41,089,432 B** |
| Heap live at stop / lifetime peak | **65,796,976 / 108,104,996 B**; peak includes original reader |
| Free CDRAM before / after GXM / two pages | **117,440,512 / 94,371,840 / 60,817,408 B** |
| Free user memory before / after GXM | **124,780,544 / 115,343,360 B**; distinct from live heap |
| Cleanup | Unpresented scene ended successfully; heap 1,142 B; system-free memory restored |
| First result | Depth and object Draw **PASS**; caption/presentation **BLOCKED**, exit 1 |

A **64 MiB resident atlas budget** prevents attempting all six 16 MiB pages. Exceeding it remains an explicit failure: recoverable eviction/backing storage is not implemented. Original CPU payloads are freed only after successful upload. Full-game fit, gameplay FPS, native input, suspend/resume and audio output remain unproven.

## Reproduction and evidence

Pinned OpenGMK `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`; cached Ramen `ef715f65981f6c96f7f889258ff43b63cb472626`; rmp3 0.3.1/minimp3; Rust/Cargo 1.100.0, MSVC 14.50.35717, existing WSL hard-float VitaSDK GCC 15.2.0. All offline. Installed libvita2d archive SHA-256 remains `c5857b65ea7a93f6ff37f29abd84ed2fe1d6faca9bcf9a83a60e33e110b69e99`; exact library source commit remains unknown.

```text
python tools/opengmk/prepare_draw_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/draw-present-final-20261124/OpenGMK --udon-source local-tools/arena-probe-20261122/udon-work/src/source.rs
python tools/opengmk/prepare_graphics_native.py --output build/depth23-native-v3
python tools/opengmk/audit_vm_probe.py --source local-tools/menu-probe-20261122/OpenGMK --work local-tools/draw-present-final-20261124/OpenGMK --report reports/local/draw-20261124/reuse-present-final.json
cargo build --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --bin caption-contract --manifest-path local-tools/draw-present-final-20261124/OpenGMK/Cargo.toml
cargo build --offline --locked --release -Z build-std=std,panic_abort --target armv7-sony-vita-newlibeabihf -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --manifest-path local-tools/draw-present-final-20261124/OpenGMK/Cargo.toml
```

Use the existing E022 WSL linker/ar environment, `RUSTFLAGS=-C target-feature=-neon`, `HOWAW_GRAPHICS_LIB_DIR=build/depth23-native-v3`, separate preserved target directories. Native C: `-mfloat-abi=hard -std=c11 -O2 -Wall -Wextra -Werror`. Geometry: `rustc --edition 2021 --test tools/opengmk/graphics/geometry.rs -o build/draw23-geometry-tests.exe`, run only new `gradient_rectangle` and `viewport_shader` tests. CPU scan comparison binary takes the original MP3 path; caption binary needs no game data. Host VM intentionally stops at Graphics/native_frame_begin after 76 fresh-profile instructions; no GPU is simulated. Desktop default-feature check PASS (27.37 s), reuse audit **22/22**, original draw.rs equals upstream except diagnostic traces/host guard, Cargo.lock unchanged.

Baseline ZIP `423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62`, EXE `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f`, MP3 `e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0`. First VPK `cbc5c31e5969e21494152689c916973e72a52a5b8b2a6c1410720272abed89c3`, installed SELF `80cbc0ca8aa561834f61992d0de0eab17c033e3d4c9fd45400c92fb4ad2e9252`, log `c3f408e5681b04e9575ae2fedad7dc691bbb23cfb4b5826d82e9912c08b97f31`. Retrieved INI is byte-identical to E022. No original files embedded in VPK or committed. Private evidence: `reports/local/draw-20261124/`, source copies `local-tools/draw*-20261124/`, preserved builds `build/draw23-*`, `build/depth23-native-*`.

**New recovery zero**; unchanged prior counts: 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms. Route B with original VM and libvita2d/GXM remains best supported. Next discriminating test: complete the caption request, present only a successful original initialization frame and identify the next real frontend service before advancing Game::frame.
