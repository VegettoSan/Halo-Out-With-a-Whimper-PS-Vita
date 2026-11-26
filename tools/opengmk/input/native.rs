use std::sync::{Mutex,OnceLock};
use super::input_mapper::{Mapper,Sample};
struct State {mapper:Mapper,last:std::time::Instant,polls:u64}
static STATE:OnceLock<Mutex<State>>=OnceLock::new();
#[cfg(target_os="vita")] extern "C" {fn howaw_input_init()->i32;fn howaw_input_sample(out:*mut u32)->i32;}
pub fn poll(game:&mut crate::game::Game)->Result<(),String> {
    #[cfg(not(target_os="vita"))] {let _=game;return Err("SERVICE_UNAVAILABLE/Window: real Vita input requires hardware".into());}
    #[cfg(target_os="vita")] unsafe {
        if STATE.get().is_none() {
            let rc=howaw_input_init();if rc<0{return Err(format!("input initialization rc={rc}"));}
            let _=STATE.set(Mutex::new(State{mapper:Mapper::default(),last:std::time::Instant::now(),polls:0}));
            crate::diagnostic!("[input-init] real Ctrl analog + front Touch; X=mouse-left R=mouse-right Start=Enter Select=Escape; left-stick=WASD dpad=arrows Circle=Space Square=R Triangle=E L=Shift; right-stick=cursor");
        }
        let mut out=[0u32;10];let rc=howaw_input_sample(out.as_mut_ptr());if rc!=0{return Err(format!("input sample rc={rc}; no state fabricated"));}
        let touch=if out[5]>0 {
            let (minx,maxx)=((out[8]>>16) as f64,(out[8]&65535) as f64);
            let (miny,maxy)=((out[9]>>16) as f64,(out[9]&65535) as f64);
            if maxx<=minx || maxy<=miny{return Err("invalid touch bounds".into());}
            Some([(out[6] as i32 as f64-minx)*960./(maxx-minx),(out[7] as i32 as f64-miny)*544./(maxy-miny)])
        } else {None};
        let mut s=STATE.get().unwrap().lock().map_err(|_|"input mutex poisoned")?;
        let now=std::time::Instant::now();let dt=now.duration_since(s.last).as_secs_f64();s.last=now;s.polls+=1;
        let changes=s.mapper.apply(&mut game.input,Sample{buttons:out[0],axes:[out[1] as u8,out[2] as u8,out[3] as u8,out[4] as u8],touch},dt,[game.window_inner_size.0,game.window_inner_size.1]);
        if s.polls<=3 || changes>0 || s.polls%120==0 {crate::diagnostic!("[input-sample] poll={} buttons=0x{:x} axes={},{},{},{} contacts={} transitions={} cursor={},{}",s.polls,out[0],out[1],out[2],out[3],out[4],out[5],changes,game.input.mouse_x(),game.input.mouse_y());}
        Ok(())
    }
}
