//! Checked native sink for the existing OpenGMK mixer. No decoder/mixer rewrite.
use super::mixer::Mixer;
use crate::audio_source::Source;
use std::sync::{Arc,atomic::{AtomicBool,AtomicI32,AtomicUsize,Ordering}};
#[derive(Default)] struct Counters {blocks:AtomicUsize,nonzero:AtomicUsize,clips:AtomicUsize,max_us:AtomicUsize}
pub struct NativeOutput {stop:Arc<AtomicBool>,error:Arc<AtomicI32>,stats:Arc<Counters>,thread:Option<std::thread::JoinHandle<()>>}
#[cfg(target_os="vita")] extern "C" {
    fn sceAudioOutOpenPort(kind:i32,len:i32,freq:i32,mode:i32)->i32;
    fn sceAudioOutOutput(port:i32,data:*const i16)->i32;
    fn sceAudioOutReleasePort(port:i32)->i32;
    fn sceAudioOutGetConfig(port:i32,kind:i32)->i32;
}
pub fn pcm16(src:&[f32],dst:&mut[i16])->Result<(usize,usize),String> {
    if src.len()!=dst.len(){return Err("PCM conversion length mismatch".into());}
    let (mut nonzero,mut clipped)=(0,0);
    for (x,y) in src.iter().zip(dst) {
        if !x.is_finite(){return Err("nonfinite mixed PCM".into());}
        clipped+=usize::from(x.abs()>1.);
        *y=if *x<=-1.{i16::MIN}else if *x>=1.{i16::MAX}else{(x*32768.).round() as i16};
        nonzero+=usize::from(*y!=0);
    }
    Ok((nonzero,clipped))
}
impl NativeOutput {
    pub fn start(mut mixer:Mixer)->Result<Self,String> {
        #[cfg(not(target_os="vita"))] {let _=&mut mixer;return Err("SERVICE_UNAVAILABLE/Audio: native SceAudioOut requires Vita".into());}
        #[cfg(target_os="vita")] unsafe {
            // BGM supports the original 44.1 kHz stream; MAIN requires 48 kHz.
            let port=sceAudioOutOpenPort(1,1024,44100,1);
            if port<0{return Err(format!("sceAudioOutOpenPort rc={port}"));}
            if sceAudioOutGetConfig(port,0)!=1024 || sceAudioOutGetConfig(port,1)!=44100 || sceAudioOutGetConfig(port,2)!=1 {
                let rc=sceAudioOutReleasePort(port);return Err(format!("audio config readback mismatch; release={rc}"));
            }
            let stop=Arc::new(AtomicBool::new(false));let error=Arc::new(AtomicI32::new(0));
            let stats=Arc::new(Counters::default());let counters=stats.clone();
            let (quit,failed)=(stop.clone(),error.clone());
            let thread=match std::thread::Builder::new().name("howaw-audio".into()).stack_size(256*1024).spawn(move || {
                let mut floats=[0f32;2048];let mut pcm=[0i16;2048];
                let (mut blocks,mut nonzero,mut clips)=(0u64,0u64,0u64);let mut max_us=0;
                while !quit.load(Ordering::Acquire) {
                    let start=std::time::Instant::now();
                    let n=mixer.write_samples(&mut floats);
                    if n!=floats.len(){failed.store(-1001,Ordering::Release);break;}
                    let (nz,clipped)=match pcm16(&floats,&mut pcm){Ok(v)=>v,Err(e)=>{crate::diagnostic!("AUDIO_PCM_FAIL {}",e);failed.store(-1002,Ordering::Release);break;}};
                    max_us=max_us.max(start.elapsed().as_micros());
                    let rc=sceAudioOutOutput(port,pcm.as_ptr());if rc<0{failed.store(rc,Ordering::Release);break;}
                    blocks+=1;nonzero+=nz as u64;clips+=clipped as u64;
                    // No routine file I/O on the audio thread. Main-loop checkpoints
                    // read these counters; a disk sync must not stall audio output.
                    counters.blocks.store(blocks as usize,Ordering::Release);counters.nonzero.store(nonzero as usize,Ordering::Release);counters.clips.store(clips as usize,Ordering::Release);counters.max_us.store(max_us as usize,Ordering::Release);
                }
                let drain=sceAudioOutOutput(port,std::ptr::null());let release=sceAudioOutReleasePort(port);
                if drain<0 {failed.store(drain,Ordering::Release);}if release<0{failed.store(release,Ordering::Release);}
                crate::diagnostic!("[audio-worker-end] blocks={} nonzero_pcm_samples={} drain={} release={} error={}",blocks,nonzero,drain,release,failed.load(Ordering::Acquire));
            }) {Ok(t)=>t,Err(e)=>{let rc=sceAudioOutReleasePort(port);return Err(format!("audio thread spawn: {e}; port release={rc}"));}};
            crate::diagnostic!("[audio-native-open] BGM port={} channels=2 rate=44100 frames_per_block=1024 readback_verified=true; no audible-success claim",port);
            Ok(Self{stop,error,stats,thread:Some(thread)})
        }
    }
    pub fn check(&self)->Result<(),String> {
        let rc=self.error.load(Ordering::Acquire);
        if rc!=0{return Err(format!("native audio worker failed rc={rc}"));}
        if !self.stop.load(Ordering::Acquire) && self.thread.as_ref().is_some_and(|t|t.is_finished()){return Err("native audio worker terminated unexpectedly".into());}
        Ok(())
    }
    pub fn metrics(&self) {
        let blocks=self.stats.blocks.load(Ordering::Acquire);
        crate::diagnostic!("[audio-output] blocks={} submitted_pcm_samples={} nonzero_pcm_samples={} clipped_samples={} max_mix_convert_us={} error={}; audible observation separate",blocks,blocks*2048,self.stats.nonzero.load(Ordering::Acquire),self.stats.clips.load(Ordering::Acquire),self.stats.max_us.load(Ordering::Acquire),self.error.load(Ordering::Acquire));
    }
}
impl Drop for NativeOutput {fn drop(&mut self){self.stop.store(true,Ordering::Release);if self.thread.take().is_some_and(|t|t.join().is_err()){crate::diagnostic!("AUDIO_WORKER_PANIC");}if let Err(e)=self.check(){crate::diagnostic!("AUDIO_CLEANUP_FAIL {}",e);}}}
