//! Keep the proven CDRAM working set; overflow pages use bounded native RAM.
const CDRAM:usize=64*1024*1024;
const MAIN:usize=32*1024*1024;
pub fn fits(cdram:usize,main:usize,bytes:usize,in_main:bool)->bool {
    cdram<=CDRAM && main<=MAIN && bytes>0 && if in_main {main.checked_add(bytes).is_some_and(|n|n<=MAIN)}else{cdram.checked_add(bytes).is_some_and(|n|n<=CDRAM)}
}
pub fn main_ram_for(cdram:usize,main:usize,bytes:usize)->Result<bool,String> {
    if fits(cdram,main,bytes,false){Ok(false)}
    else if fits(cdram,main,bytes,true){Ok(true)}
    else {Err("atlas pool budgets exceeded: CDRAM64 MiB + mapped main RAM32 MiB".into())}
}
#[cfg(test)] mod tests {
    use super::*;
    #[test] fn genuine_fifth_page_uses_main_and_total_stays_bounded() {
        let page=16*1024*1024;let(mut cd,mut ram)=(0,0);
        for i in 0..6 {let main=main_ram_for(cd,ram,page).unwrap();assert_eq!(main,i>=4);if main{ram+=page}else{cd+=page}}
        assert_eq!((cd,ram),(CDRAM,MAIN));assert!(main_ram_for(cd,ram,page).is_err());
        assert!(!fits(cd,ram,usize::MAX,true));assert!(!fits(usize::MAX,0,page,false));assert!(main_ram_for(0,0,0).is_err());
    }
}
