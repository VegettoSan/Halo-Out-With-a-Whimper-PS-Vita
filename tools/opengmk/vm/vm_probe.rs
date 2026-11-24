//! Executes ONLY the original startup route; an unavailable service is a stop.
use gm8emulator::{game::{Game,PlayType},host::{self,DataFiles},heap_meter};
#[global_allocator] static ALLOCATOR:heap_meter::Meter=heap_meter::Meter;
fn run()->Result<(),Box<dyn std::error::Error>>{
 #[cfg(not(target_os="vita"))]
 let input=std::path::PathBuf::from(std::env::args_os().nth(1).ok_or("missing copied EXE")?).canonicalize()?;
 #[cfg(target_os="vita")]
 let input=std::path::PathBuf::from("ux0:data/howaw/HOWaW_FirefightDemov1.exe");
 #[cfg(not(target_os="vita"))] {
  let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(4).unwrap().canonicalize()?;
  if !input.starts_with(root.join("recovered")) { return Err("PC probe requires a private copy under recovered/".into()); }
 }
 let files=host::LocalDataFiles;
 let mut bytes=files.read(&input)?;
 if bytes.len()!=18_142_424 {return Err("unexpected baseline size; verify SHA-256 before launch".into());}
 heap_meter::snapshot("input");
 let assets=gm8exe::reader::from_exe(&mut bytes,None::<fn(&str)>,true,false)?;
 drop(bytes);heap_meter::snapshot("strict_reader");
 let temp=input.parent().unwrap().join("vm-temp");std::fs::create_dir(&temp)?;
 let mut game=Game::launch(assets,input,vec![],Some(temp),encoding_rs::WINDOWS_1252,true,0,false,PlayType::Normal)?;
 let scripts=game.assets.scripts.iter().flatten().count();
 let instructions:usize=game.assets.scripts.iter().flatten().map(|s|s.compiled.len()).sum();
 let objects=game.assets.objects.iter().flatten().count();
 let events:usize=game.assets.objects.iter().flatten().map(|o|o.events.iter().map(|e|e.len()).sum::<usize>()).sum();
 println!("PREPARED scripts={scripts} script_top_level_instructions={instructions} objects={objects} events={events}");
 heap_meter::snapshot("compiled_game");
 let result=game.init();
 let (steps,calls)=host::counts();println!("VM_EXECUTION instructions={steps} blocked_builtin_calls={calls}");
 heap_meter::snapshot("startup_stop");result
}
fn main(){
 std::panic::set_hook(Box::new(|_|{}));
 let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(run));
 let code=match result {
  Ok(Err(e))=>{eprintln!("STARTUP_STOP {e}");if e.to_string().contains("SERVICE_UNAVAILABLE/"){2}else{1}},
  Ok(Ok(()))=>{println!("STARTUP_COMPLETED");0},
  Err(payload)=>{if let Some(r)=payload.downcast_ref::<host::Request>() {eprintln!("STARTUP_STOP SERVICE_UNAVAILABLE/{:?}/{}",r.service,r.operation);2}else{eprintln!("UNEXPECTED_PANIC");1}}
 };
 heap_meter::snapshot("exit");std::process::exit(code)
}
