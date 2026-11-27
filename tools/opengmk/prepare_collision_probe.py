#!/usr/bin/env python3
"""Post-E032 CPU/ARM candidate; does not package another device diagnostic."""
import argparse,shutil,subprocess
from pathlib import Path
from prepare_vm_probe import close

def extend(root):
    src=root/'gm8emulator/src';own=Path(__file__).parent
    shutil.copyfile(own/'cached_bbox.rs',src/'cached_bbox.rs')
    shutil.copyfile(own/'collision_contract.rs',src/'bin/collision_contract.rs')
    p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\npub mod cached_bbox;\n',encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8');a=s.index('    pub fn check_collision(');b=close(s,s.index('{',a));original=s[a:b]
    anchor='        let inst2 = self.room.instance_list.get(i2);';assert original.count(anchor)==1
    guard='\n        if crate::cached_bbox::reject(inst1,inst2) {return false;}'
    changed=original.replace(anchor,anchor+guard,1);assert changed.replace(guard,'',1)==original
    reference='\n    #[cfg(feature="howaw_collision_contract")]\n'+original.replace('pub fn check_collision(','pub fn check_collision_reference(',1)
    s=s[:a]+changed+reference+s[b:];p.write_text(s,encoding='utf-8')
    p=root/'gm8emulator/Cargo.toml';s=p.read_text(encoding='utf-8')
    assert 'howaw_perf = []' in s;s=s.replace('howaw_perf = []','howaw_perf = []\nhowaw_collision_contract = []',1)
    s+='\n[[bin]]\nname="collision-contract"\npath="src/bin/collision_contract.rs"\nrequired-features=["vita2d","howaw_collision_contract"]\n';p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_performance_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend(a.output);print('CPU/ARM cached-bbox candidate prepared; original fallback retained; no new VPK/physical PASS')
if __name__=='__main__':main()
