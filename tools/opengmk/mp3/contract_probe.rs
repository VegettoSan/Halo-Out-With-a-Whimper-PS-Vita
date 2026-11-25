//! Service contracts on a separate compiled Game; never runs the original VM.
use gm8emulator::{diagnostics,diagnostic,heap_meter,host::DataFiles,game::{Game,PlayType},asset::sound::FileType,gml::Value,game::audio::AudioManager};
#[global_allocator] static ALLOCATOR:heap_meter::Meter=heap_meter::Meter;
fn main()->Result<(),Box<dyn std::error::Error>> {
    let input=std::path::PathBuf::from(std::env::args_os().nth(1).ok_or("copied EXE required")?).canonicalize()?;
    let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(4).unwrap().canonicalize()?;
    if !input.starts_with(root.join("recovered")){return Err("contract requires an ignored recovered/ copy".into());}
    diagnostics::open(&input.parent().unwrap().join("mp3-contract-logs"))?;
    let mut bytes=gm8emulator::host::LocalDataFiles.read(&input)?;
    assert_eq!(gm8emulator::probe_sha256::digest(&bytes),"cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f");
    let assets=gm8exe::reader::from_exe(&mut bytes,None::<fn(&str)>,true,false)?;drop(bytes);
    let temp=diagnostics::workspace()?.join("temp");std::fs::create_dir(&temp)?;
    let mut game=Game::launch(assets,input.clone(),vec![],Some(temp),encoding_rs::WINDOWS_1252,true,0,false,PlayType::Normal)?;
    let path=input.parent().unwrap().join("Music/menu.mp3");
    let mp3=std::fs::read(&path)?;assert_eq!(gm8emulator::probe_sha256::digest(&mp3),"e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0");drop(mp3);
    let bad=diagnostics::workspace()?.join("invalid.mp3");std::fs::write(&bad,b"not MPEG audio")?;
    let missing=diagnostics::workspace()?.join("absent.mp3");
    let replace=|game:&mut Game,p:&std::path::Path| game.sound_replace(&[140.into(),p.to_str().unwrap().into(),3.into(),true.into()]);
    assert!(game.sound_replace(&[]).is_err());
    assert!(game.sound_replace(&[99999.into(),path.to_str().unwrap().into(),3.into(),true.into()]).is_err());
    assert_eq!(replace(&mut game,&missing)?,Value::from(0));
    assert_eq!(replace(&mut game,&bad)?,Value::from(0));
    assert!(matches!(game.assets.sounds[140].as_ref().unwrap().handle,FileType::Deferred{..}));
    assert_eq!(replace(&mut game,&path)?,Value::from(1));
    let FileType::Mp3(handle)=&game.assets.sounds[140].as_ref().unwrap().handle else{panic!("no real MP3 handle")};
    let details=AudioManager::registered_details(handle);assert_eq!(details,(140,1_293_667,2,44100,3_565_440));
    let clone=handle.clone();assert_eq!(AudioManager::shared_owners(handle),2);drop(clone);assert_eq!(AudioManager::shared_owners(handle),1);
    assert_eq!(replace(&mut game,&bad)?,Value::from(0));
    let FileType::Mp3(handle)=&game.assets.sounds[140].as_ref().unwrap().handle else{panic!("old handle lost on failed replacement")};
    assert_eq!(AudioManager::registered_details(handle),details);
    // Freeing a successful old replacement and decoding into None both need real handles.
    assert_eq!(replace(&mut game,&path)?,Value::from(1));
    game.assets.sounds[140].as_mut().unwrap().handle=FileType::None;
    assert_eq!(replace(&mut game,&path)?,Value::from(1));
    assert_eq!(gm8emulator::host::counts().0,0);
    diagnostic!("MP3_CONTRACT_PASS bad arity/id, missing/invalid data, Deferred/None/Mp3 replacements, failure retention, shared compressed ownership, release; original VM instructions=0; no playback");
    drop(game);heap_meter::snapshot("contract_after_game_drop");diagnostics::check()?;Ok(())
}
