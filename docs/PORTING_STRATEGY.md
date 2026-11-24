# Porting strategy — prioritize faithful reuse

**E019 evidence:** route B now has physical Vita 1000 execution of unchanged original data through the existing compiler/VM: 11 instructions to Dialog, 15 under the owner-selected High diagnostic policy to Process. This establishes a native logic prefix, not renderer/audio/input parity or a playable port. Continue explicit native services, preserving original logic; [E019](OPENGMK_PRIORITY_PROBE.md).

**E018 evidence:** route B preserves original startup through a real PC dialog and owner choice, then stops at an explicit Process service. CleanMem's Windows effects are measured; Vita exposes defined failure for unsupported working-set operations rather than fake success. Updated ARM ELF/VELF passes, execution remains untested. Continue bounded services/diagnostics before graphics or packaging; [ADR-006](DECISIONS.md), [E018](OPENGMK_CLEANMEM_PROBE.md).

**E017 evidence:** route B now builds the existing compiler/VM for Vita ARM and executes original startup on PC until an explicit CleanMem external-service block. This supports incremental native services without replacing GML/VM. It does not establish ARM execution or a native frontend; [ADR-005](DECISIONS.md) and [VM probe](OPENGMK_VM_PROBE.md) set the next gate.

**Current E016 evidence:** route B additionally has PC profile restart PASS and real reader/parser ARM build/link/VELF conversion PASS. Full native VM execution remains blocked by frontend/OS/audio services, with graphics and device memory untested. [ADR-004](DECISIONS.md) and [native probe](OPENGMK_NATIVE_PROBE.md) define the next bounded original-startup experiment; historical findings below retain their original scope.

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

## Evidence update — 2026-11-23 UTC

- **VERIFIED B:** GameMaker 8.0 format, strict project recovery and independent inventory succeeded. Local OpenGMK 0.2.0 executes startup GML but fails on `show_message_ext` before a menu. Standard Gmk-Splitter export also fails on a duplicate sprite name; no IDs or names were changed.
- **VERIFIED A:** the subsequently supplied WinVita loader maps the real EXE on a PC host; guest execution remains UNTESTED. The supplied source lacks D3D8 handling and returns an error for DirectDraw creation. D2Vita's Glide presentation cannot be assumed to handle this runner. Its optional kernel-plugin arrangement is a reference claim, not a requirement adopted for this port.
- **INFERRED priority:** B offers the smallest next experiment while preserving original GML/assets. Implement the missing dialog in a runtime copy and retest the unchanged EXE; keep A available. Native Vita rendering/input/audio, memory, frame pacing, suspend/resume and saves are not designed or measured yet.
- **C remains UNTESTED/deferred:** no tractable static-recompilation proof or measured reason to prefer it.

See [ADR-001](DECISIONS.md) for comparison, effort uncertainty, licensing observations and the next decision gate. No playable PC compatibility or functional Vita VPK is established.

## PC menu update — 2026-11-23 UTC

**VERIFIED E014:** route B now reaches the original interactive PC main menu and Firefight map/difficulty selection after a faithful runtime-only Windows `show_message_ext` implementation. No GML or recovered resources changed. The next test is an original PC arena; combat parity, audio, ARM portability and Vita performance remain UNTESTED. This supersedes only the current-menu blocker above, retaining E007's failed baseline. See [ADR-002](DECISIONS.md) and [reproduction details](OPENGMK_PC_PROBE.md). No VPK was generated.

## First arena update — E015

**VERIFIED:** original Site 117 gameplay works at a basic cooperative manual-test scope: movement/jump, aim/fire, enemies, collisions/damage and pause/return. A runtime INI adapter fixes default-profile visibility/cycling helmets. Audio has a measured/reported intermittent issue whose cause is not proven fixed; restart persistence remains untested after CUA stopped. **INFERRED:** enough PC reuse is demonstrated to plan native Vita adapters; no ARM/Vita viability or performance is established. [ADR-003](DECISIONS.md) retains route B and [the arena report](OPENGMK_FIREFIGHT_PROBE.md) defines the limits. WinVita remains dormant.
