#!/usr/bin/env python3
"""Fault-inject a short suspension into our audio-only fixture, never a game.

The endpoint continues consuming audio while the fixture's threads are stopped.
Output stays private. Repeating this after a backend correction tests recovery.
"""
import argparse
import ctypes
from ctypes import wintypes
from pathlib import Path
import json
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--probe', type=Path, required=True)
parser.add_argument('--report-dir', type=Path, required=True)
args = parser.parse_args()
probe = args.probe.resolve()
if probe.name != 'audio_recovery_probe.exe':
    raise ValueError('only the audio-only fixture may be suspended')
args.report_dir.mkdir(parents=True, exist_ok=False)
native = ctypes.WinDLL('ntdll')
for method in ['NtSuspendProcess', 'NtResumeProcess']:
    function = getattr(native, method)
    function.argtypes = [wintypes.HANDLE]
    function.restype = wintypes.LONG
with (args.report_dir/'stdout.txt').open('xb') as out, (args.report_dir/'stderr.txt').open('xb') as err:
    child = subprocess.Popen([str(probe)], stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(1.8)
    suspended = native.NtSuspendProcess(int(child._handle))
    try:
        if suspended != 0:
            raise OSError(f'fixture suspension failed: {suspended}')
        time.sleep(0.2)
    finally:
        resumed = native.NtResumeProcess(int(child._handle))
    code = child.wait(timeout=15)
    result = dict(pid=child.pid, suspension_ms=200, suspend_status=suspended,
                  resume_status=resumed, exit_code=code,
                  scope='audio fixture only; no game or system settings changed')
    (args.report_dir/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
