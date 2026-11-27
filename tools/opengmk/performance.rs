//! Exclusive main-thread timings. Nested stages subtract from their callers;
//! no sleeps/limiter, native rendering substitutes or game-state mutations.
use std::{cell::RefCell,time::Instant};
static STARTED:std::sync::atomic::AtomicBool=std::sync::atomic::AtomicBool::new(false);
static BASELINE:std::sync::atomic::AtomicBool=std::sync::atomic::AtomicBool::new(false);
pub fn baseline()->bool {BASELINE.load(std::sync::atomic::Ordering::Relaxed)}
pub fn trace_interval()->usize {if baseline(){120}else{1024}}
pub fn configure(flag:&std::path::Path)->std::io::Result<()> {
    let value=match flag.metadata(){Ok(m) if m.is_file()=>true,Ok(_)=>return Err(std::io::Error::other("baseline flag must be a regular diagnostic file")),Err(e) if e.kind()==std::io::ErrorKind::NotFound=>false,Err(e)=>return Err(e)};
    BASELINE.store(value,std::sync::atomic::Ordering::Relaxed);
    #[cfg(not(test))] crate::diagnostic!("[perf-policy] mode={} same_original_VM=true startup_cap=1000000 per_frame_watchdog=5000000 max_frames=2700",if value{"baseline"}else{"optimized"});Ok(())
}
pub const N:usize=12;
#[derive(Clone,Copy,PartialEq,Debug)] #[repr(usize)]
pub enum Stage {Other,GmlStep,GmlDraw,GmlOther,GmlCollision,Events,Collision,Render,Submit,Gpu,Display,Diagnostic}
const NAMES:[&str;N]=["engine_other","gml_step","gml_draw","gml_other","gml_collision","event_dispatch","collision","render_cpu","gxm_submit_wall","end_gpu_wait","swap_queue_wait","diagnostic"];
#[derive(Clone,Copy)] struct Entry {stage:Stage,start:u64,child:u64}
const EMPTY:Entry=Entry{stage:Stage::Other,start:0,child:0};
#[derive(Clone,Copy,Default)] pub struct Meta {pub objects:usize,pub all_objects:usize,pub render:[u64;10],pub heap:[usize;3],pub steps:usize}
#[derive(Clone,Copy)] struct Sample {frame:u32,room:i32,total:u64,times:[u64;N],calls:[u32;N],meta:Meta,counters:[u64;10],allocs:usize,steps:usize,collect:u64,pause:u64}
struct State {active:bool,origin:Instant,stack:[Entry;128],depth:usize,event:usize,times:[u64;N],calls:[u32;N],before:Meta,window:Vec<Sample>,invalid:bool,pause:u64}
impl State {
    fn new()->Self {Self{active:false,origin:Instant::now(),stack:[EMPTY;128],depth:0,event:usize::MAX,times:[0;N],calls:[0;N],before:Meta::default(),window:Vec::new(),invalid:false,pause:0}}
    fn now(&self)->u64 {self.origin.elapsed().as_micros() as u64}
    fn pop(&mut self) {let now=self.now();self.depth-=1;let e=self.stack[self.depth];let elapsed=now.saturating_sub(e.start);self.times[e.stage as usize]+=elapsed.saturating_sub(e.child);if self.depth>0{self.stack[self.depth-1].child+=elapsed;}}
}
thread_local! {static STATE:RefCell<State>=RefCell::new(State::new());}
pub struct Scope(bool);
pub fn scope(stage:Stage)->Scope {STATE.with(|s|{let mut s=s.borrow_mut();if !s.active{return Scope(false);}s.calls[stage as usize]+=1;
    if s.depth>0 && s.stack[s.depth-1].stage==stage{return Scope(false);}
    if s.depth==128{s.invalid=true;return Scope(false);}let d=s.depth;s.stack[d]=Entry{stage,start:s.now(),child:0};s.depth+=1;Scope(true)})}
