//! Differential ABI/OS probe for the fully reviewed, copied 1 KiB helper.
//! This diagnostic alone loads that DLL; the portable runtime never loads it.
#[cfg(windows)]
fn main() -> Result<(),Box<dyn std::error::Error>> {
    use gm8emulator::{portable_cleanmem as adapter, game::external::{ExternalManager,dll::{ExternalSignature,CallConv,ValueType}}};
    use std::{ffi::c_void,os::windows::ffi::OsStrExt,mem};
    #[link(name="kernel32")]
    extern "system" {
        fn LoadLibraryW(path:*const u16)->*mut c_void;
        fn GetProcAddress(module:*mut c_void,name:*const u8)->*mut c_void;
        fn FreeLibrary(module:*mut c_void)->i32;
        fn GetCurrentProcess()->*mut c_void;
        fn GetProcessHandleCount(process:*mut c_void,count:*mut u32)->i32;
    }
    struct Module(*mut c_void);
    impl Drop for Module {fn drop(&mut self){unsafe{FreeLibrary(self.0);}}}
    let path=std::path::PathBuf::from(std::env::args_os().nth(1).ok_or("copied DLL path required")?).canonicalize()?;
    if std::fs::metadata(&path)?.len()!=1024 {return Err("wrong helper size; launcher must verify SHA-256".into());}
    let wide:Vec<u16>=path.as_os_str().encode_wide().chain(Some(0)).collect();
    let module=Module(unsafe{LoadLibraryW(wide.as_ptr())});if module.0.is_null(){return Err(std::io::Error::last_os_error().into());}
    let trim_ptr=unsafe{GetProcAddress(module.0,b"halo_shg_clean\0".as_ptr())};
    let query_ptr=unsafe{GetProcAddress(module.0,b"halo_shg_get_mem\0".as_ptr())};
    if trim_ptr.is_null() || query_ptr.is_null(){return Err("missing reviewed exports".into());}
    let original_trim:unsafe extern "C" fn()->f64=unsafe{mem::transmute(trim_ptr)};
    let original_query:unsafe extern "C" fn()->f64=unsafe{mem::transmute(query_ptr)};
    let mut handles_before=0;assert_ne!(unsafe{GetProcessHandleCount(GetCurrentProcess(),&mut handles_before)},0);
    let mut pages=vec![0x5au8;16*1024*1024];
    for byte in pages.iter_mut().step_by(4096){unsafe{std::ptr::write_volatile(byte,0x5a);}}
    let before=adapter::working_set();let original_bytes=unsafe{original_query()};let adapted_bytes=adapter::working_set();
    assert!(before.value>0.0 && original_bytes>0.0 && adapted_bytes.value>0.0);
    assert_eq!(original_bytes.fract(),0.0);assert_eq!(adapted_bytes.value.fract(),0.0);
    let original_result=unsafe{original_trim()};assert_ne!(original_result,0.0);
    let after_original=adapter::working_set();
    let mut checksum=0u64;
    for byte in pages.iter().step_by(4096){checksum+=unsafe{std::ptr::read_volatile(byte)} as u64;}
    let before_adapter=adapter::working_set();let adapted_result=adapter::trim();assert_ne!(adapted_result.value,0.0);
    let after_adapter=adapter::working_set();
    let signature=|symbol:&str|ExternalSignature{dll:"CleanMem.dll".into(),symbol:symbol.into(),call_conv:CallConv::Cdecl,type_args:vec![],type_return:ValueType::Real};
    let mut s=signature("halo_shg_clean");s.call_conv=CallConv::Stdcall;assert!(adapter::bind(&s).is_err());
    s=signature("halo_shg_clean");s.type_return=ValueType::Str;assert!(adapter::bind(&s).is_err());
    s=signature("halo_shg_clean");s.type_args.push(ValueType::Real);assert!(adapter::bind(&s).is_err());
    assert!(adapter::bind(&signature("unknown_export")).is_err());
    s=signature("halo_shg_clean");s.dll="Other.dll".into();assert!(adapter::bind(&s)?.is_none());
    let mut registry=ExternalManager::new(false);
    let first=registry.define(signature("halo_shg_clean"))?;let second=registry.define(signature("halo_shg_get_mem"))?;
    assert_ne!(first,second);assert!(registry.get_external(first).is_some());assert!(registry.get_external(second).is_some());
    registry.free("CleanMem.dll");assert!(registry.get_external(first).is_none() && registry.get_external(second).is_none());
    let mut handles_after=0;assert_ne!(unsafe{GetProcessHandleCount(GetCurrentProcess(),&mut handles_after)},0);assert_eq!(handles_before,handles_after);
    println!("CONTRACT_PASS original_query={} adapter_query={} pre_ws={} original_trim={} ws_after_original={} pre_adapter_ws={} adapter_trim={} ws_after_adapter={} handles_before={} handles_after={} fixture_checksum={}",original_bytes,adapted_bytes.value,before.value,original_result,after_original.value,before_adapter.value,adapted_result.value,after_adapter.value,handles_before,handles_after,checksum);
    println!("SIGNATURE_AND_BINDING_LIFECYCLE_PASS; DLL and adapter queried/trimmed only this child process");
    Ok(())
}
#[cfg(not(windows))]
fn main(){eprintln!("Windows differential probe only; no native result fabricated");std::process::exit(2);}
