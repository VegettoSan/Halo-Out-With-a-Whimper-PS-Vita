#!/usr/bin/env python3
"""E032: classify real frame costs, remove cumulative diagnostic stop, preserve VM."""
import argparse,re,shutil,subprocess
from pathlib import Path

def probe(path,name,expression):
    s=path.read_text(encoding='utf-8');m=re.search(r'(?m)^\s*(?:pub(?:\([^)]*\))? )?fn '+name+r'\(',s);assert m,name
    i=s.index('{',m.start())+1;s=s[:i]+'\n        #[cfg(feature="howaw_perf")] let _howaw_perf = crate::performance::'+expression+';'+s[i:];path.write_text(s,encoding='utf-8')

def extend(root):
    src=root/'gm8emulator/src';own=Path(__file__).parent
    shutil.copyfile(own/'performance.rs',src/'performance.rs')
    p=root/'gm8emulator/Cargo.toml';s=p.read_text(encoding='utf-8');s,n=re.subn(r'(?m)^vita2d = \[(.*)\]$',r'howaw_perf = []\nvita2d = [\1,"howaw_perf"]',s);assert n==1;p.write_text(s,encoding='utf-8')
    p=src/'lib.rs';p.write_text(p.read_text(encoding='utf-8')+'\n#[cfg(feature="howaw_perf")] pub mod performance;\n',encoding='utf-8')
    p=src/'host.rs';s=p.read_text(encoding='utf-8');old='    if STEPS.fetch_add(1, Ordering::Relaxed) >= 1_000_000 { unavailable(Service::Builtin,"instruction_budget"); }';assert old in s
    s=s.replace(old,'''    let n=STEPS.fetch_add(1, Ordering::Relaxed);let limit=WATCHDOG_LIMIT.load(Ordering::Relaxed);
    if n>=limit {panic!("DIAGNOSTIC_WATCHDOG instruction_limit cumulative={} limit={}; no VM result fabricated",n+1,limit);}''')
    s+='\nstatic WATCHDOG_LIMIT:AtomicUsize=AtomicUsize::new(1_000_000);\npub fn reset_frame_watchdog(budget:usize) {assert!(budget>0);WATCHDOG_LIMIT.store(STEPS.load(Ordering::Relaxed).saturating_add(budget),Ordering::Relaxed);}\n';p.write_text(s,encoding='utf-8')
    probe(src/'gml/runtime.rs','execute','gml()')
    probe(src/'game/events.rs','run_instance_event','event(event_id)')
    probe(src/'game/events.rs','run_collisions','scope(crate::performance::Stage::Collision)')
    probe(src/'game/draw.rs','draw','scope(crate::performance::Stage::Render)')
    for name in ['check_collision','check_collision_point','check_collision_rectangle','check_collision_ellipse','check_collision_line','check_collision_solid','check_collision_any']:
        probe(src/'game.rs',name,'scope(crate::performance::Stage::Collision)')
    for name in ['draw_sprite_general','draw_rectangle_gradient','draw_line','draw_ellipse','set_blend_mode','clear_view','set_view']:
        probe(src/'render/vita2d.rs',name,'scope(crate::performance::Stage::Render)')
    for name in ['draw','tinted','colors','lines']:
        probe(src/'render/native.rs',name,'scope(crate::performance::Stage::Submit)')
    p=src/'render/native.rs';s=p.read_text(encoding='utf-8');m='            let rc=ffi::howaw_finish_frame();';assert m in s
    s=s.replace(m,m+'\n            #[cfg(feature="howaw_perf")] {let mut t=[0u32;4];ffi::howaw_present_times(t.as_mut_ptr());crate::performance::native_wait(t[0] as u64,t[1] as u64);}',1);p.write_text(s,encoding='utf-8')
    p=src/'heap_meter.rs';s=p.read_text(encoding='utf-8');s+='\npub fn counters()->[usize;3] {[LIVE.load(Ordering::Relaxed),PEAK.load(Ordering::Relaxed),ALLOCS.load(Ordering::Relaxed)]}\n';p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8');a=s.index('    pub fn native_after_init(');head=s[:a];body=s[a:]
    body=body.replace('let mut frame_us=Vec::<u64>::new();','let mut frame_us=Vec::<u64>::with_capacity(max_frames as usize);\n        crate::diagnostic!("[diagnostic-policy] startup_limit=1000000 frame_watchdog=5000000 cumulative_cap_after_init=false max_frames={}",max_frames);\n        crate::host::reset_frame_watchdog(5_000_000);',1)
    m='            let cpu_start=Instant::now();';assert m in body
    body=body.replace(m,m+'\n            crate::performance::begin_frame(crate::performance::Meta{render:self.renderer.performance_counters(),heap:crate::heap_meter::counters(),steps:crate::host::counts().0,..Default::default()});\n            crate::host::reset_frame_watchdog(5_000_000);',1)
    m='            completed+=1;frame_us.push(cpu_start.elapsed().as_micros() as u64);';assert m in body
    body=body.replace(m,m+'\n            crate::performance::end_frame(completed,self.room.id,||crate::performance::Meta{objects:self.room.instance_list.count_all_active(),all_objects:self.room.instance_list.count_all(),render:self.renderer.performance_counters(),heap:crate::heap_meter::counters(),steps:crate::host::counts().0});',1)
    body=body.replace('            if crate::render::vita2d::take_ram_upload() {crate::render::vita2d::inspect_original_frame()?;}','            // E030 actual sampling/frame proof retained; no repeated expensive diagnostic readback.')
    body=body.replace('            if let Err(e)=self.frame() {','            if let Err(e)=self.frame() {\n                crate::performance::panic_snapshot();crate::performance::finish();',1)
    p.write_text(head+body,encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8');s=s.replace('        game.native_after_init(2700)?;','        let frame_result=game.native_after_init(2700);let drain_result=game.renderer.graphics_drain();frame_result?;drain_result?;',1)
    m='    let mut game=Game::launch(';assert m in s;s=s.replace(m,'    #[cfg(target_os="vita")] gm8emulator::performance::configure(std::path::Path::new("ux0:data/howaw/e032-baseline.flag"))?;\n'+m,1)
    s=s.replace('        heap_meter::snapshot("panic");','        gm8emulator::performance::panic_snapshot();heap_meter::snapshot("panic");',1)
    s=s.replace('    heap_meter::snapshot("exit");','    gm8emulator::performance::finish();heap_meter::snapshot("exit");',1);p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e031-{n:03}','e032-{n:03}').replace('E031_DIAGNOSTIC_STARTED','E032_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    probe(p,'record','scope(crate::performance::Stage::Diagnostic)')
    probe(p,'checkpoint','scope(crate::performance::Stage::Diagnostic)')
    s=p.read_text(encoding='utf-8');s=s.replace('pub fn checkpoint()->io::Result<()> {','pub fn checkpoint()->io::Result<()> {\n    let _perf_io_start=std::time::Instant::now();',1)
    m='if result.is_err(){FAILED.store(true,Ordering::Relaxed);}result';assert m in s;s=s.replace(m,'if result.is_err(){FAILED.store(true,Ordering::Relaxed);}crate::performance::io_pause(_perf_io_start.elapsed().as_micros() as u64);result',1);p.write_text(s,encoding='utf-8')
    # Authored routine traces only. Original GML show_debug_message and failures
    # remain complete; the engine's events/audio commands are never skipped.
    for name in ['game/draw.rs','host.rs','render/vita2d.rs']:
        p=src/name;s=p.read_text(encoding='utf-8').replace('n%120==0','n%crate::performance::trace_interval()==0');p.write_text(s,encoding='utf-8')
    p=src/'game/deferred_audio.rs';s=p.read_text(encoding='utf-8');s=re.sub(r'(        crate::diagnostic!\("\[audio-command\][^\n]+;)',r'        {static N:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);let n=N.fetch_add(1,std::sync::atomic::Ordering::Relaxed);if crate::performance::baseline() || n<4 || n%512==0 {\1}}',s);p.write_text(s,encoding='utf-8')
    shutil.copyfile(own/'performance_contract.rs',src/'bin/performance_contract.rs')
    p=root/'gm8emulator/Cargo.toml';s=p.read_text(encoding='utf-8')+'\n[[bin]]\nname="performance-contract"\npath="src/bin/performance_contract.rs"\nrequired-features=["vita2d"]\n';p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_shapes_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend(a.output);print('E032 original frame retained; explicit per-frame watchdog, exclusive phase/profile windows and measured renderer optimizations')
if __name__=='__main__':main()
