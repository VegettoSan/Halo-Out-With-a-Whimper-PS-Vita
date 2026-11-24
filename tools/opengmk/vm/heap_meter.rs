use std::{alloc::{GlobalAlloc,Layout,System},sync::atomic::{AtomicUsize,Ordering}};
pub struct Meter;
static LIVE:AtomicUsize=AtomicUsize::new(0);
static PEAK:AtomicUsize=AtomicUsize::new(0);
static ALLOCS:AtomicUsize=AtomicUsize::new(0);
static LARGE:AtomicUsize=AtomicUsize::new(0);
fn add(n:usize){let live=LIVE.fetch_add(n,Ordering::Relaxed)+n;PEAK.fetch_max(live,Ordering::Relaxed);ALLOCS.fetch_add(1,Ordering::Relaxed);if n>=4*1024*1024{LARGE.fetch_add(1,Ordering::Relaxed);}}
unsafe impl GlobalAlloc for Meter {
 unsafe fn alloc(&self,l:Layout)->*mut u8{let p=System.alloc(l);if !p.is_null(){add(l.size());}p}
 unsafe fn alloc_zeroed(&self,l:Layout)->*mut u8{let p=System.alloc_zeroed(l);if !p.is_null(){add(l.size());}p}
 unsafe fn dealloc(&self,p:*mut u8,l:Layout){System.dealloc(p,l);LIVE.fetch_sub(l.size(),Ordering::Relaxed);}
 unsafe fn realloc(&self,p:*mut u8,l:Layout,n:usize)->*mut u8{let q=System.realloc(p,l,n);if !q.is_null(){LIVE.fetch_sub(l.size(),Ordering::Relaxed);add(n);}q}
}
pub fn snapshot(stage:&str){eprintln!("[heap] stage={stage} live={} peak={} allocations={} large_ge_4m={}",LIVE.load(Ordering::Relaxed),PEAK.load(Ordering::Relaxed),ALLOCS.load(Ordering::Relaxed),LARGE.load(Ordering::Relaxed));}
