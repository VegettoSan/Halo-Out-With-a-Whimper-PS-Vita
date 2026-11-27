#!/usr/bin/env python3
"""Audit explicit unit-loop alternatives while preserving original fallback text."""
import argparse,re,json,hashlib
from pathlib import Path
from audit_vm_probe import FILES,method,strip_profile
from prepare_vm_probe import close
from prepare_collision_detail_probe import METHODS

def normalize(s):
    s=strip_profile(s)
    s=re.sub(r'\n        let _collision_detail = crate::collision_profile::enter\([0-6]\);','',s)
    s=re.sub(r'\n            crate::collision_profile::reject\([0-6]\);','',s)
    s=re.sub(r'\n        if (?:inst1.bbox_is_stale.get\(\) \|\| inst2.bbox_is_stale.get\(\)|inst.bbox_is_stale.get\(\)) \{crate::collision_profile::stale\([0-6]\);\}','',s)
    guard='\n        if !crate::collision_profile::reference() && crate::cached_bbox::reject(inst1,inst2) {crate::collision_profile::reject(0);return false;}'
    s=s.replace(guard,'')
    for kind,helper,args in [(1,'reject_point','x,y'),(2,'reject_rectangle','x1,y1,x2,y2'),(3,'reject_range','x1,y1,x2,y2'),(4,'reject_range','x1,y1,x2,y2')]:
        s=s.replace(f'\n        if !crate::collision_profile::reference() && crate::cached_bbox::{helper}(inst,{args}) {{crate::collision_profile::reject({kind});return false;}}','')
    marker='            if !crate::collision_profile::reference() && crate::collision_math::is_unit('
    while marker in s:
        a=s.index(marker);first=s.index('{',a);end=close(s,first);assert s[end:end+7]==' else {'
        second=end+6;last=close(s,second);inner=s[second+1:last-1];assert inner.startswith('\n') and inner.endswith('\n            ')
        fallback=inner[1:-13];fast=s[first+1:end-1];assert fast.strip()==fallback.replace('.check_collision_point_precise(','.check_collision_point_unit(').strip()
        s=s[:a]+fallback+s[last:]
    return s

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[2]
    if not a.report.resolve().is_relative_to(root/'reports/local') or a.report.exists():p.error('NEW ignored report required')
    orig=a.source/'gm8emulator/src';work=a.work/'gm8emulator/src';checks={}
    for name in FILES:
        if name!='asset/sprite.rs':checks[name]=(orig/name).read_text(encoding='utf-8')==strip_profile((work/name).read_text(encoding='utf-8'))
    before=(orig/'game.rs').read_text(encoding='utf-8');after=(work/'game.rs').read_text(encoding='utf-8')
    for name in METHODS:
        checks[name+'_fallback']=method(before,name)==normalize(method(after,name))
        reference=normalize(method(after,name+'_reference'))
        for n in METHODS+['check_collision_point_precise']:reference=reference.replace(n+'_reference(',n+'(')
        checks[name+'_reference']=reference==method(before,name)
    checks['frame']=method(before,'frame')==method(after,'frame')
    sprite_before=(orig/'asset/sprite.rs').read_text(encoding='utf-8');sprite_after=(work/'asset/sprite.rs').read_text(encoding='utf-8')
    checks['generic_pixel_method_unchanged']=method(sprite_before,'check_collision_point_precise')==method(sprite_after,'check_collision_point_precise')
    checks['pixel_reference']=method(sprite_before,'check_collision_point_precise')==method(sprite_after,'check_collision_point_precise_reference').replace('pub fn check_collision_point_precise_reference(','pub fn check_collision_point_precise(',1)
    for file in ['collision_math.rs','collision_profile.rs','cached_bbox.rs']:checks[file+'_exact_copy']=(work/file).read_bytes()==Path(__file__).with_name(file).read_bytes()
    checks['lockfile_unchanged']=(a.source/'Cargo.lock').read_bytes()==(a.work/'Cargo.lock').read_bytes()
    checks['VM_except_counter']=(orig/'gml/runtime.rs').read_text(encoding='utf-8')==strip_profile((work/'gml/runtime.rs').read_text(encoding='utf-8').replace('\n            #[cfg(feature="headless")] crate::host::instruction();',''))
    with a.report.open('x',encoding='utf-8') as f:json.dump({'checks':checks,'result':'PASS' if all(checks.values()) else 'FAIL','scope':'explicit new fast loops; generic fallback/pixels/events/frame preserved; semantics require differential contract too'},f,indent=2)
    print(f'Collision detail delta audit {sum(checks.values())}/{len(checks)} PASS');raise SystemExit(0 if all(checks.values()) else 1)
if __name__=='__main__':main()
