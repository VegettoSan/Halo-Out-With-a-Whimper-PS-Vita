# Architecture decision log

## ADR-000 — 2026-11-22: do not select engine yet

**Status:** Accepted for initial research (not a runtime implementation).

**Context:** Original input is a Windows x86 GameMaker-family executable with no separately supplied source project. Vita is ARMv7. A direct copy of the EXE cannot run.

**Decision:** Compare (A) Win32/x86 translation, (B) GML/game data recovery + compatible runner and (C) static recompilation using reproducible small experiments. Preserve original logic/data rather than recreate game systems.

**Not decided:** GameMaker exact version, VitaSDK backend, SDL2/OpenGMK adoption, title ID, final renderer, distribution method or performance target achievement.

**Revisit when:** successful extraction test, explicit PE imports/loader analysis and at least one genuine interaction running in a compatible runtime have been documented.

## ADR-001 — 2026-11-23 UTC: prioritize route B's PC compatibility probe

**Status:** Provisional research priority; no Vita runtime selected and no P2 authorization implied.

**VERIFIED:** strict GM8Decompiler recovery and an independent GMK reader agree on 693 sprites, 128 sounds, 181 scripts, 233 objects and 15 rooms. Original GML reaches startup in OpenGMK 0.2.0, then fails at the unsupported `show_message_ext` builtin. WinVita's host loader maps the original PE and its 535 import entries, but no guest code has run under it. D3D8 support is absent from the supplied runtime source, and its DirectDraw creation shim returns an error. See E003–E010 and [technical audit](TECHNICAL_AUDIT.md).

| Criterion | A: original x86 runner + WinVita | B: original gamedata/GML + compatible runtime | C: static runner recompilation |
| --- | --- | --- | --- |
| Reuse | Original runner, GML and assets potentially retained; loader-only proof | Game data/GML structurally recovered; original startup logic executed on PC | Potential runner reuse; no translation proof |
| Fidelity | INFERRED strongest runner-semantic potential; OS/graphics replacements still affect behavior | INFERRED good logic reuse; requires semantic, collision, font/audio and timing comparisons | UNTESTED; same OS/graphics obligations plus translation correctness |
| Concrete obstacles | D3D8/device vtables, Win32/COM breadth, MCI, DLL/exception/TLS behavior | `show_message_ext` first; native backends and x86 CleanMem API adaptation | Opaque runner, indirect dispatch and OS bridges; no measured advantage |
| Complexity | INFERRED very high, several large subsystems; multi-month planning scale for one experienced developer | INFERRED lower cost for next PC experiment; substantial Vita work remains, no reliable duration yet | INFERRED highest uncertainty; defer |
| Vita performance | UNTESTED dynarec/bridge/JIT/memory costs; no transferable Diablo FPS claim | UNTESTED; avoids translating original x86 runner but interpreter/GPU/asset costs remain | UNTESTED; static code alone does not establish speed |

**Decision:** spend the next bounded experiment on a faithful implementation of `show_message_ext` in a **private compatible-runtime source copy**, retaining the original EXE/GML. Present the actual three choices and preserve return semantics; do not hard-code a return value or delete the game's call. Run the exact original copied EXE again, recording whether it reaches its real menu or the next blocker. Obtain a matching source/toolchain only if missing; no reinstall of existing binaries is warranted. Current upstream inspection also shows this builtin unimplemented.

**Why provisional:** successful recovery is not gameplay parity. An exact vendor runner patch/build has not been established beyond verified 8.0. PC menu/arena and physical Vita tests are still absent. Route A is retained because WinVita now provides a genuine loader/translation foundation; graphics and Windows compatibility costs remain unsupported by execution.

**Licenses:** local WinVita LICENSE is MIT with separately listed third-party notices; D2Vita is GPL-3.0; inspected OpenGMK runner Cargo metadata says GPL-2.0-only; Gmk-Splitter LICENSE says GPL-3.0-or-later. These are component observations, not distribution clearance. Keep reference code, original game data and recovered GML private; review the actual versions before incorporating/distributing anything. No proprietary resources from other ports were used.

**Revisit:** after an unmodified-data PC run demonstrates a real menu and one interaction, or a newly observed runtime limitation changes B's cost. Do not build a Vita VPK just to demonstrate a loader or placeholder screen.
