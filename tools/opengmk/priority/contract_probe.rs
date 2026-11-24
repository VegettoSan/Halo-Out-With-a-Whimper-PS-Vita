//! Bounded current-child OS checks, never changes the parent/system policy.
#[cfg(windows)]
fn main()->Result<(),Box<dyn std::error::Error>> {
    use gm8emulator::{process_priority as p,probe_sha256 as sha,host::PlatformServices,runtime_services::RuntimeServices};
    assert_eq!(sha::digest(b""),"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    assert_eq!(sha::digest(b"abc"),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    assert_eq!(sha::digest(b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"),"248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
    let saved=p::windows::current()?;
    struct Restore((u32,i32));impl Drop for Restore {fn drop(&mut self){let _=p::windows::set(self.0.0,self.0.1);}}
    let restore=Restore(saved);
    let services=RuntimeServices {interactive_dialog:false};
    // Only 0/1/2 occur in this game. Do not run real-time mode as an exploratory test.
    for priority in [0,1,2] {
        services.set_program_priority(priority)?;
        assert_eq!(p::windows::current()?,p::requested(priority));
        println!("PRIORITY_PASS argument={} readback={:?}",priority,p::windows::current()?);
    }
    // Pure table checks for the rest, no scheduling side effects.
    assert_eq!((-3..=3).map(p::requested).collect::<Vec<_>>(),vec![(0x40,-15),(0x20,-2),(0x20,-1),(0x20,0),(0x20,1),(0x80,2),(0x100,15)]);
    drop(restore);assert_eq!(p::windows::current()?,saved);
    println!("PRIORITY_RESTORED {:?}; SHA256_KNOWN_VECTORS_PASS",saved);Ok(())
}
#[cfg(not(windows))] fn main(){eprintln!("Windows contract probe only");std::process::exit(2);}
