#!/usr/bin/env python3
"""E024: real controller/touch frontend and the original normal frame loop."""
import argparse,subprocess,shutil
from pathlib import Path
from prepare_vm_probe import close

def extend_input(root,reference):
    src=root/'gm8emulator/src';own=Path(__file__).with_name('input')
    for name,dest in [('mapper.rs','input_mapper.rs'),('native.rs','native_input.rs'),('contract.rs','bin/input_contract.rs')]:shutil.copyfile(own/name,src/dest)
    p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\n#[cfg(feature="vita2d")] pub mod input_mapper;\n#[cfg(feature="vita2d")] pub mod native_input;\n',encoding='utf-8')
    p=root/'gm8emulator/Cargo.toml';p.write_text(p.read_text(encoding='utf-8')+'\n[[bin]]\nname="input-contract"\npath="src/bin/input_contract.rs"\nrequired-features=["vita2d"]\n',encoding='utf-8')
    p=root/'gm8emulator/build.rs';s=p.read_text(encoding='utf-8').replace('"SceSysmodule_stub"]','"SceSysmodule_stub","SceCtrl_stub","SceTouch_stub"]');p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8')
    marker='#[cfg(feature="headless")] pub fn process_window_events(&mut self) { crate::host::unavailable(crate::host::Service::Window,"poll_events") }'
    assert marker in s
    s=s.replace(marker,'''#[cfg(feature="headless")] pub fn process_window_events(&mut self) {
        #[cfg(feature="vita2d")] if let Err(e)=crate::native_input::poll(self) {panic!("INPUT_FAIL {}",e);}
        #[cfg(not(feature="vita2d"))] crate::host::unavailable(crate::host::Service::Window,"poll_events");
    }''')
    # Reuse the complete upstream run loop, scene-change macro, timing and end
    # behavior; only remove the already-completed init and bound the diagnostic.
    original=(reference/'gm8emulator/src/game.rs').read_text(encoding='utf-8')
    a=original.index('    pub fn run(&mut self)');b=close(original,original.index('{',a));body=original[a:b]
    body=body.replace('pub fn run(&mut self)','pub fn native_after_init(&mut self,max_frames:u32)')
    body=body.replace('        self.init()?;','        let mut completed=0u32;\n        let session_start=Instant::now();\n        let mut frame_us=Vec::<u64>::new();',1)
    body=body.replace('            self.process_window_events();','            let cpu_start=Instant::now();\n            self.process_window_events();',1)
    marker='            self.frame()?;'
    body=body.replace(marker,marker+'''
            completed+=1;frame_us.push(cpu_start.elapsed().as_micros() as u64);
            if completed<=3 || completed%60==0 {
                crate::diagnostic!("[original-frame] completed={} room={} speed={} instructions={} cpu_gpu_wait_us={} elapsed_us={}",completed,self.room.id,self.room.speed,crate::host::counts().0,frame_us.last().unwrap(),session_start.elapsed().as_micros());
                self.renderer.graphics_metrics("native_frames");crate::heap_meter::snapshot("native_frames");crate::diagnostics::native_memory("native_frames");
            }
            if completed==1 || completed==60 {crate::render::vita2d::inspect_original_frame()?;}
            if completed>=max_frames {
                frame_us.sort_unstable();crate::diagnostic!("[native-session-end] completed={} min_us={} median_us={} max_us={} elapsed_us={}; frame samples include CPU/GPU wait, not displayed FPS",completed,frame_us[0],frame_us[frame_us.len()/2],frame_us.last().unwrap(),session_start.elapsed().as_micros());return Ok(());
            }
''',1)
    s+='\n#[cfg(feature="vita2d")] impl Game {\n'+body+'\n}\n';p.write_text(s,encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8');a=s.index('    #[cfg(target_os="vita")] if result.is_ok()');b=s.index('    let (steps,calls)=host::counts();diagnostic!("VM_EXECUTION',a)
    s=s[:a]+'''    #[cfg(target_os="vita")] if result.is_ok() {
        diagnostic!("ORIGINAL_INIT_COMPLETED; native loop follows unchanged normal Step/Draw/event order");
        game.renderer.present(game.window_inner_size.0,game.window_inner_size.1,game.scaling);
        game.native_after_init(2700)?;
    }
'''+s[b:];p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e023-{n:03}','e024-{n:03}').replace('E023_DIAGNOSTIC_STARTED','E024_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    # Only this platform boundary is removed; original argument/state behavior.
    p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8');a=s.index('    pub fn keyboard_check_direct(');b=close(s,s.index('{',a));body=s[a:b].replace('#[cfg(feature="headless")]','#[cfg(all(feature="headless",not(feature="vita2d")))]').replace('#[cfg(not(feature="headless"))]','#[cfg(any(not(feature="headless"),feature="vita2d"))]');s=s[:a]+body+s[b:];p.write_text(s,encoding='utf-8')
    # Reuse E023 hardware proof; no old offscreen fixture per new startup.
    p=src/'render/native.rs';s=p.read_text(encoding='utf-8');a=s.index('            let device=Self;let mut result=');b=s.index('            device.check()?;Ok(device)',a)
    s=s[:a]+'            let device=Self;crate::diagnostic!("[depth-proof-reuse] E023 unchanged primitive; offscreen fixture not repeated");\n'+s[b:];p.write_text(s,encoding='utf-8')
    # Bound already-proven traces; do not sync many lines every normal frame.
    for name in ['game/draw.rs','host.rs','render/vita2d.rs']:
        p=src/name;s=p.read_text(encoding='utf-8')
        for line in s.splitlines():
            if 'crate::diagnostic!(' in line and any(tag in line for tag in ['[original-draw-enter]','[original-object-draw]','[window-caption]','[graphics-view]','[graphics-depth]','[graphics-blend]','[graphics-clear]']):
                log=line[line.index('crate::diagnostic!('):];end=close(log,log.index('('),'(',')');call=log[:end]+';'
                bounded='{static COUNT:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);let n=COUNT.fetch_add(1,std::sync::atomic::Ordering::Relaxed);if n<3 || n%120==0 {'+call+'}}'
                s=s.replace(call,bounded,1)
        p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_draw_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend_input(a.output,a.source);print('E024 real input + original frame loop prepared; no fabricated device or audio')
if __name__=='__main__':main()
