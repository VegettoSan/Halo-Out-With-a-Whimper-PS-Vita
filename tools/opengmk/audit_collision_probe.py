#!/usr/bin/env python3
"""Audit the explicit cached-box delta without claiming collision source identity."""
import argparse,hashlib,json
from pathlib import Path
from audit_vm_probe import FILES,method,strip_profile

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[2]
    if not a.report.resolve().is_relative_to(root/'reports/local') or a.report.exists():p.error('write NEW ignored reports/local result')
    source=a.source/'gm8emulator/src';work=a.work/'gm8emulator/src'
    checks={f:(source/f).read_text(encoding='utf-8')==strip_profile((work/f).read_text(encoding='utf-8')) for f in FILES}
    original=(source/'game.rs').read_text(encoding='utf-8');changed=(work/'game.rs').read_text(encoding='utf-8')
    guard='\n        if crate::cached_bbox::reject(inst1,inst2) {return false;}'
    before=method(original,'check_collision');after=strip_profile(method(changed,'check_collision'))
    checks['explicit_guard_once']=after.count(guard)==1
    checks['collision_fallback_byte_identical']=after.replace(guard,'',1)==before
    checks['test_reference_byte_identical']=strip_profile(method(changed,'check_collision_reference')).replace('pub fn check_collision_reference(','pub fn check_collision(',1)==before
    checks['approved_helper_exact_copy']=(work/'cached_bbox.rs').read_bytes()==Path(__file__).with_name('cached_bbox.rs').read_bytes()
    for name in ['frame','check_collision_point','check_collision_rectangle','check_collision_ellipse','check_collision_line','check_collision_solid','check_collision_any']:
        checks[name]=method(original,name)==strip_profile(method(changed,name))
    vm=(work/'gml/runtime.rs').read_text(encoding='utf-8').replace('\n            #[cfg(feature="headless")] crate::host::instruction();','')
    checks['VM_except_counter']=(source/'gml/runtime.rs').read_text(encoding='utf-8')==strip_profile(vm)
    checks['lockfile_unchanged']=(a.source/'Cargo.lock').read_bytes()==(a.work/'Cargo.lock').read_bytes()
    result={'checks':checks,'helper_sha256':hashlib.sha256((work/'cached_bbox.rs').read_bytes()).hexdigest(),'scope':'collision method explicitly changed; all overlap/stale paths retain original fallback, no pair iteration/event ordering changes; validate semantics with collision-contract separately'}
    with a.report.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(f'Collision delta audit: {sum(checks.values())}/{len(checks)} PASS; collision method identity intentionally not claimed');raise SystemExit(0 if all(checks.values()) else 1)
if __name__=='__main__':main()
