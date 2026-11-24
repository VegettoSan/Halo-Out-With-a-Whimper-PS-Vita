#!/usr/bin/env python3
"""Apply the E017 headless service boundary to a NEW, isolated source copy.

The existing compiler, VM, action trees and collision algorithms are retained.
Run against the pinned pristine source; never pass an earlier working copy.
"""
from pathlib import Path
import argparse,re,shutil,subprocess
BASE='9e4282e6d19f4dd00961811840ddc3e11da6dd5a'

def close(s,start,left='{',right='}'):
    # Source scanner: ignore comments/strings, Rust lifetimes are not strings.
    depth=0; i=start
    while i<len(s):
        if s.startswith('//',i):
            j=s.find('\n',i); i=len(s) if j<0 else j; continue
        if s.startswith('/*',i):
            n=1;i+=2
            while n:
                if s.startswith('/*',i):n+=1;i+=2
                elif s.startswith('*/',i):n-=1;i+=2
                else:i+=1
            continue
        if s[i]=='"':
            i+=1
            while i<len(s):
                if s[i]=='\\':i+=2
                elif s[i]=='"':i+=1;break
                else:i+=1
            continue
        if s[i]==left:depth+=1
        elif s[i]==right:
            depth-=1
            if depth==0:return i+1
        i+=1
    raise ValueError('unbalanced source')

def cfgitem(s,needle):
    at=s.index(needle); start=s.rfind('\n',0,at)+1
    return s[:start]+'#[cfg(not(feature="headless"))]\n'+s[start:]

def edit(root,name,fn):
    p=root/'gm8emulator/src'/name;s=p.read_text(encoding="utf-8");p.write_text(fn(s), encoding="utf-8")

