#!/usr/bin/env python3
"""E030: native texture times interpolated corner color, existing GXM backend."""
import argparse,subprocess
from pathlib import Path
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_frame_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    p=a.output/'gm8emulator/src/diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e029-{n:03}','e030-{n:03}').replace('E029_DIAGNOSTIC_STARTED','E030_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    print('E030 native per-vertex texture color, original triangle planes and source edge clamps')
if __name__=='__main__':main()
