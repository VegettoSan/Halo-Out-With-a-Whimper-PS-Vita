//! Decoded/validated registry handles. No native output is represented as playing.
use serde::{Serialize,Deserialize};
use crate::{host::{unavailable,Service},audio_source::Source};
#[path="audio_mp3.rs"] pub mod mp3;
#[derive(Clone,Serialize,Deserialize)] pub struct Mp3Handle { player:Box<mp3::Mp3Player>,id:i32 }
impl Drop for Mp3Handle {fn drop(&mut self){crate::diagnostic!("[mp3-release] id={} encoded_bytes={} shared_owners_before_drop={}",self.id,self.player.encoded_len(),self.player.encoded_owners());}}
#[derive(Clone,Serialize,Deserialize)] pub struct WavHandle { _unconstructible:() }
impl WavHandle {pub fn set_volume(&self,_vol:f64){unavailable(Service::Audio,"set_volume")}}
pub struct AudioManager;
impl AudioManager {
    pub fn deferred()->Self {Self}
    pub fn add_mp3(&mut self,file:Box<[u8]>,id:i32)->Option<Mp3Handle> {
        let bytes=file.len();let sha=crate::probe_sha256::digest(&file);
        let start=std::time::Instant::now();
        let mut player=match mp3::Mp3Player::new(file) {Ok(p)=>p,Err(_)=>{
            crate::diagnostic!("[mp3-rejected] id={} encoded_bytes={} reason=no_valid_stream",id,bytes);return None;
        }};
        // Reuse the actual OpenGMK streaming player, retaining only one small PCM buffer.
        let mut pcm=[0.0f32;rmp3::MAX_SAMPLES_PER_FRAME];
        let mut count=0usize;let mut nonzero=0usize;let mut peak=0.0f32;let mut squares=0.0f64;
        loop {
            let n=player.write_samples(&mut pcm);
            if n==0 {break;}
            for x in &pcm[..n] {
                if !x.is_finite(){crate::diagnostic!("[mp3-rejected] id={} reason=nonfinite_pcm",id);return None;}
                nonzero+=usize::from(*x!=0.0);peak=peak.max(x.abs());squares+=f64::from(*x)*f64::from(*x);
            }
            count+=n;
        }
        let channels=player.channel_count().get();let rate=player.sample_rate().get();
        if count==0 || count!=player.length()*usize::from(channels) {
            crate::diagnostic!("[mp3-rejected] id={} reason=empty_or_length_mismatch samples={} declared_per_channel={} channels={}",id,count,player.length(),channels);return None;
        }
        player.reset();
        crate::diagnostic!("[mp3-decoded] id={} input_sha256={} encoded_bytes={} channels={} rate={} pcm_samples={} nonzero_samples={} peak={} rms={} elapsed_us={} pcm_retained_bytes={} full_pcm_retained=false output_started=false",id,sha,bytes,channels,rate,count,nonzero,peak,(squares/count as f64).sqrt(),start.elapsed().as_micros(),rmp3::MAX_SAMPLES_PER_FRAME*std::mem::size_of::<f32>());
        crate::heap_meter::snapshot("mp3_decoded");crate::diagnostics::native_memory("mp3_decoded");
        Some(Mp3Handle {player:Box::new(player),id})
    }
    pub fn registered_details(h:&Mp3Handle)->(i32,usize,u16,u32,usize) {
        (h.id,h.player.encoded_len(),h.player.channel_count().get(),h.player.sample_rate().get(),h.player.length())
    }
    pub fn shared_owners(h:&Mp3Handle)->usize {h.player.encoded_owners()}
    // UNSUPPORTED_METHODS
}
#[derive(Clone,Serialize,Deserialize)] pub struct AudioState;
