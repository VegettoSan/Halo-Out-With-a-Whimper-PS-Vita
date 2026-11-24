//! Owner-selected E019 diagnostic policy, not a claim of a native modal UI.
use crate::runtime_services::MessageDialog;
use std::sync::atomic::{AtomicBool,Ordering};
static FIRST:AtomicBool=AtomicBool::new(true);
pub fn answer(request:&MessageDialog)->Option<Result<i32,String>> {
    let enabled=cfg!(target_os="vita") || std::env::args_os().any(|a|a=="--owner-dialog-high");
    if !enabled {return None;}
    if !FIRST.swap(false,Ordering::Relaxed) {return Some(Err("SERVICE_UNAVAILABLE/Dialog: owner policy only covers the first startup dialog".into()));}
    if request.buttons[2].is_empty(){return Some(Err("owner High policy requires an existing third button".into()));}
    let (instructions,_)=crate::host::counts();
    crate::diagnostic!("[dialog-policy-response] OWNER_POLICY_HIGH result=3 instructions={} source=owner-selected startup default; no native UI or manual response claimed",instructions);
    Some(Ok(3))
}
