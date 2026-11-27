#!/usr/bin/env python3
"""Extend E033 with exact unit pixel transforms and bounded collision profiling."""
import argparse,re,shutil,subprocess
from pathlib import Path
from prepare_vm_probe import close

METHODS=['check_collision','check_collision_point','check_collision_rectangle','check_collision_ellipse','check_collision_line','check_collision_solid','check_collision_any']

def extend(root):
    own=Path(__file__).parent;src=root/'gm8emulator/src'
    for name in ['collision_math.rs','collision_profile.rs']:shutil.copyfile(own/name,src/name)
    shutil.copyfile(own/'collision_detail_contract.rs',src/'bin/collision_detail_contract.rs')
    base=(own/'collision_contract.rs').read_text(encoding='utf-8').replace('//!','//').replace(' diagnostics::check().unwrap();',' detail(&g,&handles,&sprites);\n diagnostics::check().unwrap();')
    (src/'bin/collision_detail_base.rs').write_text(base,encoding='utf-8')
    p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\npub mod collision_math;\npub mod collision_profile;\n',encoding='utf-8')
    p=src/'asset/sprite.rs';s=p.read_text(encoding='utf-8');a=s.index('    pub fn check_collision_point_precise(');b=close(s,s.index('{',a));original=s[a:b];end=original.index('        x >= self.bbox_left');condition=original[end:original.rfind('}')].strip()
    header=original[:original.index('{')+1].replace('pub fn check_collision_point_precise(','pub fn check_collision_point_unit(')
    unit='\n    #[inline(always)]\n'+header+'\n        if let Some((x,y))=crate::collision_math::unit_point_known(x,y,inst_x,inst_y,origin_x,origin_y,xscale.into_inner(),yscale.into_inner()) {return '+condition+';}\n        self.check_collision_point_precise(x,y,inst_x,inst_y,origin_x,origin_y,xscale,yscale,angle_sin,angle_cos)\n    }'
    reference='\n    #[cfg(feature="howaw_collision_contract")]\n'+original.replace('pub fn check_collision_point_precise(','pub fn check_collision_point_precise_reference(',1)
    s=s[:b]+unit+reference+s[b:];p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8')
    # E033 comparison policy: its existing exact guard also observes baseline mode.
    s=s.replace('if crate::cached_bbox::reject(inst1,inst2) {return false;}','if !crate::collision_profile::reference() && crate::cached_bbox::reject(inst1,inst2) {crate::collision_profile::reject(0);return false;}',1)
    for kind,name in enumerate(METHODS):
        a=s.index('    pub fn '+name+'(');b=close(s,s.index('{',a));body=s[a:b]
        if kind>0:
            reference='\n    #[cfg(feature="howaw_collision_contract")]\n'+body.replace('pub fn '+name+'(','pub fn '+name+'_reference(',1)
        else:reference=''
        # Choose the exact unit transform once per query, never for every pixel.
        if kind in [0,2,3]:
            loop_a=body.index('            for intersect_y');loop_b=close(body,body.index('{',loop_a));loop=body[loop_a:loop_b]
            if kind==0:
                eligible='crate::collision_math::is_unit(inst1.image_xscale.get().into_inner(),inst1.image_yscale.get().into_inner(),sin1,cos1) && crate::collision_math::is_unit(inst2.image_xscale.get().into_inner(),inst2.image_yscale.get().into_inner(),sin2,cos2)'
            else:eligible='crate::collision_math::is_unit(inst.image_xscale.get().into_inner(),inst.image_yscale.get().into_inner(),sin,cos)'
            fast=loop.replace('.check_collision_point_precise(','.check_collision_point_unit(')
            body=body[:loop_a]+'            if !crate::collision_profile::reference() && '+eligible+' {\n'+fast+'\n            } else {\n'+loop+'\n            }'+body[loop_b:]
        i=body.index('{')+1;body=body[:i]+f'\n        let _collision_detail = crate::collision_profile::enter({kind});'+body[i:]
        if kind<5:
            # Count actual first AABB exit in the original fallback; no re-evaluation.
            anchor='            return false;';pos=body.index('// First, an AABB') if kind==0 else body.index('// AABB')
            j=body.index(anchor,pos);body=body[:j]+f'            crate::collision_profile::reject({kind});\n'+body[j:]
            marker='        inst1.update_bbox(sprite1);' if kind==0 else '        inst.update_bbox(sprite);'
            stale='inst1.bbox_is_stale.get() || inst2.bbox_is_stale.get()' if kind==0 else 'inst.bbox_is_stale.get()'
            assert marker in body;body=body.replace(marker,f'        if {stale} {{crate::collision_profile::stale({kind});}}\n'+marker,1)
        s=s[:a]+body+reference+s[b:]
    for name in METHODS:
        a=s.index('    pub fn '+name+'_reference(');b=close(s,s.index('{',a));body=s[a:b]
        body=body.replace('.check_collision_point_precise(','.check_collision_point_precise_reference(').replace('self.check_collision(','self.check_collision_reference(')
        kind=METHODS.index(name);i=body.index('{')+1;body=body[:i]+f'\n        let _collision_detail = crate::collision_profile::enter({kind});'+body[i:]
        if kind<5:
            pos=body.index('// First, an AABB') if kind==0 else body.index('// AABB');j=body.index('            return false;',pos);body=body[:j]+f'            crate::collision_profile::reject({kind});\n'+body[j:]
            marker='        inst1.update_bbox(sprite1);' if kind==0 else '        inst.update_bbox(sprite);';stale='inst1.bbox_is_stale.get() || inst2.bbox_is_stale.get()' if kind==0 else 'inst.bbox_is_stale.get()'
            body=body.replace(marker,f'        if {stale} {{crate::collision_profile::stale({kind});}}\n'+marker,1)
        s=s[:a]+body+s[b:]
    marker='            if completed%60==0 {';assert marker in s;s=s.replace(marker,marker+'\n                crate::diagnostic!("[collision-window] completed={} room={}",completed,self.room.id);crate::collision_profile::report("native-window");crate::collision_profile::reset();',1)
    a=s.index('    pub fn native_after_init(');i=s.index('{',a)+1;s=s[:i]+'\n        crate::collision_profile::reset();'+s[i:]
    p.write_text(s,encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8');marker='    let mut game=Game::launch(';assert marker in s;s=s.replace(marker,'    #[cfg(target_os="vita")] {gm8emulator::collision_profile::configure(std::path::Path::new("ux0:data/howaw/e034-collision-reference.flag"))?;gm8emulator::collision_profile::calibrate();}\n'+marker,1);p.write_text(s,encoding='utf-8')
    p=root/'gm8emulator/Cargo.toml';p.write_text(p.read_text(encoding='utf-8')+'\n[[bin]]\nname="collision-detail-contract"\npath="src/bin/collision_detail_contract.rs"\nrequired-features=["vita2d","howaw_collision_contract"]\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_collision_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend(a.output);print('Collision method samples/rejection counts/calibration + exact unit pixel specialization; hardware behavior UNTESTED')
if __name__=='__main__':main()
