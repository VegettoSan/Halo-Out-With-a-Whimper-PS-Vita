//! Contract adapter for the audited zero-argument CleanMem helper.
//! No legacy DLL is loaded here. Unknown signatures are never guessed.
use crate::{game::external::dll::{CallConv, ExternalSignature, ValueType}, gml::{self, Value}};

#[derive(Clone, Copy, Debug)]
pub enum Binding { TrimWorkingSet, QueryWorkingSet }

pub fn bind(s: &ExternalSignature) -> Result<Option<Binding>, String> {
    let name = s.dll.rsplit(['/', '\\']).next().unwrap_or(&s.dll);
    if !name.eq_ignore_ascii_case("CleanMem.dll") { return Ok(None); }
    if !matches!(s.call_conv, CallConv::Cdecl) || !matches!(s.type_return, ValueType::Real) || !s.type_args.is_empty() {
        return Err("CleanMem requires cdecl, real return, zero arguments".into());
    }
    let binding = match s.symbol.as_str() {
        "halo_shg_clean" => Binding::TrimWorkingSet,
        "halo_shg_get_mem" => Binding::QueryWorkingSet,
        _ => return Err("unknown CleanMem export".into()),
    };
    eprintln!("[external-bind] CleanMem {:?}: cdecl real argc=0", binding);
    Ok(Some(binding))
}

#[derive(Debug)]
pub struct Outcome { pub value: f64, pub status: &'static str, pub os_error: Option<u32> }

pub fn invoke(binding: Binding, args: &[Value]) -> gml::Result<Value> {
    if !args.is_empty() { return Err(gml::Error::WrongArgumentCount(0, args.len())); }
    crate::host::trace("cleanmem_service");
    let result = match binding { Binding::TrimWorkingSet => trim(), Binding::QueryWorkingSet => working_set() };
    eprintln!("[external-result] {:?} value={} status={} os_error={:?}", binding, result.value, result.status, result.os_error);
    Ok(result.value.into())
}

#[cfg(windows)]
mod windows {
    use super::Outcome;
    use std::{ffi::c_void, mem, ptr};
    type Handle = *mut c_void;
    #[repr(C)]
    struct Counters { cb: u32, faults: u32, peak: usize, working: usize, rest: [usize; 6] }
    #[link(name="kernel32")]
    extern "system" {
        fn GetCurrentProcessId() -> u32;
        fn OpenProcess(access: u32, inherit: i32, pid: u32) -> Handle;
        fn CloseHandle(handle: Handle) -> i32;
        fn GetLastError() -> u32;
    }
    #[link(name="psapi")]
    extern "system" {
        fn EmptyWorkingSet(handle: Handle) -> i32;
        fn GetProcessMemoryInfo(handle: Handle, counters: *mut Counters, size: u32) -> i32;
    }
    struct Process(Handle);
    impl Drop for Process { fn drop(&mut self) { unsafe { CloseHandle(self.0); } } }
    fn open() -> Result<Process, Outcome> {
        // Same access mask/current PID as the reviewed helper, no other process.
        let h=unsafe { OpenProcess(0x001f_0fff, 0, GetCurrentProcessId()) };
        if h==ptr::null_mut() { Err(Outcome { value:0.0, status:"OpenProcess failed", os_error:Some(unsafe { GetLastError() }) }) }
        else { Ok(Process(h)) }
    }
    pub fn trim() -> Outcome {
        let process=match open() { Ok(p)=>p,Err(e)=>return e };
        let value=unsafe { EmptyWorkingSet(process.0) };
        Outcome { value:f64::from(value), status:if value!=0 { "EmptyWorkingSet performed" } else { "EmptyWorkingSet failed" }, os_error:if value==0 { Some(unsafe { GetLastError() }) } else { None } }
    }
    pub fn working_set() -> Outcome {
        let process=match open() { Ok(p)=>p,Err(e)=>return e };
        let mut c:Counters=unsafe { mem::zeroed() };c.cb=mem::size_of::<Counters>() as u32;
        let ok=unsafe { GetProcessMemoryInfo(process.0,&mut c,mem::size_of::<Counters>() as u32) };
        if ok==0 { Outcome { value:0.0,status:"GetProcessMemoryInfo failed",os_error:Some(unsafe { GetLastError() }) } }
        // The original x86 FILD reads a SIGNED 32-bit WorkingSetSize, even >2GiB.
        else { Outcome { value:f64::from(c.working as u32 as i32),status:"current working-set bytes (original signed32 contract)",os_error:None } }
    }
}

#[cfg(target_os="vita")]
fn vita_diagnostic() {
    #[repr(C)] struct FreeMemory { size:i32, user:i32, cdram:i32, phycont:i32 }
    extern "C" { fn sceKernelGetFreeMemorySize(info:*mut FreeMemory) -> i32; }
    let mut info=FreeMemory {size:16,user:0,cdram:0,phycont:0};
    let rc=unsafe {sceKernelGetFreeMemorySize(&mut info)};
    // Diagnostic only. These values are NOT process WorkingSetSize.
    eprintln!("[vita-memory] rc={} free_user={} free_cdram={} free_phycont={}",rc,info.user,info.cdram,info.phycont);
}

pub fn trim() -> Outcome {
    #[cfg(windows)] { return windows::trim(); }
    #[cfg(target_os="vita")] { vita_diagnostic(); }
    #[cfg(not(windows))] {
        // No paged Windows working set exists in the inspected public Vita SDK.
        // Its _sbrk_r only adjusts a break within an already reserved heap block;
        // malloc_trim success would not prove physical working-set reclamation.
        Outcome {value:0.0,status:"unsupported Windows working-set trim; original failure return, no cleanup success claimed",os_error:None}
    }
}
pub fn working_set() -> Outcome {
    #[cfg(windows)] { return windows::working_set(); }
    #[cfg(target_os="vita")] { vita_diagnostic(); }
    #[cfg(not(windows))] { Outcome {value:0.0,status:"unsupported process WorkingSetSize metric; original query-failure return",os_error:None} }
}
