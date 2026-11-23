#!/usr/bin/env python3
"""Bounded, read-only PE32 import/signature audit; never loads guest code."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import sys


def inspect(data: bytes) -> dict:
    def u16(off):
        return struct.unpack_from('<H', data, off)[0]

    def u32(off):
        return struct.unpack_from('<I', data, off)[0]

    def cstr(off):
        end = data.index(b'\0', off, min(off + 4096, len(data)))
        return data[off:end].decode('ascii', errors='replace')

    if data[:2] != b'MZ':
        raise ValueError('not MZ')
    pe = u32(0x3c)
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('not PE')
    opt = pe + 24
    if u16(opt) != 0x10b:
        raise ValueError('only PE32 supported')
    section_table = opt + u16(pe + 20)
    sections = []
    for index in range(u16(pe + 6)):
        off = section_table + index * 40
        sections.append(dict(name=data[off:off + 8].rstrip(b'\0').decode('ascii'),
                             virtual_size=u32(off + 8), rva=u32(off + 12),
                             raw_size=u32(off + 16), raw_offset=u32(off + 20)))

    def raw(rva):
        if rva < u32(opt + 60):
            return rva
        for section in sections:
            delta = rva - section['rva']
            if 0 <= delta < section['raw_size']:
                return section['raw_offset'] + delta
        raise ValueError(f'unbacked RVA {rva:#x}')

    imports = []
    import_rva, import_size = struct.unpack_from('<II', data, opt + 104)
    if import_rva:
        off = raw(import_rva)
        for index in range(min(import_size // 20, 4096)):
            original, stamp, chain, name, first = struct.unpack_from('<5I', data, off + index * 20)
            if not any((original, stamp, chain, name, first)):
                break
            thunk = raw(original or first)
            functions = []
            for n in range(65536):
                value = u32(thunk + n * 4)
                if value == 0:
                    break
                functions.append(f'ordinal:{value & 0xffff}' if value & 0x80000000 else cstr(raw(value) + 2))
            imports.append(dict(dll=cstr(raw(name)), functions=functions))
    # Literal candidates do NOT prove dynamic loading or execution.
    candidates = []
    for match in re.finditer(rb'[A-Za-z0-9_.-]+\.dll', data, flags=re.IGNORECASE):
        if len(match.group()) <= 128:
            candidates.append(dict(offset=hex(match.start()), name=match.group().decode('ascii')))
    fixed_versions = []
    for match in re.finditer(re.escape(bytes.fromhex('bd04effe')), data):
        off = match.start()
        if off + 52 <= len(data) and u32(off + 4) == 0x10000:
            def version(at):
                high, low = u32(at), u32(at + 4)
                return f'{high >> 16}.{high & 65535}.{low >> 16}.{low & 65535}'
            fixed_versions.append(dict(offset=hex(off), file_version=version(off + 8),
                                       product_version=version(off + 16),
                                       caveat='application metadata; not runner-build proof'))
    gm80 = dict(signature_source='OpenGMK gm8exe/src/gamedata/gm80.rs',
                load_sequence=False, version_check=False, header_matches=False)
    if len(data) > 0x144ac4:
        gm80['load_sequence'] = data[0xa49be:0xa49c6] == bytes.fromhex('8b45f4e82abdfdff')
        gm80['version_check'] = data[0xa49e2:0xa49f4] == bytes.fromhex('8bc6e807bdfdff3d200300000f85f5000000')
        if gm80['load_sequence'] and data[0xa49c6] == 0x3d:
            magic = u32(0xa49c7)
            pointer = u32(0x144ac0)
            gm80.update(magic=magic, pointer=hex(pointer))
            for pos in range(pointer, len(data) - 16, 10000):
                if u32(pos) == magic:
                    gm80.update(header_offset=hex(pos), header_version=u32(pos + 4),
                                header_matches=u32(pos + 4) == 800)
                    break
    overlay = max(s['raw_offset'] + s['raw_size'] for s in sections)
    return dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                machine=hex(u16(pe + 4)), entry_rva=hex(u32(opt + 16)),
                image_base=hex(u32(opt + 28)), image_bytes=u32(opt + 56),
                stack_reserve=u32(opt + 72), heap_reserve=u32(opt + 80),
                sections=sections, overlay_offset=overlay, overlay_bytes=len(data) - overlay,
                imports=imports, import_descriptors=len(imports),
                import_entries=sum(len(item['functions']) for item in imports),
                unique_imports=len({(item['dll'].lower(), f) for item in imports for f in item['functions']}),
                delay_import_directory=struct.unpack_from('<II', data, opt + 96 + 13 * 8),
                dll_literal_candidates=candidates, fixed_versions=fixed_versions,
                gm80=gm80)


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python tools/inspect_pe.py <private-copy.exe>')
    path = Path(sys.argv[1])
    if path.stat().st_size > 512 * 1024 * 1024:
        raise ValueError('input too large')
    print(json.dumps(inspect(path.read_bytes()), indent=2))


if __name__ == '__main__':
    main()