def apply(root):
    p=root/'gm8emulator/Cargo.toml';s=p.read_text(encoding="utf-8")
    optional=['clipboard','imgui','lzzzz','ramen','rmp3','udon','libffi','crc32fast']
    for name in optional:
        pattern=rf'(?m)^{name} = (.+)$';m=re.search(pattern,s);assert m,name
        value=m[1]
        if value.startswith('{'): value=value.replace('{','{ optional = true,',1)
        else:value='{ version = '+value+', optional = true }'
        s=s[:m.start(1)]+value+s[m.end(1):]
    s+='\n[features]\ndefault = ["desktop"]\nheadless = []\ndesktop = ['+','.join('"dep:'+n+'"' for n in optional)+']\n\n[[bin]]\nname="gm8emulator"\npath="src/main.rs"\nrequired-features=["desktop"]\n\n[[bin]]\nname="howaw-vm-probe"\npath="src/bin/vm_probe.rs"\nrequired-features=["headless"]\n'
    p.write_text(s, encoding="utf-8")
    src=root/'gm8emulator/src'; assets=Path(__file__).with_name('vm')
    lib=(src/'main.rs').read_text(encoding="utf-8").split('use game::',1)[0]
    lib=lib.replace('mod ','pub mod ')
    lib='#[cfg(all(feature="desktop",feature="headless"))] compile_error!("select one frontend; use --no-default-features for headless");\n'+lib
    for name in ['imgui_key_utils','imgui_utils']:lib=lib.replace('pub mod '+name+';', '#[cfg(not(feature="headless"))]\npub mod '+name+';')
    (src/'lib.rs').write_text(lib+'\n#[cfg(feature="headless")] pub mod host;\n#[cfg(feature="headless")] pub mod heap_meter;\n', encoding="utf-8")
    shutil.copyfile(assets/'host_services.rs',src/'host.rs')
    shutil.copyfile(assets/'deferred_audio.rs',src/'game/deferred_audio.rs')
    shutil.copyfile(assets/'heap_meter.rs',src/'heap_meter.rs')
    (src/'bin').mkdir(exist_ok=True);shutil.copyfile(assets/'vm_probe.rs',src/'bin/vm_probe.rs')
    def build(s):
        s=s.replace('if cfg!(target_os = "windows") {','if !cfg!(feature="headless") && cfg!(target_os = "windows") {')
        s=s.replace('#[cfg(target_os = "windows")]','#[cfg(all(not(feature="headless"),target_os = "windows"))]')
        return s
    p=root/'gm8emulator/build.rs';p.write_text(build(p.read_text(encoding="utf-8")), encoding="utf-8")
    def game(s):
        s=s.replace('pub mod audio;', '#[cfg(not(feature="headless"))] pub mod audio;\n#[cfg(feature="headless")] #[path="game/deferred_audio.rs"] pub mod audio;')
        for name in ['recording','savestate']:s=s.replace('pub mod '+name+';', '#[cfg(not(feature="headless"))] pub mod '+name+';')
        s=s.replace('pub use savestate::SaveState;', '#[cfg(not(feature="headless"))] pub use savestate::SaveState;')
        s=s.replace('use ramen::{','#[cfg(not(feature="headless"))]\nuse ramen::{',1)
        s=s.replace('/// Structure which contains', '#[cfg(feature="headless")] use crate::host::Window;\n\n/// Structure which contains',1)
        s=s.replace('pub struct Game {','pub struct Game {\n    #[cfg(feature="headless")] pub services: Box<dyn crate::host::PlatformServices>,',1)
        s=s.replace('#[cfg(target_os = "windows")]', '#[cfg(all(not(feature="headless"),target_os = "windows"))]')
        a=s.index('        let connection = ramen::');b=s.index('        let ffmpeg_recorder',a)
        body=s[a:b];body=body.replace('        let window = builder.build()?;','        let window = builder.build()?;\n        (connection,window)')
        s=s[:a]+'        #[cfg(not(feature="headless"))]\n        let (connection, window) = {\n'+body+'        };\n        #[cfg(feature="headless")] let window = Window::deferred();\n'+s[b:]
        s=s.replace('        let mut audio = audio::AudioManager::new(', '        #[cfg(not(feature="headless"))]\n        let mut audio = audio::AudioManager::new(',1)
        s=s.replace('        let mut renderer = Renderer::new(', '        #[cfg(feature="headless")] let mut audio = audio::AudioManager::deferred();\n        #[cfg(not(feature="headless"))]\n        let mut renderer = Renderer::new(',1)
        s=s.replace('        let mut atlases = AtlasBuilder::new(', '        #[cfg(feature="headless")] let mut renderer = Renderer::prepare_headless();\n        let mut atlases = AtlasBuilder::new(',1)
        s=s.replace('GPU Max Texture Size:', 'Atlas construction limit (backend-specific):')
        a=s.index('                    let handle = match b.data');b=s.index('                    Box::new(Sound',a)
        s=s[:a]+'                    #[cfg(not(feature="headless"))]\n'+s[a:b]+'                    #[cfg(feature="headless")] let handle = FileType::Deferred { data: b.data, extension: b.extension.0 };\n'+s[b:]
        s=s.replace('let mut game = Self {','let mut game = Self {\n            #[cfg(feature="headless")] services: Box::new(crate::host::UnavailableServices),',1)
        s=s.replace('        game.window.set_visible(true);','        #[cfg(not(feature="headless"))]\n        game.window.set_visible(true);',1)
        for name in ['process_window_events','replay']:
            s=cfgitem(s,'pub fn '+name+'(')
        a=s.index('    fn resize_window(');b=close(s,s.index('{',a));original=s[a:b]
        original=original.replace('            self.renderer.resize_framebuffer', '            #[cfg(not(feature="headless"))]\n            self.renderer.resize_framebuffer',1)
        original=original.replace('                self.window.set_size', '                #[cfg(not(feature="headless"))]\n                self.window.set_size',1)
        s=s[:a]+original+s[b:]
        s=s.replace('    pub fn refresh_event_holders', '    #[cfg(feature="headless")] pub fn process_window_events(&mut self) { crate::host::unavailable(crate::host::Service::Window,"poll_events") }\n\n    pub fn refresh_event_holders',1)
        # Normal run/event pumping is a frontend operation, not core VM logic.
        s=cfgitem(s,'pub fn run(&mut self)')
        return s
    edit(root,'game.rs',game)
    def input_(s):
        for needle in ['impl TryFrom<ramen::input::Key>', 'pub fn ramen2imgui(', 'pub fn ramen2vk(', 'impl TryFrom<ramen::input::MouseButton>', 'pub fn ramen2mb(']:s=cfgitem(s,needle)
        return s
    edit(root,'input.rs',input_)
    def renderer(s):
        s=s.replace('pub mod opengl;','#[cfg(not(feature="headless"))] pub mod opengl;\n#[cfg(feature="headless")] mod headless;')
        s=s.replace('use ramen::{','#[cfg(not(feature="headless"))]\nuse ramen::{',1)
        s=cfgitem(s,'pub fn new(backend:')
        s=s.replace('impl Renderer {','impl Renderer {\n    #[cfg(feature="headless")] pub fn prepare_headless() -> Self { Self(Box::new(headless::PreparedTextures::new())) }',1)
        return s
    edit(root,'render.rs',renderer)
    # Generate a strict graphics adapter from REQUIRED trait methods. No zero/success stubs.
    render=(src/'render.rs').read_text(encoding="utf-8");a=render.index('pub trait RendererTrait');a=render.index('{',a);b=close(render,a)
    methods=[];i=a+1
    while i<b:
        m=re.search(r'\bfn\s+(\w+)\s*\(',render[i:b])
        if not m:break
        start=i+m.start();name=m[1];paren=render.index('(',start);end=close(render,paren,'(',')');j=end
        while render[j] not in '{;':
            if render[j]=='[':j=close(render,j,'[',']')
            else:j+=1
        if render[j]=='{':i=close(render,j);continue
        methods.append((name,render[start:j].strip()));i=j+1
    code='#![allow(unused_variables)]\nuse super::*;\npub struct PreparedTextures { textures: Vec<(AtlasRect,Box<[u8]>)> }\nimpl PreparedTextures { pub fn new()->Self { Self{textures:Vec::new()} } }\nimpl RendererTrait for PreparedTextures {\n'
    for name,sig in methods:
        if name=='as_any':body='self'
        elif name=='max_texture_size':body='2048'
        elif name=='get_rect':body='usize::try_from(id.0).ok().and_then(|i|self.textures.get(i)).map(|t| &t.0)'
        elif name=='push_atlases':body='let (_,textures)=atl.into_inner(); self.textures=textures; crate::heap_meter::snapshot("prepared_textures"); Ok(())'
        else:body=f'crate::host::unavailable(crate::host::Service::Graphics,"{name}")'
        code+=sig+' { '+body+' }\n'
    code+='}\n';(src/'render/headless.rs').write_text(code, encoding="utf-8")
    # Preserve audio method signatures, but never claim available output/decoding.
    audio=(src/'game/audio.rs').read_text(encoding="utf-8"); a=audio.index('impl AudioManager {'); b=close(audio,audio.index('{',a))
    added='\n#[derive(Clone,serde::Serialize,serde::Deserialize)] pub struct AudioState;\nimpl AudioManager {\n'
    for m in re.finditer(r'    pub fn (\w+)\(',audio[a:b]):
        start=a+m.start(); op=m[1]
        if op=='new':continue
        end=audio.index('{',start); sig=audio[start:end]
        added+=sig+'{ crate::host::unavailable(crate::host::Service::Audio,"'+op+'") }\n'
    added+='}\n'
    p=src/'game/deferred_audio.rs';p.write_text(p.read_text(encoding="utf-8")+added, encoding="utf-8")
    # Encoded original audio is explicitly Deferred, never represented as decoded/playing.
    edit(root,'asset/sound.rs',lambda s:s.replace('pub enum FileType {','pub enum FileType {\n    #[cfg(feature="headless")] Deferred { data: Option<Box<[u8]>>, extension: Box<[u8]> },'))
    def kernel(s):
        s=s.replace('use ramen::window::Cursor;', '#[cfg(not(feature="headless"))]\nuse ramen::window::Cursor;')
        functions=[]
        for m in re.finditer(r'(?m)^    pub fn (\w+)\(',s):
            a=s.index('{',m.start());b=close(s,a);sig=s[m.start():a];body=s[a:b];name=m[1];service=None
            if name=='external_define':continue  # retain original argument/signature validation
            if name in ['set_program_priority','set_application_title']:service='Process'
            elif name.startswith(('sound_','action_sound','cd_')) or 'self.audio' in body:service='Audio'
            elif name.startswith(('file_','directory_','ini_','export_include','disk_')) or 'std::fs' in body or 'File::' in body:service='Files'
            elif name.startswith('external_') or 'self.externals' in body:service='External'
            elif name.startswith('clipboard_'):service='Clipboard'
            elif name.startswith(('message_','show_','get_open_filename','get_save_filename','get_directory','get_color','get_integer','get_string')):service='Dialog'
            elif 'self.window' in body or 'ramen::' in body or 'platform::' in body or name.startswith(('window_','display_','keyboard_check_direct','mouse_get_','mouse_set_')):service='Window'
            elif 'Command::' in body or 'std::process' in body:service='Process'
            elif 'self.renderer' in body:service='Graphics'
            elif 'unimplemented!' in body:service='Builtin'
            if service and 'gml::Result' in sig:
                args='args' if re.search(r'\bargs\s*:',sig) else '_args'
                if '&self' in sig or '&mut self' in sig:
                    replacement=f'{{ crate::host::trace("{name}"); self.services.request(crate::host::Request {{service:crate::host::Service::{service}, operation:"{name}"}}, {args}) }}'
                else:replacement=f'{{ crate::host::trace("{name}"); Err(gml::Error::FunctionError("{name}".into(),"SERVICE_UNAVAILABLE/{service}".into())) }}'
                functions.append((m.start(),b,sig+'{\n        #[cfg(feature="headless")] '+replacement+'\n        #[cfg(not(feature="headless"))] '+body+'\n    }'))
        for a,b,new in reversed(functions):s=s[:a]+new+s[b:]
        return s
    edit(root,'gml/kernel.rs',kernel)
    def runtime(s):
        marker='        for instruction in instructions.iter() {'
        assert marker in s
        return s.replace(marker,marker+'\n            #[cfg(feature="headless")] crate::host::instruction();',1)
    edit(root,'gml/runtime.rs',runtime)
    # No native DLL/IPC setup in inspection mode; builtins block at the service interface.
    for name in ['game/external/win32.rs']:
        edit(root,name,lambda s:s.replace('#![cfg(all(', '#![cfg(all(not(feature="headless"),',1))
    edit(root,'game/external.rs',lambda s:s.replace('all(target_os = "windows", target_arch = "x86")','all(not(feature="headless"), target_os = "windows", target_arch = "x86")'))
    split_media_preparation(root)
    print('Applied headless boundary; required renderer methods:',len(methods))

