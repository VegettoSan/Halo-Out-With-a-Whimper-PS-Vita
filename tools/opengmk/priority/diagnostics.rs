//! Durable bounded diagnostics. No allocation or logging inside successful allocs.
use std::{fmt,fs::{File,OpenOptions},io::{self,Write},path::{Path,PathBuf},sync::{Mutex,OnceLock,atomic::{AtomicBool,Ordering}}};
static LOG:Mutex<Option<File>>=Mutex::new(None);
static WORKSPACE:OnceLock<PathBuf>=OnceLock::new();
static FAILED:AtomicBool=AtomicBool::new(false);
#[macro_export]
macro_rules! diagnostic { ($($arg:tt)*) => { $crate::diagnostics::record(format_args!($($arg)*)) }; }
pub fn open(directory:&Path)->io::Result<()> {
    std::fs::create_dir_all(directory)?;
    for n in 0..1000 {
        let work=directory.join(format!("e019-{n:03}"));
        match std::fs::create_dir(&work) {
            Ok(())=>{},
            Err(e) if e.kind()==io::ErrorKind::AlreadyExists=>continue,
            Err(e)=>return Err(e),
        }
        let path=work.join("run.log");let file=OpenOptions::new().write(true).create_new(true).open(&path)?;
        WORKSPACE.set(work).map_err(|_|io::Error::other("diagnostic already initialized"))?;
        *LOG.lock().unwrap()=Some(file);record(format_args!("E019_DIAGNOSTIC_STARTED log={}",path.display()));return check();
    }
    Err(io::Error::other("diagnostic slots exhausted; preserve logs and select a new directory"))
}
pub fn workspace()->io::Result<PathBuf>{WORKSPACE.get().cloned().ok_or_else(||io::Error::other("diagnostic not initialized"))}
pub fn record(args:fmt::Arguments<'_>) {
    eprintln!("{args}");
    if let Ok(mut guard)=LOG.try_lock() {
        if let Some(file)=guard.as_mut() {
            // File is unbuffered; synchronize each phase/service boundary before continuing.
            if writeln!(file,"{args}").and_then(|_|file.sync_all()).is_err() {FAILED.store(true,Ordering::Relaxed);}
        }
    } else {FAILED.store(true,Ordering::Relaxed);}
}
pub fn check()->io::Result<()> {if FAILED.load(Ordering::Relaxed){Err(io::Error::other("persistent diagnostic write/sync failed"))}else{Ok(())}}
pub fn allocation_failed(size:usize,align:usize) {record(format_args!("ALLOCATION_FAILED requested={} align={}",size,align));}
pub fn native_memory(stage:&str) {
    #[cfg(target_os="vita")] {
        #[repr(C)] struct Free {size:i32,user:i32,cdram:i32,phycont:i32}
        extern "C" {fn sceKernelGetFreeMemorySize(info:*mut Free)->i32;}
        let mut f=Free {size:16,user:0,cdram:0,phycont:0};let rc=unsafe{sceKernelGetFreeMemorySize(&mut f)};
        record(format_args!("[native-memory] stage={} rc={} free_user={} free_cdram={} free_phycont={} valid={}",stage,rc,f.user,f.cdram,f.phycont,rc==0));
    }
    #[cfg(not(target_os="vita"))] {let _=stage;}
}
pub fn initialize_platform()->Result<(),String> {
    #[cfg(target_os="vita")] {
        extern "C" {fn sceSysmoduleIsLoaded(id:i32)->i32;fn sceSysmoduleLoadModule(id:i32)->i32;}
        record(format_args!("[platform] Rust main reached via VitaSDK CRT; configured_newlib_heap=134217728; builtin kernel/io/rtc/rng imports; no graphics/audio initialized"));
        native_memory("before_modules");
        // Retained std/network imports require NET. No sockets/NET heap are initialized or faked.
        let before=unsafe{sceSysmoduleIsLoaded(1)};
        let load=if before==0 {None}else{Some(unsafe{sceSysmoduleLoadModule(1)})};
        let after=unsafe{sceSysmoduleIsLoaded(1)};
        record(format_args!("[module] NET id=1 before={} load={:?} after={}; network APIs not exercised",before,load,after));
        if after!=0 {return Err(format!("NET module unavailable status={after}"));}
        native_memory("after_modules");
    }
    #[cfg(not(target_os="vita"))] {record(format_args!("[platform] Windows host; Vita initialization UNTESTED"));}
    check().map_err(|e|e.to_string())
}
