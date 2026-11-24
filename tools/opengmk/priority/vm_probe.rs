//! Actual existing loader/compiler/VM, with durable diagnostic boundaries.
use gm8emulator::{diagnostic,diagnostics,game::{Game,PlayType},host::{self,DataFiles},heap_meter,probe_sha256};
#[global_allocator] static ALLOCATOR:heap_meter::Meter=heap_meter::Meter;
#[cfg(target_os="vita")]
#[no_mangle] pub static _newlib_heap_size_user:u32=128*1024*1024; // Explicit existing SDK default; not a measured fit.
const EXE_SHA:&str="cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f";
fn run()->Result<(),Box<dyn std::error::Error>> {
    diagnostics::initialize_platform()?;
    #[cfg(not(target_os="vita"))]
    let input=std::path::PathBuf::from(std::env::args_os().nth(1).ok_or("missing copied EXE")?).canonicalize()?;
    #[cfg(target_os="vita")]
    let input=std::path::PathBuf::from("ux0:data/howaw/HOWaW_FirefightDemov1.exe");
    #[cfg(not(target_os="vita"))] {
        let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(4).unwrap().canonicalize()?;
        if !input.starts_with(root.join("recovered")){return Err("PC probe requires ignored recovered/ copy".into());}
    }
    diagnostic!("[data-open] path={}",input.display());
    let mut bytes=host::LocalDataFiles.read(&input)?;
    if bytes.len()!=18_142_424 {return Err(format!("EXE size mismatch: {}",bytes.len()).into());}
    let hash=probe_sha256::digest(&bytes);
    diagnostic!("[data-verify] bytes={} sha256={} expected={} pass={}",bytes.len(),hash,EXE_SHA,hash==EXE_SHA);
    if hash!=EXE_SHA {return Err("EXE SHA-256 mismatch; original data not interpreted".into());}
    heap_meter::snapshot("input");diagnostics::native_memory("input");
    let assets=gm8exe::reader::from_exe(&mut bytes,None::<fn(&str)>,true,false)?;
    drop(bytes);heap_meter::snapshot("strict_reader");diagnostics::native_memory("strict_reader");
    // Each diagnostic owns a new workspace; never overwrite a prior save/temp.
    let temp=diagnostics::workspace()?.join("vm-temp");std::fs::create_dir(&temp)?;
    diagnostic!("[compile-begin] original scripts/events; existing OpenGMK Game::launch");
    let mut game=Game::launch(assets,input,vec![],Some(temp),encoding_rs::WINDOWS_1252,true,0,false,PlayType::Normal)?;
    #[cfg(windows)] {game.services=Box::new(gm8emulator::runtime_services::RuntimeServices {interactive_dialog:std::env::args_os().any(|a|a=="--interactive-dialog")});}
    let scripts=game.assets.scripts.iter().flatten().count();
    let instructions:usize=game.assets.scripts.iter().flatten().map(|s|s.compiled.len()).sum();
    let objects=game.assets.objects.iter().flatten().count();
    let events:usize=game.assets.objects.iter().flatten().map(|o|o.events.iter().map(|e|e.len()).sum::<usize>()).sum();
    diagnostic!("PREPARED scripts={scripts} script_top_level_instructions={instructions} objects={objects} events={events}");
    heap_meter::snapshot("compiled_game");diagnostics::native_memory("compiled_game");diagnostics::check()?;
    diagnostic!("[vm-start] unchanged Game::init");
    let result=game.init();
    let (steps,calls)=host::counts();diagnostic!("VM_EXECUTION instructions={steps} blocked_builtin_calls={calls}");
    heap_meter::snapshot("startup_stop");diagnostics::native_memory("startup_stop");result
}
fn diagnostic_directory()->std::io::Result<std::path::PathBuf> {
    #[cfg(target_os="vita")] {Ok(std::path::PathBuf::from("ux0:data/howaw/diagnostics"))}
    #[cfg(not(target_os="vita"))] {Ok(std::path::PathBuf::from(std::env::args_os().nth(1).ok_or_else(||std::io::Error::other("missing input"))?).canonicalize()?.parent().unwrap().join("diagnostics"))}
}
fn main() {
    // Panic-abort on Vita still executes this hook; last service/count is durable.
    std::panic::set_hook(Box::new(|info|{
        let (steps,calls)=host::counts();
        if let Some(r)=info.payload().downcast_ref::<host::Request>() {diagnostic!("PANIC_STOP SERVICE_UNAVAILABLE/{:?}/{} instructions={} calls={}",r.service,r.operation,steps,calls);}
        else {diagnostic!("PANIC_STOP {} instructions={} calls={}",info,steps,calls);}
        heap_meter::snapshot("panic");diagnostics::native_memory("panic");
    }));
    let setup=diagnostic_directory().and_then(|d|diagnostics::open(&d));
    if let Err(e)=setup {eprintln!("DIAGNOSTIC_SETUP_FAIL {e}");std::process::exit(1);}
    let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(run));
    let mut code=match result {
        Ok(Err(e))=>{diagnostic!("STARTUP_STOP {e}");if e.to_string().contains("SERVICE_UNAVAILABLE/"){2}else{1}},
        Ok(Ok(()))=>{diagnostic!("STARTUP_COMPLETED");0},
        Err(_)=>{diagnostic!("STARTUP_STOP panic; see persisted hook");1},
    };
    heap_meter::snapshot("exit");diagnostics::native_memory("exit");
    diagnostic!("DIAGNOSTIC_END exit_code={code}");
    if let Err(e)=diagnostics::check(){eprintln!("DIAGNOSTIC_PERSIST_FAIL {e}");code=1;}
    std::process::exit(code)
}
