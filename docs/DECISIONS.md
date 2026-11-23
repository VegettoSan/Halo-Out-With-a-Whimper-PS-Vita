# Architecture decision log

## ADR-000 — 2026-11-22: do not select engine yet

**Status:** Accepted for initial research (not a runtime implementation).

**Context:** Original input is a Windows x86 GameMaker-family executable with no separately supplied source project. Vita is ARMv7. A direct copy of the EXE cannot run.

**Decision:** Compare (A) Win32/x86 translation, (B) GML/game data recovery + compatible runner and (C) static recompilation using reproducible small experiments. Preserve original logic/data rather than recreate game systems.

**Not decided:** GameMaker exact version, VitaSDK backend, SDL2/OpenGMK adoption, title ID, final renderer, distribution method or performance target achievement.

**Revisit when:** successful extraction test, explicit PE imports/loader analysis and at least one genuine interaction running in a compatible runtime have been documented.