def split_media_preparation(root):
    def game(s):
        s=s.replace('        #[cfg(feature="headless")] let mut renderer = Renderer::prepare_headless();\n','')
        s=s.replace('        let mut atlases = AtlasBuilder::new(renderer.max_texture_size() as _);', '        #[cfg(not(feature="headless"))]\n        let mut atlases = AtlasBuilder::new(renderer.max_texture_size() as _);\n        #[cfg(feature="headless")] let mut atlases = AtlasBuilder::new(2048);')
        s=s.replace('        println!("Atlas construction limit (backend-specific): {}", renderer.max_texture_size());', '        #[cfg(not(feature="headless"))]\n        println!("GPU Max Texture Size: {}", renderer.max_texture_size());\n        #[cfg(feature="headless")] println!("CPU texture preparation limit: 2048");')
        s=s.replace('        renderer.push_atlases(atlases)?;', '        #[cfg(not(feature="headless"))]\n        renderer.push_atlases(atlases)?;\n        #[cfg(feature="headless")] let renderer = Renderer::from_prepared_atlases(atlases);')
        return s
    edit(root,'game.rs',game)
    edit(root,'render.rs',lambda s:s.replace('pub fn prepare_headless() -> Self { Self(Box::new(headless::PreparedTextures::new())) }', 'pub fn from_prepared_atlases(atl: atlas::AtlasBuilder) -> Self { Self(Box::new(headless::PreparedTextures::from_atlases(atl))) }'))
    def renderer(s):
        s=s.replace('pub fn new()->Self { Self{textures:Vec::new()} }', 'pub fn from_atlases(atl: atlas::AtlasBuilder)->Self { let (_,textures)=atl.into_inner(); let bytes:usize=textures.iter().map(|t|t.1.len()).sum(); eprintln!("[resources] pending_texture_bytes={} texture_entries={}",bytes,textures.len()); crate::heap_meter::snapshot("prepared_textures"); Self{textures} }')
        s=s.replace('fn max_texture_size(&self) -> u32 { 2048 }', 'fn max_texture_size(&self) -> u32 { crate::host::unavailable(crate::host::Service::Graphics,"max_texture_size") }')
        s=s.replace('let (_,textures)=atl.into_inner(); self.textures=textures; crate::heap_meter::snapshot("prepared_textures"); Ok(())', 'crate::host::unavailable(crate::host::Service::Graphics,"push_atlases")')
        return s
    edit(root,'render/headless.rs',renderer)

