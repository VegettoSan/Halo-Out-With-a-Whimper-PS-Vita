#!/usr/bin/env python3
"""E020: reproduce E019 in a NEW copy and attach a strict libvita2d renderer."""
import argparse,re,shutil,subprocess
from pathlib import Path
from prepare_vm_probe import close

def extend_graphics(root):
    src=root/'gm8emulator/src';own=Path(__file__).with_name('graphics')
    # Required trait coverage is generated from the compiler-checked E017 boundary.
    old=(src/'render/headless.rs').read_text(encoding='utf-8')
    backend=(own/'backend.rs').read_text(encoding='utf-8')
    implemented=set(re.findall(r'\bfn\s+(\w+)\(',backend))
    missing=[]
    for m in re.finditer(r'\bfn\s+(\w+)\(',old):
        if m[1] in implemented:continue
        end=old.index('{',m.start());sig=old[m.start():end].strip()
        missing.append(sig+' { crate::host::unavailable(crate::host::Service::Graphics,"'+m[1]+'") }')
    backend=backend.replace('// REQUIRED_UNSUPPORTED','\n'.join(missing))
    (src/'render/vita2d.rs').write_text(backend,encoding='utf-8')
    for name in ['geometry.rs','native.rs']:
        shutil.copyfile(own/name,src/'render'/name)
    shutil.copyfile(own/'vita2d_bridge.c',src/'render/vita2d_bridge.c')
    p=src/'render.rs';s=p.read_text(encoding='utf-8')
    s=s.replace('#[cfg(feature="headless")] mod headless;', '#[cfg(all(feature="headless",not(feature="vita2d")))] mod headless;\n#[cfg(feature="vita2d")] pub mod vita2d;')
    old='Self(Box::new(headless::PreparedTextures::from_atlases(atl)))'
    assert old in s
    s=s.replace(old,'{\n#[cfg(feature="vita2d")] {Self(Box::new(vita2d::Vita2d::from_atlases(atl)))}\n#[cfg(not(feature="vita2d"))] {Self(Box::new(headless::PreparedTextures::from_atlases(atl)))}\n}')
    p.write_text(s,encoding='utf-8')
    # Let real sprite builtins reach RendererTrait. Others retain explicit service stops.
    p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8')
    for name in ['draw_sprite','draw_sprite_ext','draw_sprite_part_ext','draw_background_ext','draw_background_tiled_ext']:
        a=s.index('    pub fn '+name+'(');b=close(s,s.index('{',a));body=s[a:b]
        body=body.replace('#[cfg(feature="headless")]', '#[cfg(all(feature="headless",not(feature="vita2d")))]')
        body=body.replace('#[cfg(not(feature="headless"))]', '#[cfg(any(not(feature="headless"),feature="vita2d"))]')
        s=s[:a]+body+s[b:]
    p.write_text(s,encoding='utf-8')
    p=root/'gm8emulator/Cargo.toml';s=p.read_text(encoding='utf-8').replace('headless = []','headless = []\nvita2d = ["headless"]');p.write_text(s,encoding='utf-8')
    p=root/'gm8emulator/build.rs';s=p.read_text(encoding='utf-8')
    marker='    let out = env::var("OUT_DIR")?;'
    assert marker in s
    s=s.replace(marker,marker+'''
    if env::var("CARGO_CFG_TARGET_OS").as_deref()==Ok("vita") && env::var_os("CARGO_FEATURE_VITA2D").is_some() {
        let bridge=env::var("HOWAW_GRAPHICS_LIB_DIR")?;
        println!("cargo:rerun-if-env-changed=HOWAW_GRAPHICS_LIB_DIR");
        println!("cargo:rustc-link-search=native={bridge}");
        for lib in ["howaw_graphics","vita2d","SceGxm_stub","SceDisplay_stub","SceCommonDialog_stub","SceAppMgr_stub","SceSysmodule_stub"] {
            println!("cargo:rustc-link-lib=static={lib}");
        }
        for api in ["sceGxmInitialize","sceGxmBeginScene","sceGxmDraw","sceGxmEndScene","sceGxmDisplayQueueAddEntry","sceDisplaySetFrameBuf","sceGxmTextureInitLinear"] {
            println!("cargo:rustc-link-arg=-Wl,--wrap={api}");
        }
    }
'''.rstrip())
    p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e019-{n:03}','e020-{n:03}').replace('E019_DIAGNOSTIC_STARTED','E020_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8')
    marker='diagnostics::native_memory("startup_stop");result'
    assert marker in s
    s=s.replace(marker,'''diagnostics::native_memory("startup_stop");
    diagnostic!("[startup-result-before-graphics] {:?}; original VM is not resumed or bypassed",result.as_ref().map_err(|e|e.to_string()));
    // The original engine loaded/compiled these assets. No export or substitute image.
    let sprite=game.assets.sprites.get(0).and_then(|s|s.as_ref()).ok_or("original sprite 0 missing")?;
    let frame=sprite.frames.first().ok_or("original sprite 0 frame missing")?;
    let (tex,w,h,ox,oy)=(frame.atlas_ref,frame.width,frame.height,sprite.origin_x,sprite.origin_y);
    diagnostic!("[visual-fixture] original_sprite=0 frame=0 width={} height={} origin={},{}; diagnostic resource draw, NOT original menu",w,h,ox,oy);
    game.renderer.graphics_resource(tex)?;
    #[cfg(target_os="vita")] {
        use gm8emulator::{render::Scaling,types::Colour};
        diagnostic!("[visual-begin] 360 frames; same Game.renderer/AtlasRef; startup remains BLOCKED");
        let start=std::time::Instant::now();
        let mut frame_us=Vec::with_capacity(360);
        for n in 0..360 {
            let at=std::time::Instant::now();
            game.renderer.clear_view(Colour::from(0x302010u32),1.0);
            if n<120 {
                game.renderer.draw_sprite(tex,480.-w as f64/2.+ox as f64,272.-h as f64/2.+oy as f64,1.,1.,0.,0xffffff,1.);
            } else {
                for (x,y,ang,alpha) in [(240.,140.,0.,1.),(720.,140.,30.,1.),(240.,400.,-30.,0.5),(720.,400.,0.,0.5)] {
                    game.renderer.draw_sprite(tex,x-w as f64/4.+ox as f64/2.,y-h as f64/4.+oy as f64/2.,0.5,0.5,ang,0xffffff,alpha);
                }
            }
            game.renderer.present(960,544,Scaling::Fixed(1.));
            frame_us.push(at.elapsed().as_micros() as u64);
            if n==0 || n==120 {gm8emulator::render::vita2d::readback(0xff302010)?;}
        }
        frame_us.sort_unstable();
        diagnostic!("[visual-timing] submitted_frames=360 elapsed_us={} frame_wait_inclusive_min_us={} median_us={} p95_us={} max_us={}; includes GPU finish/display queue wait and first upload/logs; readback outside samples; NOT displayed gameplay FPS",start.elapsed().as_micros(),frame_us[0],frame_us[180],frame_us[342],frame_us[359]);
        game.renderer.graphics_metrics("visual_end");heap_meter::snapshot("visual_end");diagnostics::native_memory("visual_end");
        diagnostic!("VISUAL_PROBE_COMPLETED; original startup result preserved");
    }
    #[cfg(not(target_os="vita"))] diagnostic!("[visual-host] GPU execution UNTESTED; no substitute renderer");
    result''')
    p.write_text(s,encoding='utf-8')
    print('E020 attached to Game.renderer; unsupported trait operations remain explicit')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    # E019 owns preservation guards and the explicit owner High policy.
    subprocess.run(['python',str(Path(__file__).with_name('prepare_priority_probe.py')),'--source',str(a.source),'--output',str(a.output),'--owner-dialog-high'],check=True)
    extend_graphics(a.output)
if __name__=='__main__':main()
