//! Explicit CPU-only service fixture; never modifies the original game profile.
use crate::{game::Game,gml::Value};
pub fn run(game:&mut Game)->Result<(),Box<dyn std::error::Error>> {
    let counts=crate::host::counts().0;
    assert_eq!(game.file_exists(&["never-created.ini".into()])?,Value::from(false));
    assert!(game.file_exists(&["../outside.ini".into()]).is_err());
    assert!(game.file_exists(&["C:/outside.ini".into()]).is_err());
    assert!(game.file_exists(&["/outside.ini".into()]).is_err());
    game.ini_open(&["contract.ini".into()])?;
    assert_eq!(game.ini_read_real(&["Section".into(),"missing".into(),1.25.into()])?,Value::from(1.25));
    game.ini_write_real(&["Section".into(),"number".into(),123.5.into()])?;
    game.ini_write_string(&["Section".into(),"text".into(),"persisted".into()])?;
    assert_eq!(game.file_exists(&["contract.ini".into()])?,Value::from(true));
    game.ini_close(&[])?;game.ini_open(&["contract.ini".into()])?;
    assert_eq!(game.ini_read_real(&["Section".into(),"number".into(),0.into()])?,Value::from(123.5));
    assert_eq!(game.ini_read_string(&["Section".into(),"text".into(),"wrong".into()])?,Value::from("persisted"));
    game.ini_close(&[])?;
    let dir=crate::menu_files::resolve("directory.ini")?;std::fs::create_dir(&dir)?;
    assert_eq!(game.file_exists(&["directory.ini".into()])?,Value::from(false));
    assert!(game.ini_open(&["directory.ini".into()]).is_err());
    game.ini_open(&["absent-parent/contract.ini".into()])?;
    assert!(game.ini_write_real(&["S".into(),"K".into(),1.into()]).is_err());
    assert!(game.ini_close(&[]).is_err());
    assert_eq!(counts,crate::host::counts().0);
    crate::diagnostic!("FILES_CONTRACT_PASS real existence, missing defaults, write-through/sync, reopen, directory rejection, path rejection, write failure; VM instructions unchanged={}",counts);
    Ok(())
}