def finish_boundaries(root):
    def external(s):
        s=s.replace('mod wow64;', '#[cfg(not(feature="headless"))] mod wow64;')
        s=s.replace('#[cfg(all(not(feature="headless"), target_os = "windows", target_arch = "x86"))]\nuse dummy as ipc;', '#[cfg(any(feature="headless",all(target_os="windows",target_arch="x86")))]\nuse dummy as ipc;')
        s=s.replace('#[cfg(not(all(not(feature="headless"), target_os = "windows", target_arch = "x86")))]\nuse wow64 as ipc;', '#[cfg(all(not(feature="headless"),not(all(target_os="windows",target_arch="x86"))))]\nuse wow64 as ipc;')
        a=s.index('    fn make_call(');a=s.index('{',a);b=close(s,a);body=s[a:b]
        return s[:a]+'{\n        #[cfg(feature="headless")] { crate::host::trace("external_define"); return Err(format!("SERVICE_UNAVAILABLE/External dll={} symbol={}", signature.dll, signature.symbol)); }\n        #[cfg(not(feature="headless"))] '+body+'\n    }'+s[b:]
    edit(root,'game/external.rs',external)
    def replay(s):
        s=s.replace('use lzzzz::lz4;', '#[cfg(not(feature="headless"))] use lzzzz::lz4;')
        s=s.replace('    DecompressErr(lzzzz::Error),','    #[cfg(not(feature="headless"))] DecompressErr(lzzzz::Error),').replace('    CompressErr(lzzzz::Error),','    #[cfg(not(feature="headless"))] CompressErr(lzzzz::Error),')
        for name in ['from_file','to_file']:s=cfgitem(s,'pub fn '+name+'(')
        return s
    edit(root,'game/replay.rs',replay)
    src=root/'gm8emulator/src';p=src/'render/opengl.rs';s=p.read_text(encoding="utf-8");a=s.index('impl From<AtlasRect> for [f32; 4]');b=close(s,s.index('{',a));conversion=s[a:b];p.write_text(s[:a]+s[b:], encoding="utf-8");p=src/'render/atlas.rs';p.write_text(p.read_text(encoding="utf-8")+'\n'+conversion+'\n', encoding="utf-8")

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[2]
    source=a.source.resolve();output=a.output.resolve()
    if not source.is_relative_to(root/'local-tools') or not output.is_relative_to(root/'local-tools') or output.exists():p.error('use a preserved local source and NEW local-tools output')
    if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=BASE:p.error('unexpected source revision')
    if subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip():p.error('source must be pristine')
    shutil.copytree(source,output,ignore=shutil.ignore_patterns('.git','target'))
    apply(output);finish_boundaries(output)
