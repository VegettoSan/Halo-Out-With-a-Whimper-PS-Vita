#!/usr/bin/env python3
"""Launch a private, already-copied PC game and log process memory/exit status.

No guest/game changes. Output directories must be ignored; logs may contain
private paths. Windows only. Memory counters are not frame-time/FPS measurements.
"""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time


class MemoryCounters(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('faults', wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in (
            'peak_working_set', 'working_set', 'peak_paged_pool', 'paged_pool',
            'peak_nonpaged_pool', 'nonpaged_pool', 'pagefile', 'peak_pagefile', 'private_bytes')]


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--game-dir', type=Path, required=True)
    parser.add_argument('--report-dir', type=Path, required=True)
    parser.add_argument('--temp-dir', type=Path, required=True)
    parser.add_argument('--audio-latency-ms', type=float)
    parser.add_argument('--audio-diagnostics', action='store_true')
    args = parser.parse_args()
    runtime, game, report, temp = [p.resolve() for p in (
        args.runtime, args.game_dir, args.report_dir, args.temp_dir)]
    exe = game / 'HOWaW_FirefightDemov1.exe'
    game_hash = hashlib.sha256(exe.read_bytes()).hexdigest()
    if game_hash != 'cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f':
        raise ValueError('copied game does not match baseline')
    report.mkdir(parents=True, exist_ok=False)
    temp.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(TEMP=str(temp), TMP=str(temp), RUST_BACKTRACE='1')
    if args.audio_latency_ms is not None:
        env['OPENGMK_AUDIO_LATENCY_MS'] = str(args.audio_latency_ms)
    if args.audio_diagnostics:
        env['OPENGMK_AUDIO_DIAGNOSTICS'] = '1'
    for key in ['APPDATA', 'LOCALAPPDATA', 'USERPROFILE']:
        location = temp / key.lower()
        location.mkdir(exist_ok=True)
        env[key] = str(location)
    command = [str(runtime), exe.name, '-s']
    get_memory = ctypes.WinDLL('psapi', use_last_error=True).GetProcessMemoryInfo
    get_memory.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
    get_memory.restype = wintypes.BOOL
    with (report / 'stdout.txt').open('xb') as stdout, (report / 'stderr.txt').open('xb') as stderr:
        child = subprocess.Popen(command, cwd=game, env=env, stdout=stdout, stderr=stderr,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        (report / 'process.json').write_text(json.dumps(dict(
            pid=child.pid, utc_start=utc(), command=command, game_sha256=game_hash,
            runtime_sha256=hashlib.sha256(runtime.read_bytes()).hexdigest(),
            isolation='fresh cwd and process-local profile/temp; host process, not VM'), indent=2))
        print(f'Probe PID {child.pid}; reports {report.name}', flush=True)
        stop = threading.Event()
        def sample():
            started = time.perf_counter()
            with (report / 'memory.jsonl').open('x') as log:
                while not stop.is_set():
                    counters = MemoryCounters()
                    counters.cb = ctypes.sizeof(counters)
                    if get_memory(int(child._handle), ctypes.byref(counters), counters.cb):
                        log.write(json.dumps(dict(utc=utc(), elapsed_s=time.perf_counter()-started,
                            working_set_bytes=counters.working_set,
                            peak_working_set_bytes=counters.peak_working_set,
                            private_bytes=counters.private_bytes,
                            page_faults=counters.faults)) + '\n')
                        log.flush()
                    stop.wait(0.5)
        worker = threading.Thread(target=sample, daemon=True)
        worker.start()
        code = child.wait()
        stop.set()
        worker.join()
        (report / 'exit.json').write_text(json.dumps(dict(exit_code=code, utc_end=utc()), indent=2))
        print(f'Probe exited {code}', flush=True)


if __name__ == '__main__':
    main()
