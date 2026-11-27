//! Synthetic counter protection fixture, not fabricated game frames.
fn main() {
    use gm8emulator::host;
    let directory=std::path::PathBuf::from(std::env::args_os().nth(1).expect("new private fixture directory required"));std::fs::create_dir(&directory).unwrap();
    let flag=directory.join("baseline.flag");gm8emulator::performance::configure(&flag).unwrap();assert!(!gm8emulator::performance::baseline());
    std::fs::write(&flag,b"diagnostic reference").unwrap();gm8emulator::performance::configure(&flag).unwrap();assert!(gm8emulator::performance::baseline());
    assert!(gm8emulator::performance::configure(&directory).is_err());
    std::fs::rename(&flag,directory.join("baseline.archived.flag")).unwrap();gm8emulator::performance::configure(&flag).unwrap();assert!(!gm8emulator::performance::baseline());
    for _ in 0..1100 {host::reset_frame_watchdog(2000);for _ in 0..1000 {host::instruction();}}
    assert!(host::counts().0>1_000_000);
    host::reset_frame_watchdog(2);host::instruction();host::instruction();
    assert!(std::panic::catch_unwind(host::instruction).is_err());
    host::reset_frame_watchdog(100);host::instruction();
    println!("PERFORMANCE_CONTRACT_PASS real diagnostic mode flag/error handling, cumulative>1M across synthetic frames allowed; actual per-frame budget violation panics; execution resumes only in this CPU fixture");
}