impl Drop for Scope {fn drop(&mut self){if self.0{STATE.with(|s|s.borrow_mut().pop());}}}
pub struct Event {previous:usize,_scope:Scope}
pub fn event(id:usize)->Event {let previous=STATE.with(|s|{let mut s=s.borrow_mut();let old=s.event;s.event=id;old});Event{previous,_scope:scope(Stage::Events)}}
impl Drop for Event {fn drop(&mut self){STATE.with(|s|s.borrow_mut().event=self.previous);}}
pub fn gml()->Scope {let id=STATE.with(|s|s.borrow().event);scope(match id {3=>Stage::GmlStep,4=>Stage::GmlCollision,8=>Stage::GmlDraw,_=>Stage::GmlOther})}
pub fn begin_frame(before:Meta) {STARTED.store(true,std::sync::atomic::Ordering::Relaxed);STATE.with(|s|{let mut s=s.borrow_mut();if s.window.capacity()<60{s.window.reserve(60);}s.active=true;s.origin=Instant::now();s.depth=1;s.event=usize::MAX;s.times=[0;N];s.calls=[0;N];s.invalid=false;s.before=before;s.stack[0]=EMPTY;});}
pub fn native_wait(gpu:u64,display:u64) {STATE.with(|s|{let mut s=s.borrow_mut();if s.active{s.times[Stage::Gpu as usize]+=gpu;s.times[Stage::Display as usize]+=display;if s.depth>0 {let d=s.depth-1;s.stack[d].child+=gpu+display;}}});}
pub fn io_pause(us:u64) {STATE.with(|s|{let mut s=s.borrow_mut();if !s.active{s.pause=s.pause.saturating_add(us);}});}
fn quant(mut values:Vec<u64>)->[u64;3] {values.sort_unstable();let n=values.len();[values[n/2],values[((n*95+99)/100).saturating_sub(1)],values[n-1]]}
fn report(v:&[Sample]) {
    let reporting=Instant::now();
    if v.is_empty(){return;}let first=v.first().unwrap();let last=v.last().unwrap();let object_q=quant(v.iter().map(|s|s.meta.objects as u64).collect());
    #[cfg(not(test))] crate::diagnostic!("[perf-load] room={} first={} last={} n={} objects_p50={} objects_min={} objects_max={} all_objects_max={} total_us={:?} instructions={:?} collection_us={:?} outside_frame_sync_us={:?}",first.room,first.frame,last.frame,v.len(),object_q[0],v.iter().map(|s|s.meta.objects).min().unwrap(),v.iter().map(|s|s.meta.objects).max().unwrap(),v.iter().map(|s|s.meta.all_objects).max().unwrap(),quant(v.iter().map(|s|s.total).collect()),quant(v.iter().map(|s|s.steps as u64).collect()),quant(v.iter().map(|s|s.collect).collect()),quant(v.iter().map(|s|s.pause).collect()));
    for stage in 0..N {let q=quant(v.iter().map(|s|s.times[stage]).collect());let calls:u64=v.iter().map(|s|u64::from(s.calls[stage])).sum();
        #[cfg(not(test))] crate::diagnostic!("[perf-stage] room={} last={} n={} stage={} p50_us={} p95_us={} peak_us={} calls={}; exclusive except native end/wait includes driver work",first.room,last.frame,v.len(),NAMES[stage],q[0],q[1],q[2],calls);
    }
    let q:Vec<_>=(0..10).map(|i|quant(v.iter().map(|s|s.counters[i]).collect())).collect();
    #[cfg(not(test))] crate::diagnostic!("[perf-render] room={} last={} n={} quantiles=p50,p95,peak fields=visible,culled,batches,vertices,gxm_draws,shader_changes,texture_changes,state_requests,state_changes,tint_calls values={:?} allocations={:?} heap_live_max={} heap_peak={}",first.room,last.frame,v.len(),q,quant(v.iter().map(|s|s.allocs as u64).collect()),v.iter().map(|s|s.meta.heap[0]).max().unwrap(),v.iter().map(|s|s.meta.heap[1]).max().unwrap());
    #[cfg(not(test))] crate::diagnostic!("[perf-overhead] room={} last={} reporting_us={}; excluded from processing and limiter",first.room,last.frame,reporting.elapsed().as_micros());
}
pub fn end_frame<F:FnOnce()->Meta>(frame:u32,room:i32,metadata:F) {
    let start=Instant::now();let (total,times,calls,before,invalid,pause)=STATE.with(|s|{let mut s=s.borrow_mut();let invalid=s.depth!=1 || s.invalid;while s.depth>0{s.pop();}s.active=false;let pause=std::mem::take(&mut s.pause);(s.now(),s.times,s.calls,s.before,invalid,pause)});
    let meta=metadata();let sample=Sample{frame,room,total,times,calls,meta,counters:std::array::from_fn(|i|meta.render[i].saturating_sub(before.render[i])),allocs:meta.heap[2].saturating_sub(before.heap[2]),steps:meta.steps.saturating_sub(before.steps),collect:start.elapsed().as_micros() as u64,pause};
    if invalid {#[cfg(not(test))] crate::diagnostic!("PROFILE_INVALID frame={} depth_or_capacity_error=true",frame);}
    let mut old=None;let mut full=None;
    STATE.with(|s|{let mut s=s.borrow_mut();if s.window.first().is_some_and(|a|a.room!=room){old=Some(std::mem::replace(&mut s.window,Vec::with_capacity(60)));}s.window.push(sample);if s.window.len()==60 {full=Some(std::mem::replace(&mut s.window,Vec::with_capacity(60)));}});
    if let Some(v)=old {report(&v);}if let Some(v)=full {report(&v);}
}
pub fn flush() {let v=STATE.with(|s|{let mut s=s.borrow_mut();std::mem::replace(&mut s.window,Vec::with_capacity(60))});report(&v);}
pub fn finish() {if !STARTED.load(std::sync::atomic::Ordering::Relaxed){return;}STATE.with(|s|{let mut s=s.borrow_mut();s.active=false;s.depth=0;});flush();}
pub fn panic_snapshot() {if !STARTED.load(std::sync::atomic::Ordering::Relaxed){return;}let data=STATE.with(|s|{let s=s.borrow();(s.active,s.depth,s.times,s.calls)});#[cfg(not(test))] crate::diagnostic!("[perf-panic] active={} depth={} partial_exclusive_us={:?} calls={:?}",data.0,data.1,data.2,data.3);}
#[cfg(test)] mod tests {
    use super::*;
    #[test] fn quantiles_and_nested_exclusive_scopes() {
        assert_eq!(quant((1..=60).collect()),[31,57,60]);begin_frame(Meta::default());
        {let _e=event(3);let _g=gml();std::thread::sleep(std::time::Duration::from_millis(2));{let _r=scope(Stage::Render);std::thread::sleep(std::time::Duration::from_millis(2));}}
        STATE.with(|s|{let mut s=s.borrow_mut();assert_eq!(s.depth,1);s.pop();s.active=false;assert!(!s.invalid);assert!(s.times[Stage::GmlStep as usize]>=1000 && s.times[Stage::Render as usize]>=1000);assert!(s.times.iter().sum::<u64>()<=s.now()+20);});
    }
}
