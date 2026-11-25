//! Real, bounded filesystem operations. Original data roots stay read only.
use std::{path::{Path,PathBuf,Component},sync::OnceLock,io};
static ROOTS:OnceLock<(PathBuf,PathBuf)>=OnceLock::new();
pub fn initialize(assets:PathBuf,saves:PathBuf)->io::Result<()> {
    std::fs::create_dir_all(&saves)?;
    ROOTS.set((assets,saves)).map_err(|_|io::Error::other("file roots already initialized"))
}
pub fn resolve(name:&str)->Result<PathBuf,String> {
    let normalized=name.replace('\\',"/");let path=Path::new(&normalized);
    if normalized.contains(':') || normalized.contains('\0') || path.is_absolute() || path.components().any(|c|!matches!(c,Component::Normal(_)|Component::CurDir)) {
        return Err("SERVICE_UNAVAILABLE/Files: absolute, parent or drive-qualified GML path requires an explicit mapping".into());
    }
    let (assets,saves)=ROOTS.get().ok_or("file roots not initialized")?;
    // INI writes/readback always address the dedicated persistent profile.
    let is_ini=path.extension().is_some_and(|e|e.eq_ignore_ascii_case("ini"));
    if is_ini {Ok(saves.join(path))}else{Ok(assets.join(path))}
}
pub fn exists(name:&str)->Result<bool,String> {
    let path=resolve(name)?;
    let value=match std::fs::metadata(&path) {
        Ok(m)=>m.is_file(),Err(e) if e.kind()==io::ErrorKind::NotFound=>false,
        Err(e)=>return Err(format!("file_exists: {e}")),
    };
    crate::diagnostic!("[file-exists] logical={:?} actual={} exists={}",name,path.display(),value);Ok(value)
}
pub fn sync(path:&str)->Result<(),String> {
    std::fs::OpenOptions::new().read(true).write(true).open(path).and_then(|f|f.sync_all()).map_err(|e|e.to_string())
}
