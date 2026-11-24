//! Measured GM8 process + current-thread priority contract; no Vita mapping.
use crate::gml::{self, Value};

/// Table verified against the owner's original runner, not inferred from labels.
pub fn requested(priority:i32)->(u32,i32) {
    match priority {
        -3=>(0x40,-15), -2=>(0x20,-2), -1=>(0x20,-1),
        1=>(0x20,1), 2=>(0x80,2), 3=>(0x100,15), _=>(0x20,0),
    }
}
#[cfg(windows)]
pub mod windows {
    use std::ffi::c_void;
    #[link(name="kernel32")]
    extern "system" {
        fn GetCurrentProcess()->*mut c_void;
        fn GetCurrentThread()->*mut c_void;
        fn SetPriorityClass(process:*mut c_void,class:u32)->i32;
        fn SetThreadPriority(thread:*mut c_void,priority:i32)->i32;
        fn GetPriorityClass(process:*mut c_void)->u32;
        fn GetThreadPriority(thread:*mut c_void)->i32;
        fn GetLastError()->u32;
    }
    pub fn current()->Result<(u32,i32),String> { unsafe {
        let class=GetPriorityClass(GetCurrentProcess());
        if class==0 {return Err(format!("GetPriorityClass error={}",GetLastError()));}
        let thread=GetThreadPriority(GetCurrentThread());
        if thread==i32::MAX {return Err(format!("GetThreadPriority error={}",GetLastError()));}
        Ok((class,thread))
    }}
    pub fn set(class:u32,thread:i32)->Result<(),String> { unsafe {
        // Original order. A partial failure is reported; no successful result is invented.
        if SetPriorityClass(GetCurrentProcess(),class)==0 {return Err(format!("SetPriorityClass error={}",GetLastError()));}
        if SetThreadPriority(GetCurrentThread(),thread)==0 {return Err(format!("SetThreadPriority error={}; process class already changed",GetLastError()));}
        Ok(())
    }}
}
pub fn set(priority:i32)->gml::Result<Value> {
    let wanted=requested(priority);
    crate::diagnostic!("[priority-request] value={} class={:#x} thread={}",priority,wanted.0,wanted.1);
    #[cfg(windows)] {
        let operation=||->Result<(),String> {
            let before=windows::current()?;
            windows::set(wanted.0,wanted.1)?;
            let actual=windows::current()?;
            crate::diagnostic!("[priority-result] before={:?} actual={:?} expected={:?}",before,actual,wanted);
            if actual!=wanted {return Err("priority readback mismatch".into());}
            Ok(())
        };
        operation().map_err(|e|gml::Error::FunctionError("set_program_priority".into(),e))?;
        // GM8 has no meaningful GML return; preserve existing VM default AFTER real OS work.
        Ok(Default::default())
    }
    #[cfg(not(windows))] {
        Err(gml::Error::FunctionError("set_program_priority".into(),
            "SERVICE_UNAVAILABLE/Process: no verified Windows process/thread priority equivalent".into()))
    }
}
