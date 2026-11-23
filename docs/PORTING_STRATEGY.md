# Porting strategy — prioritize faithful reuse

PS Vita ARMv7 cannot directly run Windows x86 PE32. Comparison is between **three research paths**, not three ready-made ports.

## A. Translate original executable x86 -> ARM and implement APIs
- Reference: [D2Vita](https://github.com/Franckrst/D2Vita) for feasibility *in another game*. NOT proof of GM compatibility.
- Needs: PE loader, x86-to-ARM execution, Windows API stubs or implementations, memory/TLS/threads/exceptions, graphics pipeline (Direct3D 8 / DirectDraw if actually used), audio (DirectSound if used), input and timing.
- Minimum test: inspect exact imports and runner behavior; demonstrate real code execution with bounded scope, then real game progress. Launching a dummy shell fails parity.
- Main risks: legacy runner coupling, API breadth, frame pacing, CPU/memory overhead.

## B. Recover GameMaker data/GML and adapt a compatible runtime
- References: [GM8Decompiler](https://github.com/OpenGMK/GM8Decompiler), [OpenGMK](https://github.com/OpenGMK/OpenGMK), [Gmk-Splitter](https://github.com/Medo42/Gmk-Splitter).
- First identify actual runner version; then try a compatible extractor on a COPY. Never promise .gmk/.gm81 without recovery evidence.
- Inventory objects, rooms, events, scripts, sprites, audio and assets; validate a representative interaction on a compatible PC runtime.
- Evaluate VitaSDK graphics/input/audio backend only after proving data/logic compatibility. **OpenGMK is not an existing Vita engine.**
- Main risks: missing GameMaker built-ins, proprietary runner behavior, asset fidelity, script semantics and license/portability.

## C. Static recompilation of selected x86 code to ARM
- Reference: [sh3vita](https://github.com/matfsouza/sh3vita), as a distinct game's approach.
- Main risks: monolithic opaque GameMaker runner, OS/DirectX glue and indirect calls.
- Do not adopt without a concrete tractable translation proof.

## Decision matrix
Rank using: actual recovered/executed game logic; amount of original code/assets reused; reproducible PASS/FAIL evidence; Vita memory/CPU cost; time to a real interacting menu/arena; legal compatibility.

**Initial priority:** cheap tests for both A (imports/loader compatibility) and B (version/dump compatibility). Route B may be more maintainable but is NOT preselected. Escalate to C only when justified.

## Evidence labels
VERIFIED = inspected or measured; INFERRED = reasoned; UNTESTED = proposed. Update decisions in docs/DECISIONS.md and tests in docs/EXPERIMENTS.md.
