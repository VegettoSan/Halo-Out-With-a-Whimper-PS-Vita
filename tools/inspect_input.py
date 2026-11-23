#!/usr/bin/env python3
"""Read a private HOWaW archive without executing or extracting its contents."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

EXPECTED_ZIP = "423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62"
EXPECTED_EXE = "cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f"
MAX_BYTES = 512 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_pe(data: bytes) -> dict:
    if len(data) < 64 or data[:2] != b"MZ":
        return {"error": "not an MZ executable"}
    off = struct.unpack_from("<I", data, 0x3c)[0]
    if off + 24 > len(data) or data[off:off + 4] != b"PE\x00\x00":
        return {"error": "invalid PE signature"}
    machine, sections = struct.unpack_from("<HH", data, off + 4)
    optional_size = struct.unpack_from("<H", data, off + 20)[0]
    optional_start = off + 24
    table = optional_start + optional_size
    if table + 40 * sections > len(data):
        return {"error": "invalid section table"}
    magic = struct.unpack_from("<H", data, optional_start)[0]
    end = 0
    for idx in range(sections):
        base = table + idx * 40
        raw_size, raw_offset = struct.unpack_from("<II", data, base + 16)
        if raw_size and raw_offset + raw_size <= len(data):
            end = max(end, raw_offset + raw_size)
    markers = ("Game Maker", "gamemaker_version", "Sprite_Class", "Room_Class", "D3DX8.dll")
    return {
        "machine": f"0x{machine:04x}",
        "arch_hint": "x86" if machine == 0x14c else "unknown",
        "pe_type": "PE32" if magic == 0x10b else "PE32+" if magic == 0x20b else "unknown",
        "sections": sections,
        "overlay_bytes": len(data) - end if end else None,
        "markers": {m: m.encode("ascii") in data for m in markers},
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        print("Missing input or too large", file=sys.stderr)
        return 2
    blob = path.read_bytes()
    report = {"archive": path.name, "sha256": sha256(blob), "matches_baseline": sha256(blob) == EXPECTED_ZIP}
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        if len(infos) > 1000 or sum(i.file_size for i in infos) > MAX_BYTES:
            raise ValueError("Archive exceeds inspection limits")
        for info in infos:
            name = info.filename.replace("\\", "/")
            if not name or name.startswith("/") or ".." in name.split("/") or ":" in name:
                raise ValueError(f"unsafe archive path: {name!r}")
        report["crc_ok"] = z.testzip() is None
        report["entries"] = []
        for info in infos:
            if info.is_dir():
                continue
            data = z.read(info)
            entry = {"name": info.filename, "size": info.file_size, "sha256": sha256(data)}
            if info.filename.lower().endswith(".exe"):
                entry["pe"] = inspect_pe(data)
                entry["matches_baseline_exe"] = entry["sha256"] == EXPECTED_EXE
            report["entries"].append(entry)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["crc_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
