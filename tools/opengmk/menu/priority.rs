//! GM8 procedure completion is distinct from successful scheduler effects.
use crate::gml::{self,Value};
#[derive(Debug)] pub enum Effect { Applied, Failed(u32), Unavailable }
pub fn complete(process:Effect,thread:Effect)->gml::Result<Value> {
    crate::diagnostic!("[priority-effects] process={:?} thread={:?}; GM8 procedure returns no status; completion is NOT scheduler success",process,thread);
    Ok(Default::default())
}
pub fn set(priority:i32)->gml::Result<Value> {
    let (class,thread)=crate::process_priority::requested(priority);
    crate::diagnostic!("[priority-request] value={} class={:#x} thread={}",priority,class,thread);
    #[cfg(windows)] {
        if !std::env::args_os().any(|a|a=="--native-priority-contract") {
            use std::ffi::c_void;
            #[link(name="kernel32")] extern "system" {
                fn GetCurrentProcess()->*mut c_void; fn GetCurrentThread()->*mut c_void;
                fn SetPriorityClass(p:*mut c_void,c:u32)->i32; fn SetThreadPriority(t:*mut c_void,p:i32)->i32;
                fn GetLastError()->u32;
            }
            // Both calls are made in original order, including when the first fails.
            let p=unsafe{if SetPriorityClass(GetCurrentProcess(),class)!=0 {Effect::Applied}else{Effect::Failed(GetLastError())}};
            let t=unsafe{if SetThreadPriority(GetCurrentThread(),thread)!=0 {Effect::Applied}else{Effect::Failed(GetLastError())}};
            crate::diagnostic!("[priority-readback] {:?}",crate::process_priority::windows::current());
            return complete(p,t);
        }
    }
    crate::diagnostic!("[priority-unavailable] Windows process class and relative thread priority have no verified native equivalent; scheduler unchanged by this adapter");
    complete(Effect::Unavailable,Effect::Unavailable)
}
