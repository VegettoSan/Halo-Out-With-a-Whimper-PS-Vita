#!/usr/bin/env python3
"""E019: reuse E018 in a new copy; typed priority and persistent native diagnostics."""
import argparse,shutil,subprocess
from pathlib import Path
from prepare_cleanmem_probe import extend,patch_copy,method
from prepare_vm_probe import BASE,apply,finish_boundaries

def extend_priority(root):
 src=root/'gm8emulator/src';own=Path(__file__).with_name('priority')
 for name in ['process_priority.rs','diagnostics.rs']:
  shutil.copyfile(own/name,src/name)
 shutil.copyfile(own/'sha256.rs',src/'probe_sha256.rs')
 shutil.copyfile(own/'vm_probe.rs',src/'bin/vm_probe.rs')
 shutil.copyfile(own/'contract_probe.rs',src/'bin/priority_contract_probe.rs')
 p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\n#[cfg(feature="headless")] pub mod process_priority;\n#[cfg(feature="headless")] pub mod diagnostics;\n#[cfg(feature="headless")] pub mod probe_sha256;\n',encoding='utf-8')
 p=src/'host.rs';s=p.read_text(encoding='utf-8');marker='    fn request(&self, request: Request, args: &[Value]) -> gml::Result<Value>;';assert marker in s
 s=s.replace(marker,marker+'\n    fn set_program_priority(&self, _priority:i32)->gml::Result<Value> { Err(gml::Error::FunctionError("set_program_priority".into(),"SERVICE_UNAVAILABLE/Process".into())) }')
 s=s.replace('fn request(&self, r: Request, _args: &[Value]) -> gml::Result<Value> {','fn request(&self, r: Request, args: &[Value]) -> gml::Result<Value> {\n        crate::diagnostic!("[service-stop] {:?}/{} argc={}",r.service,r.operation,args.len());')
 p.write_text(s,encoding='utf-8')
 p=src/'runtime_services.rs';s=p.read_text(encoding='utf-8');marker='impl PlatformServices for RuntimeServices {';assert marker in s
 s=s.replace(marker,marker+'\n    fn set_program_priority(&self, priority:i32)->gml::Result<Value> { crate::process_priority::set(priority) }');p.write_text(s,encoding='utf-8')
 p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8');a,b=method(s,'set_program_priority');at=s.index('        #[cfg(not(feature="headless"))]',a,b)
 s=s[:a]+'''    pub fn set_program_priority(&mut self, args: &[Value]) -> gml::Result<Value> {
        #[cfg(feature="headless")] {
            let priority=expect_args!(args,[int])?;
            crate::host::trace("set_program_priority");
            self.services.set_program_priority(priority)
        }
'''+s[at:];p.write_text(s,encoding='utf-8')
 # Route instrumentation and adapters to the persistent sink, preserving old sources.
 for name in ['host.rs','heap_meter.rs','portable_cleanmem.rs','runtime_services.rs']:
  p=src/name;s=p.read_text(encoding='utf-8').replace('eprintln!(', 'crate::diagnostic!(');p.write_text(s,encoding='utf-8')
 p=src/'heap_meter.rs';s=p.read_text(encoding='utf-8').replace('if !p.is_null(){add(l.size());}','if !p.is_null(){add(l.size());}else{crate::diagnostics::allocation_failed(l.size(),l.align());}').replace('if !q.is_null(){LIVE.fetch_sub(l.size(),Ordering::Relaxed);add(n);}','if !q.is_null(){LIVE.fetch_sub(l.size(),Ordering::Relaxed);add(n);}else{crate::diagnostics::allocation_failed(n,l.align());}')
 p.write_text(s,encoding='utf-8')
 p=root/'gm8emulator/Cargo.toml';p.write_text(p.read_text(encoding='utf-8')+'\n[[bin]]\nname="priority-contract-probe"\npath="src/bin/priority_contract_probe.rs"\nrequired-features=["headless"]\n',encoding='utf-8')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--owner-dialog-high',action='store_true',help='explicit owner-selected E019 diagnostic policy, native only unless host flag supplied');a=p.parse_args()
 repo=Path(__file__).resolve().parents[2];source=a.source.resolve();out=a.output.resolve()
 if not source.is_relative_to(repo/'local-tools') or not out.is_relative_to(repo/'local-tools') or out.exists():p.error('pristine local source, NEW local-tools output required')
 if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=BASE or subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip():p.error('wrong or modified upstream')
 shutil.copytree(source,out,ignore=shutil.ignore_patterns('.git','target'))
 for name in ['0001-show-message-ext.patch','0002-classic-ini-write-through.patch']:patch_copy(out,repo/'patches/opengmk'/name)
 apply(out);finish_boundaries(out);extend(out,source);extend_priority(out)
 if a.owner_dialog_high:
  src=out/'gm8emulator/src';shutil.copyfile(Path(__file__).with_name('priority')/'owner_dialog_high.rs',src/'owner_dialog_high.rs')
  p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\n#[cfg(feature="headless")] pub mod owner_dialog_high;\n',encoding='utf-8')
  p=src/'runtime_services.rs';s=p.read_text(encoding='utf-8');marker='        if !self.interactive_dialog {';assert marker in s
  s=s.replace(marker,'        if let Some(answer)=crate::owner_dialog_high::answer(request) { return answer; }\n'+marker,1);p.write_text(s,encoding='utf-8')
 print('E019 prepared; original compiler/VM preserved; no data or dependency changes')
