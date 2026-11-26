#!/usr/bin/env python3
"""E028: original customization outline and per-sprite clamped source crops."""
import argparse,subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_residency_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    p=a.output/'gm8emulator/src/diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e027-{n:03}','e028-{n:03}').replace('E027_DIAGNOSTIC_STARTED','E028_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    print('E028 original outline and edge-clamped crops; original events/resources unchanged')
if __name__=='__main__':main()
