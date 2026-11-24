//! Host services for E018. Dialog responses come only from an actual frontend.
use crate::{gml::{self,Value},host::{PlatformServices,Request,UnavailableServices},portable_cleanmem::{self,Binding}};

pub struct MessageDialog { pub text:String, pub buttons:[String;3] }
pub struct RuntimeServices { pub interactive_dialog:bool }
impl PlatformServices for RuntimeServices {
    fn request(&self, r:Request, args:&[Value]) -> gml::Result<Value> { UnavailableServices.request(r,args) }
    fn call_external(&self, binding:Binding, args:&[Value]) -> gml::Result<Value> { portable_cleanmem::invoke(binding,args) }
    fn show_message_ext(&self, request:&MessageDialog) -> Result<i32,String> {
        crate::host::trace("show_message_ext");
        let (instructions,_)=crate::host::counts();
        eprintln!("[dialog-request] instructions={} text={:?} buttons={:?}",instructions,request.text,request.buttons);
        if !self.interactive_dialog { return Err("SERVICE_UNAVAILABLE/Dialog: real frontend response required".into()); }
        #[cfg(windows)] {
            eprintln!("[dialog-pending] waiting for HUMAN input; no VM stepping");
            let started=std::time::Instant::now();
            let result=crate::game::platform::message_dialog::show(0,&request.text,[&request.buttons[0],&request.buttons[1],&request.buttons[2]])
                .map_err(|e|e.to_string())?;
            let (after,_)=crate::host::counts();
            eprintln!("[dialog-response] result={} instructions_before={} instructions_after={} pending_ms={}",result,instructions,after,started.elapsed().as_millis());
            if !(0..=3).contains(&result) { return Err("invalid modal result".into()); }
            Ok(result)
        }
        #[cfg(not(windows))] { Err("SERVICE_UNAVAILABLE/Dialog: native Vita frontend not implemented".into()) }
    }
}
