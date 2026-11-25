#!/usr/bin/env python3
"""E022: reuse the existing OpenGMK MP3 player and cached decoder, no output shim."""
import argparse,re,shutil,subprocess
from pathlib import Path
from prepare_vm_probe import close

def extend_mp3(root,reference,source_trait):
    src=root/'gm8emulator/src';own=Path(__file__).with_name('mp3')
    # Keep the upstream GM8 player policies; only detach the host audio interface,
    # initialize its scratch buffer, and share the owned compressed allocation.
    s=(reference/'gm8emulator/src/game/audio/mp3.rs').read_text(encoding='utf-8')
    s=s.replace('use udon::source::','use crate::audio_source::').replace('file: Arc<[u8]>','file: Arc<Box<[u8]>>')
    s=s.replace('let alloc = alloc::alloc(layout);','let alloc = alloc::alloc_zeroed(layout);')
    s=s.replace('                file: file.into(),','                file: Arc::new(file.into_boxed_slice()),')
    s+='\nimpl Mp3Player { pub fn encoded_len(&self)->usize {self.file.len()} pub fn encoded_owners(&self)->usize {Arc::strong_count(&self.file)} }\n'
    (src/'game/audio_mp3.rs').write_text(s,encoding='utf-8')
    s=source_trait.read_text(encoding='utf-8').replace('pub mod consts;','')
    (src/'audio_source.rs').write_text(s,encoding='utf-8')
    # Retain every unavailable output operation with its existing signature.
    old=(src/'game/deferred_audio.rs').read_text(encoding='utf-8')
    unsupported=[]
    for m in re.finditer(r'    pub fn (\w+)\(',old):
        if m[1] in ['deferred','add_mp3']:continue
        end=close(old,old.index('{',m.start()));unsupported.append(old[m.start():end])
    s=(own/'registered_audio.rs').read_text(encoding='utf-8').replace('// UNSUPPORTED_METHODS','\n'.join(unsupported))
    (src/'game/deferred_audio.rs').write_text(s,encoding='utf-8')
    p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\n#[cfg(feature="headless")] pub mod audio_source;\n',encoding='utf-8')
    p=root/'gm8emulator/Cargo.toml';s=p.read_text(encoding='utf-8')
    s=s.replace('features = ["float"]','features = ["float"], default-features = false')
    s=s.replace('vita2d = ["headless"]','vita2d = ["headless","dep:rmp3"]')
    s=s.replace('desktop = [','desktop = ["rmp3/simd",',1)
    s+='\n[[bin]]\nname="mp3-contract-probe"\npath="src/bin/mp3_contract_probe.rs"\nrequired-features=["vita2d"]\n'
    p.write_text(s,encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8')
    marker='    game.renderer.graphics_metrics("startup_stop");'
    s=s.replace(marker,marker+'\n    crate_layout(&game);')
    s+='\nfn crate_layout(game:&Game) { diagnostic!("[draw-layout] room={} size={}x{} views_enabled={} visible_views={:?}",game.room.id,game.room.width,game.room.height,game.room.views_enabled,game.room.views.iter().filter(|v|v.visible).map(|v|(v.source_x,v.source_y,v.source_w,v.source_h,v.port_x,v.port_y,v.port_w,v.port_h,v.angle.into_inner())).collect::<Vec<_>>()); }\n'
    p.write_text(s,encoding='utf-8')
    shutil.copyfile(own/'contract_probe.rs',src/'bin/mp3_contract_probe.rs')
    p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8');a=s.index('    pub fn sound_replace(');b=close(s,s.index('{',a));body=s[a:b]
    marker='        #[cfg(not(feature="headless"))]';at=body.index(marker)
    s=s[:a]+body[:body.index('{')+1]+'\n'+(own/'replace_body.rs').read_text(encoding='utf-8')+body[at:]+s[b:]
    # Existing native string/asset conversion and arity checking remain in force.
    p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8')
    marker='''        if self.play_type != PlayType::Record {
            let w: i32 = self.window_inner_size.0.try_into().unwrap();'''
    assert s.count(marker)==1
    s=s.replace(marker,marker.replace('self.play_type != PlayType::Record','self.play_type != PlayType::Record && self.ffmpeg_recorder.is_some()'))
    p.write_text(s,encoding='utf-8')
    p=src/'game/draw.rs';s=p.read_text(encoding='utf-8')
    marker='    pub fn draw(&mut self) -> gml::Result<()> {';assert marker in s
    s=s.replace(marker,marker+'''
        #[cfg(feature="vita2d")] crate::diagnostic!("[original-draw-enter] room={} original Game::draw; no forced draw after error",self.room.id);
        #[cfg(all(feature="vita2d",not(target_os="vita")))] { return Err(gml::Error::FunctionError("native_frame_begin".into(),"SERVICE_UNAVAILABLE/Graphics: native GXM execution requires Vita; no simulated host frame".into())); }
''',1)
    marker='''        } else {
            self.renderer.clear_zbuf();
        }'''
    assert s.count(marker)==1
    # RendererTrait clear_zbuf has no error return. Keep the known missing operation
    # a structured service error at the existing fallible call site, not fake clear.
    s=s.replace(marker,'''        } else {
            #[cfg(feature="vita2d")] {
                crate::diagnostic!("[graphics-stop] clear_zbuf required by original room; depth-only clear not implemented");
                return Err(gml::Error::FunctionError("clear_zbuf".into(),"SERVICE_UNAVAILABLE/Graphics: real depth-only clear required".into()));
            }
            #[cfg(not(feature="vita2d"))] self.renderer.clear_zbuf();
        }''',1)
    p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e021-{n:03}','e022-{n:03}').replace('E021_DIAGNOSTIC_STARTED','E022_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    repo=Path(__file__).resolve().parents[2]
    trait=a.udon_source.resolve()
    if not trait.is_relative_to(repo/'local-tools') or not trait.is_file():p.error('existing local cached udon source.rs required')
    subprocess.run(['python',str(Path(__file__).with_name('prepare_menu_probe.py')),'--source',str(a.source),'--output',str(a.output)],check=True)
    extend_mp3(a.output,a.source,trait)
    print('E022: existing rmp3/player enabled, actual registration; output services remain unavailable')
if __name__=='__main__':main()
