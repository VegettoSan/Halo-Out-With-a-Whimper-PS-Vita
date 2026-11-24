#!/usr/bin/env python3
"""Prepare E018 in a fresh local copy, reusing the E017 core and E015 adapters."""
import argparse,re,shutil,subprocess
from pathlib import Path
from prepare_vm_probe import BASE,apply,finish_boundaries,close

def patch_copy(root,patch):
    # Apply the existing small public E015 patches to COPIES, checking context.
    lines=patch.read_text(encoding='utf-8').splitlines(); i=0
    while i<len(lines):
        if not lines[i].startswith('--- a/'):
            i+=1;continue
        relative=lines[i][6:];i+=1
        assert lines[i]=='+++ b/'+relative;i+=1
        p=root/relative;original=p.read_text(encoding='utf-8').splitlines();cursor=0;out=[]
        while i<len(lines) and not lines[i].startswith(('diff --git','--- a/')):
            if not lines[i].startswith('@@ '):i+=1;continue
            m=re.match(r'@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@',lines[i]);assert m
            start=int(m[1])-1;i+=1;old=[];new=[]
            while i<len(lines) and not lines[i].startswith(('@@ ','diff --git','--- a/')):
                line=lines[i]
                if line.startswith((' ','-')):old.append(line[1:])
                if line.startswith((' ','+')):new.append(line[1:])
                i+=1
            assert original[start:start+len(old)]==old,(relative,start)
            out+=original[cursor:start]+new;cursor=start+len(old)
        out+=original[cursor:];p.write_text('\n'.join(out)+'\n',encoding='utf-8')

def method(s,name):
    a=s.index('    pub fn '+name+'(');return a,close(s,s.index('{',a))

def extend(root,reference):
    src=root/'gm8emulator/src';own=Path(__file__).with_name('cleanmem')
    for name in ['portable_cleanmem.rs','runtime_services.rs']:
        shutil.copyfile(own/name,src/name)
    shutil.copyfile(own/'contract_probe.rs',src/'bin/cleanmem_contract_probe.rs')
    shutil.copyfile(Path(__file__).with_name('message_dialog.rs'),src/'game/platform/message_dialog.rs')
    p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\n#[cfg(feature="headless")] pub mod portable_cleanmem;\n#[cfg(feature="headless")] pub mod runtime_services;\n',encoding='utf-8')
    p=src/'host.rs';s=p.read_text(encoding='utf-8');marker='    fn request(&self, request: Request, args: &[Value]) -> gml::Result<Value>;'
    s=s.replace(marker,marker+'''
    fn call_external(&self, _binding:crate::portable_cleanmem::Binding, _args:&[Value]) -> gml::Result<Value> {
        Err(gml::Error::FunctionError("external_call".into(),"SERVICE_UNAVAILABLE/External".into()))
    }
    fn show_message_ext(&self, _request:&crate::runtime_services::MessageDialog) -> Result<i32,String> {
        Err("SERVICE_UNAVAILABLE/Dialog".into())
    }
''');p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8').replace('services: Box::new(crate::host::UnavailableServices)','services: Box::new(crate::runtime_services::RuntimeServices {interactive_dialog:false})')
    marker='            match &external.call {';assert s.count(marker)==1
    s=s.replace(marker,marker+'\n                #[cfg(feature="headless")] external::Call::Adapted(binding) => self.services.call_external(*binding,args),',1);p.write_text(s,encoding='utf-8')
    p=src/'game/external.rs';s=p.read_text(encoding='utf-8').replace('pub enum Call {','pub enum Call {\n    #[cfg(feature="headless")] Adapted(crate::portable_cleanmem::Binding),',1)
    old='crate::host::trace("external_define"); return Err(format!("SERVICE_UNAVAILABLE/External dll={} symbol={}", signature.dll, signature.symbol));'
    assert old in s
    s=s.replace(old,'''crate::host::trace("external_define");
            return match crate::portable_cleanmem::bind(signature)? {
                Some(binding)=>Ok(Call::Adapted(binding)),
                None=>Err(format!("SERVICE_UNAVAILABLE/External dll={} symbol={}",signature.dll,signature.symbol)),
            };''',1);p.write_text(s,encoding='utf-8')
    p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8');base=(reference/'gm8emulator/src/gml/kernel.rs').read_text(encoding='utf-8')
    for name in ['external_call','external_free']:
        a,b=method(s,name);x,y=method(base,name);s=s[:a]+base[x:y]+s[b:]
    a,b=method(s,'show_message_ext');at=s.index('        #[cfg(not(feature="headless"))]',a,b);desktop=s[at:b]
    sig='    pub fn show_message_ext(&mut self, args: &[Value]) -> gml::Result<Value> {'
    headless='''
        #[cfg(feature="headless")] {
            let (message,button1,button2,button3)=expect_args!(args,[bytes,bytes,bytes,bytes])?;
            let request=crate::runtime_services::MessageDialog {
                text:self.decode_str(message.as_ref()).into_owned(),
                buttons:[button1,button2,button3].map(|s|self.decode_str(s.as_ref()).into_owned()),
            };
            let result=self.services.show_message_ext(&request)
                .map_err(|e|gml::Error::FunctionError("show_message_ext".into(),e))?;
            self.input.keyboard_clear_all();self.input.mouse_clear_all();
            Ok(result.into())
        }
'''
    s=s[:a]+sig+headless+desktop+s[b:];p.write_text(s,encoding='utf-8')
    p=root/'gm8emulator/Cargo.toml';p.write_text(p.read_text(encoding='utf-8')+'\n[[bin]]\nname="cleanmem-contract-probe"\npath="src/bin/cleanmem_contract_probe.rs"\nrequired-features=["headless"]\n',encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8');marker=' let scripts=game.assets.scripts.iter().flatten().count();'
    assert marker in s
    s=s.replace(marker,''' #[cfg(windows)] { game.services=Box::new(gm8emulator::runtime_services::RuntimeServices {interactive_dialog:std::env::args_os().any(|a|a=="--interactive-dialog")}); }
'''+marker,1);p.write_text(s,encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    repo=Path(__file__).resolve().parents[2];source=a.source.resolve();out=a.output.resolve()
    if not source.is_relative_to(repo/'local-tools') or not out.is_relative_to(repo/'local-tools') or out.exists():p.error('use preserved local source and NEW local-tools output')
    if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=BASE:p.error('unexpected base')
    if subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip():p.error('source must be pristine')
    shutil.copytree(source,out,ignore=shutil.ignore_patterns('.git','target'))
    for name in ['0001-show-message-ext.patch','0002-classic-ini-write-through.patch']:patch_copy(out,repo/'patches/opengmk'/name)
    apply(out);finish_boundaries(out);extend(out,source)
    print('E018 prepared from E017 plus preserved E015 dialog/INI patches')
