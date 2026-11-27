#!/usr/bin/env python3
"""E031: original line family/circles and separated native presentation timings."""
import argparse,subprocess
from pathlib import Path
from prepare_vm_probe import close
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_tint_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    p=a.output/'gm8emulator/src/gml/kernel.rs';s=p.read_text(encoding='utf-8')
    for name in ['draw_line','draw_line_color','draw_line_width','draw_line_width_color','draw_circle','draw_circle_color','draw_set_circle_precision']:
        start=s.index('    pub fn '+name+'(');end=close(s,s.index('{',start));body=s[start:end].replace('#[cfg(feature="headless")]','#[cfg(all(feature="headless",not(feature="vita2d")))]').replace('#[cfg(not(feature="headless"))]','#[cfg(any(not(feature="headless"),feature="vita2d"))]');s=s[:start]+body+s[end:]
    p.write_text(s,encoding='utf-8');p=a.output/'gm8emulator/src/diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e030-{n:03}','e031-{n:03}').replace('E030_DIAGNOSTIC_STARTED','E031_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    print('E031 general original line/circle contracts and CPU/GPU/display timing split')
if __name__=='__main__':main()
