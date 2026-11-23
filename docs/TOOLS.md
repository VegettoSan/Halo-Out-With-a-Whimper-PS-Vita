# Tooling checklist (prefer existing local tools)

**Host:** Windows development machine. Codex should inventory local utilities first; do not download or reinstall everything reflexively.

## Baseline
- Python 3 (standard library), script: `python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip`.
- 7-Zip or Python zipfile: archive inspection and isolated copying. Do not double-click unknown executables.
- PE introspection: pefile / dumpbin / llvm-readobj / Ghidra, whichever is already present.

## GameMaker investigation
- [GM8Decompiler](https://github.com/OpenGMK/GM8Decompiler): candidate, **only after** runner version detection.
- [Gmk-Splitter](https://github.com/Medo42/Gmk-Splitter): may help examine a recovered project.
- [OpenGMK](https://github.com/OpenGMK/OpenGMK): runner/backend research; check license, compiler, graphics dependencies and actual game compatibility.

## Windows EXE translation + Vita examples
- [D2Vita](https://github.com/Franckrst/D2Vita): research reference for x86-to-ARM/Windows adaptation.
- [sh3vita](https://github.com/matfsouza/sh3vita): comparison for recompilation method.
- [VitaSDK](https://vitasdk.org/) and [SDL2 Vita](https://wiki.libsdl.org/SDL2/README-vita): potential native target toolchain; not chosen architecture.
- Vita3K optional; **real Vita required** to substantiate performance/compatibility.

## Local-only directory roles
- `original/`: user-provided ZIP/EXE + music.
- `recovered/`: private recovered GML/resources.
- `local-tools/`: fetched third-party binaries/source copies.
- `reports/local/`: logs, dumps, profiles.
- `build/`: VPK/ELF outputs.

Never commit tool downloads, proprietary sources or recovered game data.
