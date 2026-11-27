//! Bounded per-method counters and 1/128 inclusive wall-time samples.
//! Nested method samples overlap; do not add their times or infer native CPU cycles.
use std::{cell::RefCell,time::Instant,sync::atomic::{AtomicBool,Ordering}};
static ENABLED:AtomicBool=AtomicBool::new(false);
static REFERENCE:AtomicBool=AtomicBool::new(false);
pub fn reference()->bool{REFERENCE.load(Ordering::Relaxed)}
pub fn configure(path:&std::path::Path)->std::io::Result<()>{let value=match path.metadata(){Ok(m) if m.is_file()=>true,Ok(_)=>return Err(std::io::Error::other("collision reference flag must be a regular file")),Err(e) if e.kind()==std::io::ErrorKind::NotFound=>false,Err(e)=>return Err(e)};REFERENCE.store(value,Ordering::Relaxed);crate::diagnostic!("[collision-policy] reference={} renderer_unchanged=true simulation_hz_unchanged=true",value);Ok(())}
pub fn enabled(value:bool){ENABLED.store(value,Ordering::Relaxed);}
const K:usize=7;
const NAMES:[&str;K]=["pair","point","rectangle","ellipse","line","solid","any"];
#[derive(Clone,Copy,Default)] struct Row{calls:u64,samples:u64,ns:u64,peak_ns:u64,reject:u64,stale:u64}
thread_local!{static DATA:RefCell<[Row;K]>=const{RefCell::new([Row{calls:0,samples:0,ns:0,peak_ns:0,reject:0,stale:0};K])};}
pub struct Scope{kind:usize,start:Option<Instant>}
#[inline(always)] pub fn enter(kind:usize)->Scope {if !ENABLED.load(Ordering::Relaxed){return Scope{kind,start:None};}enter_active(kind)}
#[cold] #[inline(never)] fn enter_active(kind:usize)->Scope {let sample=DATA.with(|d|{let mut d=d.borrow_mut();d[kind].calls+=1;let h=(d[kind].calls as u32).wrapping_mul(0x9e3779b9).rotate_right(13);d[kind].calls==1 || h&127==0});Scope{kind,start:sample.then(Instant::now)}}
impl Drop for Scope{#[inline(always)] fn drop(&mut self){if let Some(t)=self.start{let n=t.elapsed().as_nanos() as u64;DATA.with(|d|{let mut d=d.borrow_mut();let r=&mut d[self.kind];r.samples+=1;r.ns+=n;r.peak_ns=r.peak_ns.max(n);});}}}
#[inline(always)] pub fn reject(kind:usize){if ENABLED.load(Ordering::Relaxed){DATA.with(|d|d.borrow_mut()[kind].reject+=1);}}
#[inline(always)] pub fn stale(kind:usize){if ENABLED.load(Ordering::Relaxed){DATA.with(|d|d.borrow_mut()[kind].stale+=1);}}
pub fn reset(){DATA.with(|d|*d.borrow_mut()=[Row::default();K]);}
pub fn report(label:&str){let data=DATA.with(|d|*d.borrow());for (i,r) in data.iter().enumerate(){crate::diagnostic!("[collision-method] stage={} kind={} calls={} samples={} sampled_inclusive_ns={} sampled_peak_ns={} early_reject={} stale_queries={}; first+hashed~1of128, nested times overlap",label,NAMES[i],r.calls,r.samples,r.ns,r.peak_ns,r.reject,r.stale);}}
pub fn calibrate(){enabled(true);
    for round in 0..3 {let n=100_000u64;let mut sum=0;let t=Instant::now();for i in 0..n{sum+=std::hint::black_box(i);}let base=t.elapsed().as_nanos();
        let t=Instant::now();for i in 0..n{let _s=enter(0);sum+=std::hint::black_box(i);}let sampled=t.elapsed().as_nanos();
        crate::performance::begin_frame(Default::default());let t=Instant::now();for i in 0..n{let _s=crate::performance::scope(crate::performance::Stage::Collision);sum+=std::hint::black_box(i);}let full=t.elapsed().as_nanos();
        let outer=crate::performance::scope(crate::performance::Stage::Collision);let t=Instant::now();for i in 0..n{let _s=crate::performance::scope(crate::performance::Stage::Collision);sum+=std::hint::black_box(i);}let nested=t.elapsed().as_nanos();
        let t=Instant::now();for i in 0..n{let _s=crate::performance::scope(crate::performance::Stage::Collision);let _m=enter(0);if i&1==0{reject(0)}else{stale(0)}sum+=std::hint::black_box(i);}let combined=t.elapsed().as_nanos();drop(outer);crate::performance::finish();
        std::hint::black_box(sum);crate::diagnostic!("[collision-calibration] round={} iterations={} empty_ns={} sampled_ns={} legacy_timed_ns={} legacy_nested_ns={} combined_nested_ns={}; wall clock, no correction subtracted",round,n,base,sampled,full,nested,combined);
    }reset();
}
