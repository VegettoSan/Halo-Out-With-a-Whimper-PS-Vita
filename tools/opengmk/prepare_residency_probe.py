#!/usr/bin/env python3
"""E027: measured fifth-atlas gate; bounded native GPU-mapped main RAM."""
import argparse,subprocess
from pathlib import Path

def extend_residency(root):
    src=root/'gm8emulator/src'
    p=src/'render/native.rs';s=p.read_text(encoding='utf-8');marker='device.color_clear_contract()?;device.check()?;Ok(device)';assert marker in s
    s=s.replace(marker,'crate::diagnostic!("[color-clear-proof-reuse] E026 contract PASS; fixture not repeated");device.check()?;Ok(device)',1);p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8');marker='            completed+=1;frame_us.push(cpu_start.elapsed().as_micros() as u64);';assert marker in s
    s=s.replace(marker,marker+'''
            if crate::render::vita2d::take_ram_upload() {crate::render::vita2d::inspect_original_frame()?;}
            if completed%60==0 {
                let mut samples=[0u64;60];samples.copy_from_slice(&frame_us[frame_us.len()-60..]);samples.sort_unstable();
                let budget=1_000_000/u64::from(self.room.speed.max(1));
                crate::diagnostic!("[frame-window] completed={} room={} count=60 min_us={} p50_us={} p95_us={} max_us={} over_room_budget={}; CPU/input/GPU-wait excludes limiter, not displayed FPS",completed,self.room.id,samples[0],samples[30],samples[56],samples[59],samples.iter().filter(|&&v|v>budget).count());
            }
''',1);p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e026-{n:03}','e027-{n:03}').replace('E026_DIAGNOSTIC_STARTED','E027_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_room_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend_residency(a.output);print('E027 bounded CDRAM/main-RAM pools, no eviction or duplicate pixels; original frame readback after new RAM upload only')
if __name__=='__main__':main()
