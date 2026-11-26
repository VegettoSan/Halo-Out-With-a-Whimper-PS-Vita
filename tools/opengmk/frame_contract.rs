//! CPU service fixture; never claims a native frame or simulated game input.
use gm8emulator::{game::{Game,PlayType},gml::Value,diagnostics,probe_sha256};
fn main() {
    let input=std::path::PathBuf::from(std::env::args_os().nth(1).unwrap()).canonicalize().unwrap();
    let temp=std::path::PathBuf::from(std::env::args_os().nth(2).unwrap());std::fs::create_dir(&temp).unwrap();let temp=temp.canonicalize().unwrap();diagnostics::open(&temp).unwrap();
    let mut bytes=std::fs::read(&input).unwrap();assert_eq!(probe_sha256::digest(&bytes),"cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f");
    let assets=gm8exe::reader::from_exe(&mut bytes,None::<fn(&str)>,true,false).unwrap();drop(bytes);
    let game=Game::launch(assets,input,vec![],Some(temp.join("profile")),encoding_rs::WINDOWS_1252,true,0,false,PlayType::Normal).unwrap();
    assert_eq!(game.show_debug_message(&[Value::from("CPU debug contract")]).unwrap(),Value::from(0));
    assert_eq!(game.show_debug_message(&[Value::from(42)]).unwrap(),Value::from(0));
    assert!(game.show_debug_message(&[]).is_err());assert!(game.show_debug_message(&[Value::from(1),Value::from(2)]).is_err());
    diagnostics::check().unwrap();let log=std::fs::read_to_string(diagnostics::workspace().unwrap().join("run.log")).unwrap();
    assert!(log.contains("[gml-debug] CPU debug contract") && log.contains("[gml-debug] 42"));
    println!("FRAME_CPU_CONTRACT_PASS real string/number log, void/default result, argument errors; no Game::init/frame or native GPU claim");
}
