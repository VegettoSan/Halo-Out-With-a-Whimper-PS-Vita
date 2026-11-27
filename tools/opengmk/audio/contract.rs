use gm8emulator::{audio_source::{Source,SampleRate,ChannelCount},audio_wav::WavPlayer,audio_resampler::Resampler,audio_rechanneler::Rechanneler,audio_cycle::Cycle,game::audio::{mixer::Mixer,SoundParams,native_output::{NativeOutput,pcm16}}};
use std::sync::{Arc,atomic::AtomicU32};
fn main() {
    let mut bins=[0usize;129];bins[1]=2;bins[12]=6;bins[88]=2;
    assert_eq!(gm8emulator::game::audio::native_output::histogram_quantiles(&bins,90000),(10,12999,88999));
    bins=[0;129];bins[128]=1;assert_eq!(gm8emulator::game::audio::native_output::histogram_quantiles(&bins,300000),(1,300000,300000));
    assert_eq!(std::mem::align_of::<gm8emulator::game::audio::native_output::PcmBlock>(),64);
    assert_eq!(std::mem::size_of::<gm8emulator::game::audio::native_output::PcmBlock>(),4096);
    let dir=std::env::args_os().nth(2).expect("new private diagnostic directory required");gm8emulator::diagnostics::open(std::path::Path::new(&dir)).unwrap();
    let jobs:Vec<_>=(0..2).map(|writer|std::thread::spawn(move ||for n in 0..20 {gm8emulator::diagnostic!("[concurrent-log-contract] writer={} item={}",writer,n);})).collect();
    for job in jobs {job.join().unwrap();}gm8emulator::diagnostics::check().unwrap();
    let log=std::fs::read_to_string(gm8emulator::diagnostics::workspace().unwrap().join("run.log")).unwrap();assert_eq!(log.matches("[concurrent-log-contract]").count(),40);
    let mut pcm=[0i16;7];assert_eq!(pcm16(&[-2.,-1.,-0.5,0.,0.5,1.,2.],&mut pcm).unwrap(),(6,2));assert_eq!(pcm,[i16::MIN,i16::MIN,-16384,0,16384,i16::MAX,i16::MAX]);assert!(pcm16(&[f32::NAN],&mut[0]).is_err());
    let mut bytes=std::fs::read(std::env::args_os().nth(1).expect("copied EXE required")).unwrap();assert_eq!(gm8emulator::probe_sha256::digest(&bytes),"cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f");
    let mut assets=gm8exe::reader::from_exe(&mut bytes,None::<fn(&str)>,true,false).unwrap();drop(bytes);
    let (id,sound)=assets.sounds.iter_mut().enumerate().filter_map(|(i,s)|s.as_mut().map(|s|(i,s))).find(|(_,s)|s.extension.0.as_ref()==b".wav" && s.data.is_some()).expect("original WAV absent");
    let data=sound.data.take().unwrap();let sha=gm8emulator::probe_sha256::digest(&data);let player=WavPlayer::new(data).unwrap();
    let details=(player.channel_count().get(),player.sample_rate().get(),player.length());
    let global=Arc::new(AtomicU32::new(1f32.to_bits()));let (mut mixer,h)=Mixer::new(SampleRate::new(44100).unwrap(),ChannelCount::new(2).unwrap(),global);
    h.add(Cycle::new(Rechanneler::new(Resampler::new(player,SampleRate::new(44100).unwrap()),ChannelCount::new(2).unwrap())),Arc::new(SoundParams{volume:AtomicU32::new(1f32.to_bits())}),id as i32).unwrap();
    let mut floats=[0f32;2048];let mut output=[0i16;2048];let mut nonzero=0;
    for _ in 0..32 {assert_eq!(mixer.write_samples(&mut floats),2048);nonzero+=pcm16(&floats,&mut output).unwrap().0;}
    assert!(nonzero>0);h.stop(id as i32).unwrap();mixer.write_samples(&mut floats);assert!(floats.iter().all(|x|*x==0.));
    assert!(NativeOutput::start(mixer).is_err());
    println!("AUDIO_CPU_CONTRACT_PASS original_wav_id={} sha256={} channels={} rate={} samples={} mixed_nonzero_pcm={} looping_source_stopped=true clipping_finite_checks=true native_sink_unavailable_on_host=true; no VM or native audio success claim",id,sha,details.0,details.1,details.2,nonzero);
}
