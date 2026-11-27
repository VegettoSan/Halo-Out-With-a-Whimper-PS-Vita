#!/usr/bin/env python3
"""E035: measured native pair/line AABB misses bypass per-query clocks, not GML."""
import argparse,subprocess,shutil
from pathlib import Path
from prepare_vm_probe import close

PAIR='\n        if !crate::collision_profile::reference() && i1!=i2 {let a=self.room.instance_list.get(i1);let b=self.room.instance_list.get(i2);if crate::cached_bbox::reject(a,b) {crate::collision_profile::fast_reject(0);return false;}}'
LINE='\n        if !crate::collision_profile::reference() {let a=self.room.instance_list.get(inst);if crate::cached_bbox::reject_line(a,x1,y1,x2,y2) {crate::collision_profile::fast_reject(4);return false;}}'

def ellipse_wrapper(header):
    return header+'\n        let item=self.room.instance_list.get(inst);\n        if !crate::collision_profile::reference() && item.image_angle.get().into_inner()==0. && item.image_xscale.get().into_inner().abs()==1. && item.image_yscale.get().into_inner().abs()==1. {self.check_collision_ellipse_unit_candidate(inst,x1,y1,x2,y2,precise)} else {self.check_collision_ellipse_generic_candidate(inst,x1,y1,x2,y2,precise)}\n    }'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);p.add_argument('--device-identity',action='store_true');a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_collision_detail_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    src=a.output/'gm8emulator/src';path=src/'game.rs';s=path.read_text(encoding='utf-8')
    for name,guard in [('check_collision',PAIR),('check_collision_line',LINE)]:
        start=s.index('    pub fn '+name+'(');i=s.index('{',start)+1;s=s[:i]+guard+s[i:]
    from audit_vm_probe import method
    name='check_collision_ellipse';start=s.index('    pub fn '+name+'(');end=close(s,s.index('{',start))
    reference=method(s,name+'_reference').replace('pub fn '+name+'_reference(','pub fn '+name+'_generic_candidate(',1).replace('.check_collision_point_precise_reference(','.check_collision_point_precise(')
    unit=reference.replace('pub fn '+name+'_generic_candidate(','pub fn '+name+'_unit_candidate(',1).replace('.check_collision_point_precise(','.check_collision_point_unit(')
    s=s[:start]+ellipse_wrapper(s[start:s.index('{',start)+1])+'\n    #[inline(never)]\n'+reference+'\n    #[inline(never)]\n'+unit+s[end:]
    path.write_text(s,encoding='utf-8')
    path=src/'bin/collision_detail_contract.rs';s=path.read_text(encoding='utf-8');anchor='  let n=3200;';assert anchor in s
    extra='''  bench(&format!("{label}_far_line_320"),32000,|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);let x=Real::from(i.bbox_right.get())+1024.into();let y=Real::from(i.bbox_bottom.get())+1024.into();g.check_collision_line_reference(h,x,y,x+16.into(),y+16.into(),true)},|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);let x=Real::from(i.bbox_right.get())+1024.into();let y=Real::from(i.bbox_bottom.get())+1024.into();g.check_collision_line(h,x,y,x+16.into(),y+16.into(),true)});
'''
    path.write_text(s.replace(anchor,extra+anchor,1),encoding='utf-8')
    if a.device_identity:
        path=src/'diagnostics.rs';s=path.read_text(encoding='utf-8');assert 'E032_DIAGNOSTIC_STARTED' in s;s=s.replace('E032_DIAGNOSTIC_STARTED','E035_DIAGNOSTIC_STARTED').replace('e032-{n:03}','e035-{n:03}');path.write_text(s,encoding='utf-8')
        path=src/'bin/vm_probe.rs';s=path.read_text(encoding='utf-8').replace('e034-collision-reference.flag','e035-collision-reference.flag');path.write_text(s,encoding='utf-8')
    print('E035 pair/line fresh-box prefilters before timing probes; all fallback/GML preserved, no VPK')
if __name__=='__main__':main()
