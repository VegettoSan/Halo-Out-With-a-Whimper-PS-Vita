#!/usr/bin/env python3
"""E026: active-scene clears, full physical display and original room entry."""
import argparse,subprocess
from pathlib import Path

def extend_room(root):
    src=root/'gm8emulator/src'
    p=src/'render/native.rs';s=p.read_text(encoding='utf-8');marker='            device.check()?;Ok(device)';assert marker in s;s=s.replace(marker,'            device.color_clear_contract()?;device.check()?;Ok(device)',1);p.write_text(s,encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8');marker='    let mut game=Game::launch(';assert marker in s;s=s.replace(marker,'    #[cfg(target_os="vita")] gm8emulator::render::vita2d::set_display_fill(true);\n'+marker,1);p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8');a=s.index('    pub fn load_room(');b=s.index('{',a)+1
    # Log the real requested room, not a selected/forced destination.
    import re
    name=re.search(r'load_room\(&mut self,\s*(\w+):',s[a:b])[1]
    s=s[:b]+f'\n        #[cfg(feature="vita2d")] crate::diagnostic!("[original-room-load] requested={{}}",{name});'+s[b:];p.write_text(s,encoding='utf-8')
    s=s.replace('            if completed==1 || completed==60 {crate::render::vita2d::inspect_original_frame()?;}','            // E025 full-frame readbacks already verified; avoid repeating their measured startup stalls.')
    p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e025-{n:03}','e026-{n:03}').replace('E025_DIAGNOSTIC_STARTED','E026_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_audio_output_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend_room(a.output);print('E026 original room progression + real active clear, full-display policy, camera translation')
if __name__=='__main__':main()
