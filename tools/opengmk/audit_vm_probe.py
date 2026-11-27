#!/usr/bin/env python3
"""Verify that E017 retains the original compiler/VM/gameplay implementation."""
import argparse,hashlib,json,re
from pathlib import Path
from prepare_vm_probe import close
FILES=['action.rs','gml/compiler.rs','gml/context.rs','gml/value.rs','gml/ds.rs','instance.rs','instancelist.rs','game/events.rs','game/movement.rs','asset/object.rs','asset/sprite.rs','asset/room.rs']
def digest(data):return hashlib.sha256(data).hexdigest()
def strip_profile(s):
 return re.sub(r'\n        #\[cfg\(feature="howaw_perf"\)\] let _howaw_perf = crate::performance::(?:scope\(crate::performance::Stage::(?:Render|Collision|Submit|Diagnostic)\)|gml\(\)|event\(event_id\));','',s)
def method(source,name):
 a=source.index('    pub fn '+name+'(');return source[a:close(source,source.index('{',a))]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 root=Path(__file__).resolve().parents[2];report=a.report.resolve()
 if not report.is_relative_to(root/'reports/local'):p.error('report must stay under ignored reports/local/')
 source=a.source/'gm8emulator/src';work=a.work/'gm8emulator/src'
 checks={f:(source/f).read_text(encoding='utf-8')==strip_profile((work/f).read_text(encoding='utf-8')) for f in FILES}
 original=(source/'gml/runtime.rs').read_text(encoding="utf-8");modified=(work/'gml/runtime.rs').read_text(encoding="utf-8").replace('\n            #[cfg(feature="headless")] crate::host::instruction();','')
 checks['VM_except_counter']=original==strip_profile(modified)
 for name in ['check_collision','check_collision_point','check_collision_rectangle','check_collision_ellipse','check_collision_line','check_collision_solid','check_collision_any']:
  checks[name]=method((source/'game.rs').read_text(encoding="utf-8"),name)==strip_profile(method((work/'game.rs').read_text(encoding="utf-8"),name))
 checks['external_define_original_validation']=method((source/'gml/kernel.rs').read_text(encoding="utf-8"),'external_define')==method((work/'gml/kernel.rs').read_text(encoding="utf-8"),'external_define')
 checks['lockfile_unchanged']=(a.source/'Cargo.lock').read_bytes()==(a.work/'Cargo.lock').read_bytes()
 report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(checks,indent=2), encoding="utf-8")
 print(f'Reuse audit: {sum(checks.values())}/{len(checks)} PASS');raise SystemExit(0 if all(checks.values()) else 1)
if __name__=='__main__':main()
