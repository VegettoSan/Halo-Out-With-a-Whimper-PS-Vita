//! Explicit platform boundary for the inspection frontend. No success stubs.
use crate::gml::{self, Value};
use std::sync::atomic::{AtomicUsize, Ordering};
#[derive(Clone, Copy, Debug)]
pub enum Service { Window, Graphics, Audio, Clipboard, Files, External, Dialog, Process, Builtin }
#[derive(Debug)]
pub struct Request { pub service: Service, pub operation: &'static str }
pub trait PlatformServices {
    fn request(&self, request: Request, args: &[Value]) -> gml::Result<Value>;
}
pub struct UnavailableServices;
impl PlatformServices for UnavailableServices {
    fn request(&self, r: Request, _args: &[Value]) -> gml::Result<Value> {
        Err(gml::Error::FunctionError(r.operation.into(), format!("SERVICE_UNAVAILABLE/{:?}", r.service)))
    }
}
pub fn unavailable(service: Service, operation: &'static str) -> ! {
    std::panic::panic_any(Request { service, operation })
}
static STEPS: AtomicUsize = AtomicUsize::new(0);
static CALLS: AtomicUsize = AtomicUsize::new(0);
pub fn instruction() {
    if STEPS.fetch_add(1, Ordering::Relaxed) >= 1_000_000 { unavailable(Service::Builtin,"instruction_budget"); }
}
pub fn trace(name: &'static str) {
    let n=CALLS.fetch_add(1, Ordering::Relaxed);
    if n<32 { eprintln!("[vm-call] {name}"); }
}
pub fn counts() -> (usize,usize) { (STEPS.load(Ordering::Relaxed),CALLS.load(Ordering::Relaxed)) }
// A deferred frontend token, never an OS window. All actual operations stop.
pub struct Window;
impl Window {
    pub fn deferred() -> Self { Self }
    pub fn set_title(&self, _title: &str) { unavailable(Service::Window,"set_title") }
    pub fn set_size(&self, _size: (u16,u16)) { unavailable(Service::Window,"set_size") }
    pub fn set_visible(&self, _visible: bool) { unavailable(Service::Window,"set_visible") }
}
/// Loader-only filesystem interface; GML file services stay explicitly blocked.
pub trait DataFiles {
    fn read(&self, path: &std::path::Path) -> std::io::Result<Vec<u8>>;
}
pub struct LocalDataFiles;
impl DataFiles for LocalDataFiles {
    fn read(&self, path: &std::path::Path) -> std::io::Result<Vec<u8>> { std::fs::read(path) }
}
