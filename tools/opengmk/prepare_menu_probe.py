#!/usr/bin/env python3
"""E021: extend E020 in a fresh copy; real startup only, no logo fixture."""
import argparse,shutil,subprocess
from pathlib import Path
from prepare_vm_probe import close

def enable(root,names):
    p=root/'gm8emulator/src/gml/kernel.rs';s=p.read_text(encoding='utf-8')
    for name in names:
        a=s.index('    pub fn '+name+'(');b=close(s,s.index('{',a));old=s[a:b]
        marker='        #[cfg(not(feature="headless"))] '
        at=old.index(marker);sig=old[:old.index('{')]
        body=old[at+len(marker):].rstrip();assert body.endswith('}')
        body=body[:-1].rstrip()  # discard the outer method brace, keep its original body
        s=s[:a]+sig+body+s[b:]
    p.write_text(s,encoding='utf-8')

def extend_menu(root):
    src=root/'gm8emulator/src';own=Path(__file__).with_name('menu')
    desktop_kernel=(src/'gml/kernel.rs').read_text(encoding='utf-8')
    for name in ['priority','files','files_contract']:shutil.copyfile(own/(name+'.rs'),src/('menu_'+name+'.rs'))
    p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\n#[cfg(feature="headless")] pub mod menu_priority;\n#[cfg(feature="headless")] pub mod menu_files;\n#[cfg(feature="headless")] pub mod menu_files_contract;\n',encoding='utf-8')
    p=src/'runtime_services.rs';s=p.read_text(encoding='utf-8').replace('crate::process_priority::set(priority)','crate::menu_priority::set(priority)')
    s=s.replace('UnavailableServices.request(r,args)', '{ crate::diagnostic!("[service-request] {:?}/{} args={:?}",r.service,r.operation,args); UnavailableServices.request(r,args) }')
    p.write_text(s,encoding='utf-8')
    enable(root,['file_exists','ini_open','ini_close','ini_read_string','ini_read_real','ini_write_string','ini_write_real','ini_key_exists','ini_section_exists'])
    p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8')
    a=s.index('    pub fn file_exists(');b=close(s,s.index('{',a))
    s=s[:a]+'''    pub fn file_exists(&self,args:&[Value])->gml::Result<Value> {
        crate::host::trace("file_exists");
        match expect_args!(args,[any])? {
            Value::Str(name)=>crate::menu_files::exists(&self.decode_str(name.as_ref())).map(|v|v.into()).map_err(|e|gml::Error::FunctionError("file_exists".into(),e)),
            Value::Real(_)=>Ok(gml::FALSE.into()),
        }
    }'''+s[b:]
    a=s.index('    pub fn ini_open(');b=close(s,s.index('{',a));body=s[a:b]
    body=body.replace('        let name_str = self.decode_str(name.as_ref());','''        crate::host::trace("ini_open");
        let physical=crate::menu_files::resolve(&self.decode_str(name.as_ref())).map_err(|e|gml::Error::FunctionError("ini_open".into(),e))?;
        let name=self.encode_str_maybe(physical.to_str().ok_or_else(||gml::Error::FunctionError("ini_open".into(),"path encoding".into()))?).ok_or_else(||gml::Error::FunctionError("ini_open".into(),"path encoding".into()))?.into_owned().into();
        let name_str = self.decode_str(name.as_ref());''')
    body=body.replace('if file::file_exists(&file::to_path(&name_str)) {','if physical.try_exists().map_err(|e|gml::Error::FunctionError("ini_open".into(),e.to_string()))? {')
    s=s[:a]+body+s[b:]
    # Preserve E015's write-through behavior and add durable sync/error propagation.
    a=s.index('    fn persist_classic_ini(');b=close(s,s.index('{',a));body=s[a:b]
    body=body.replace('.map_err(|e| gml::Error::FunctionError("ini_write".into(), e.to_string())),','.map_err(|e| gml::Error::FunctionError("ini_write".into(), e.to_string()))\n                .and_then(|_|crate::menu_files::sync(&self.decode_str(path.as_ref())).map_err(|e|gml::Error::FunctionError("ini_write".into(),e))),')
    s=s[:a]+body+s[b:]
    # infer stored GML-string type explicitly, preserving original representation.
    s=s.replace('let name=self.encode_str_maybe(physical.', 'let name:gml::String=self.encode_str_maybe(physical.')
    for name in ['ini_close','ini_read_string','ini_read_real','ini_write_string','ini_write_real','ini_key_exists','ini_section_exists']:
        a=s.index('    pub fn '+name+'(');at=s.index('{',a)+1;s=s[:at]+'\n        crate::host::trace("'+name+'");'+s[at:]
    a=s.index('    pub fn ini_close(');b=close(s,s.index('{',a));body=s[a:b]
    body=body.replace('                    self.open_ini = None;','                    crate::menu_files::sync(&self.decode_str(path.as_ref())).map_err(|e|gml::Error::FunctionError("ini_close".into(),e))?;\n                    self.open_ini = None;')
    s=s[:a]+body+s[b:]
    # Preserve the existing desktop implementation byte-for-byte inside its cfg body.
    for name in ['file_exists','ini_open','ini_close','ini_read_string','ini_read_real','ini_write_string','ini_write_real','ini_key_exists','ini_section_exists','persist_classic_ini']:
        prefix='    fn ' if name=='persist_classic_ini' else '    pub fn '
        a=s.index(prefix+name+'(');op=s.index('{',a);b=close(s,op)
        da=desktop_kernel.index(prefix+name+'(');do=desktop_kernel.index('{',da);db=close(desktop_kernel,do);original=desktop_kernel[do:db]
        marker='#[cfg(not(feature="headless"))] '
        if marker in original:
            start=original.index('{',original.index(marker)+len(marker));original=original[start:close(original,start)]
        headless=s[op:b]
        s=s[:op]+'{\n#[cfg(feature="headless")] '+headless+'\n#[cfg(not(feature="headless"))] '+original+'\n    }'+s[b:]
    p.write_text(s,encoding='utf-8')
    # Start from the durable E019 harness, removing the E020 visual fixture entirely.
    s=Path(__file__).with_name('priority').joinpath('vm_probe.rs').read_text(encoding='utf-8')
    s=s.replace('Game::launch(assets,input,','Game::launch(assets,input.clone(),')
    marker='    diagnostic!("[vm-start] unchanged Game::init");'
    s=s.replace(marker,'''    let profile=input.parent().unwrap().join("e021-profile");
    gm8emulator::menu_files::initialize(input.parent().unwrap().to_path_buf(),profile)?;
'''+marker)
    s=s.replace('diagnostics::native_memory("startup_stop");result','''diagnostics::native_memory("startup_stop");
    game.renderer.graphics_metrics("startup_stop");
    #[cfg(windows)] if std::env::args_os().any(|a|a=="--files-contract") { gm8emulator::menu_files_contract::run(&mut game)?; }
    result''')
    s=s.replace('    let result=game.init();','    let started=std::time::Instant::now();\n    let result=game.init();\n    diagnostic!("[startup-time] elapsed_us={} includes real file/INI synchronization; no gameplay frame executed",started.elapsed().as_micros());')
    (src/'bin/vm_probe.rs').write_text(s,encoding='utf-8')
    # Record actual entry into room loading and events without changing control flow.
    p=src/'game.rs';s=p.read_text(encoding='utf-8')
    s=s.replace('        // Load first room\n        self.load_room', '        #[cfg(feature="headless")] crate::diagnostic!("[vm-phase] library/extension init completed; entering first original room");\n        // Load first room\n        self.load_room')
    p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e020-{n:03}','e021-{n:03}').replace('E020_DIAGNOSTIC_STARTED','E021_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_graphics_probe.py')),'--source',str(a.source),'--output',str(a.output)],check=True)
    extend_menu(a.output)
    print('E021 startup services prepared; original VM and E020 backend retained')
if __name__=='__main__':main()
