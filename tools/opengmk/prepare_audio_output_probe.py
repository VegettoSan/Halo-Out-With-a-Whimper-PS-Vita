#!/usr/bin/env python3
"""E025: reuse existing mixer/players/transforms with a real SceAudioOut sink."""
import argparse,subprocess,shutil
from pathlib import Path
from prepare_vm_probe import close

def extend_audio(root,reference,udon):
    src=root/'gm8emulator/src';own=Path(__file__).with_name('audio')
    for name in ['wav','resampler','rechanneler','cycle']:
        s=(udon/(name+'.rs')).read_text(encoding='utf-8').replace('crate::source','crate::audio_source').replace('crate::{source::','crate::{audio_source::')
        s=s.replace('#[cfg_attr(feature = "serde-derives", derive(serde::Serialize, serde::Deserialize))]','#[derive(serde::Serialize,serde::Deserialize)]')
        if name=='wav':s=s.replace('file: Arc<[u8]>','file: Arc<Box<[u8]>>').replace('file: file.into()','file: Arc::new(file.into_boxed_slice())')
        (src/('audio_'+name+'.rs')).write_text(s,encoding='utf-8')
    p=src/'lib.rs';s=p.read_text(encoding='utf-8');s+='\n'+''.join(f'#[cfg(feature="vita2d")] pub mod audio_{n};\n' for n in ['wav','resampler','rechanneler','cycle']);p.write_text(s,encoding='utf-8')
    p=src/'audio_source.rs';s=p.read_text(encoding='utf-8');s+='''
impl<T:Source+?Sized> Source for Box<T> {
    fn channel_count(&self)->ChannelCount{(**self).channel_count()}
    fn sample_rate(&self)->SampleRate{(**self).sample_rate()}
    fn write_samples(&mut self,b:&mut[Sample])->usize{(**self).write_samples(b)}
    fn reset(&mut self){(**self).reset()}
}
''';p.write_text(s,encoding='utf-8')
    s=(reference/'gm8emulator/src/game/audio/mixer.rs').read_text(encoding='utf-8').replace('use udon::source::','use crate::audio_source::')
    (src/'game/audio_mixer.rs').write_text(s,encoding='utf-8')
    shutil.copyfile(own/'native_output.rs',src/'game/native_output.rs')
    shutil.copyfile(own/'contract.rs',src/'bin/audio_output_contract.rs')
    p=root/'gm8emulator/Cargo.toml';p.write_text(p.read_text(encoding='utf-8')+'\n[[bin]]\nname="audio-output-contract"\npath="src/bin/audio_output_contract.rs"\nrequired-features=["vita2d"]\n',encoding='utf-8')
    old=(src/'game/deferred_audio.rs').read_text(encoding='utf-8')
    a=old.index('    pub fn add_mp3(');validated=old[a:close(old,old.index('{',a))]
    s=(reference/'gm8emulator/src/game/audio.rs').read_text(encoding='utf-8')
    s=s.replace('mod mixer;','#[path="audio_mixer.rs"] pub mod mixer;\n#[path="native_output.rs"] pub mod native_output;')
    s=s.replace('mod mp3;','#[path="audio_mp3.rs"] pub mod mp3;')
    s=s.replace('use udon::{','use crate::{').replace('cycle::Cycle','audio_cycle::Cycle').replace('rechanneler::Rechanneler','audio_rechanneler::Rechanneler').replace('resampler::Resampler','audio_resampler::Resampler').replace('    session::{Api, Session},\n','').replace('source::{ChannelCount, Sample, SampleRate, Source}','audio_source::{ChannelCount, Sample, SampleRate, Source}').replace('wav::WavPlayer','audio_wav::WavPlayer')
    s=s.replace('    player: Mp3Player,','    player: Box<Mp3Player>,').replace('pub struct AudioManager {','pub struct AudioManager {\n    output:Option<native_output::NativeOutput>,')
    a=s.index('    pub fn new(',s.index('impl AudioManager {'));b=close(s,s.index('{',a))
    s=s[:a]+'''    pub fn deferred()->Self {
        let rate=SampleRate::new(44100).unwrap();let channels=ChannelCount::new(2).unwrap();
        let global_volume=Arc::new(AtomicU32::new(1f32.to_bits()));
        let (mixer,mixer_handle)=Mixer::new(rate,channels,global_volume.clone());
        Self{output:None,mixer:Some(mixer),sample_sender:None,mixer_handle,mixer_channel_count:channels,mixer_sample_rate:rate,do_output:false,global_volume,end_times:HashMap::new(),multimedia_end:None,audio_recorder:None}
    }
    fn ensure_output(&mut self) {
        if let Some(out)=&self.output {if let Err(e)=out.check(){panic!("AUDIO_FAIL {}",e);}return;}
        let mixer=self.mixer.take().expect("audio mixer absent after earlier output failure");
        self.output=Some(native_output::NativeOutput::start(mixer).unwrap_or_else(|e|panic!("AUDIO_FAIL {}",e)));
        self.do_output=true;
    }
    pub fn check_native(&self)->Result<(),String> {if let Some(o)=&self.output{o.check()}else{Ok(())}}
    pub fn log_native(&self) {if let Some(o)=&self.output{o.metrics();}}
'''+s[b:]
    a=s.index('    pub fn add_mp3(');b=close(s,s.index('{',a));s=s[:a]+validated+s[b:]
    for name in ['play_mp3','play_wav','loop_mp3','loop_wav']:
        a=s.index('    pub fn '+name+'(');i=s.index('{',a)+1;s=s[:i]+'\n        self.ensure_output();\n        crate::diagnostic!("[audio-command] '+name+' id={}",handle.id);'+s[i:]
    # Sender errors cannot masquerade as accepted playback/stop commands.
    import re
    start=0
    while True:
        a=s.find('let _ = self.mixer_handle.',start)
        if a<0:break
        b=s.index(';',a);expr=s[a+8:b]  # remove `let _ = `
        replacement=expr+'.unwrap_or_else(|e|panic!("AUDIO_QUEUE_FAIL {:?}",e));'
        s=s[:a]+replacement+s[b+1:];start=a+len(replacement)
    # E022 identity/ownership APIs remain available; no repeated decoder fixture.
    a=old.index('    pub fn registered_details(');b=old.index('    pub fn capture_audio(',a)
    s+='\nimpl AudioManager {\n'+old[a:b]+'}\n'
    (src/'game/deferred_audio.rs').write_text(s,encoding='utf-8')
    # Preserve loader-only metadata needed for genuinely lazy WAV registration.
    p=src/'asset/sound.rs';s=p.read_text(encoding='utf-8').replace('extension: Box<[u8]> },','extension: Box<[u8]>, volume:f64, use_3d:bool, exclusive:bool },');p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8').replace('data: b.data, extension: b.extension.0 }','data: b.data, extension: b.extension.0, volume:b.volume, use_3d:b.kind==SoundKind::ThreeDimensional, exclusive:b.kind==SoundKind::Multimedia }')
    at=s.index('    pub fn native_after_init(');part=s[at:].replace('            self.frame()?;','''            self.audio.check_native()?;
            if let Err(e)=self.frame() {
                crate::diagnostic!("[original-frame-error] completed={} attempted={} room={} instructions={} error={}",completed,completed+1,self.room.id,crate::host::counts().0,e);
                self.renderer.graphics_metrics("frame_error");crate::heap_meter::snapshot("frame_error");crate::diagnostics::native_memory("frame_error");let _=crate::diagnostics::check();
                return Err(e.into());
            }''',1);s=s[:at]+part
    s+='\n#[cfg(feature="vita2d")] impl Game {\n'+(own/'lazy_sound.rs').read_text(encoding='utf-8')+'\n}\n';p.write_text(s,encoding='utf-8')
    p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8')
    for name in ['sound_play','sound_loop','sound_stop','sound_stop_all','sound_isplaying','sound_volume','sound_global_volume']:
        a=s.index('    pub fn '+name+'(');b=close(s,s.index('{',a));body=s[a:b]
        body=body.replace('#[cfg(feature="headless")]','#[cfg(all(feature="headless",not(feature="vita2d")))]').replace('#[cfg(not(feature="headless"))]','#[cfg(any(not(feature="headless"),feature="vita2d"))]')
        if name in ['sound_play','sound_loop','sound_volume']:
            pos=body.index('        if let Some(sound)');body=body[:pos]+'        #[cfg(feature="vita2d")] self.ensure_native_sound(sound_id)?;\n'+body[pos:]
            body=body.replace('                FileType::None => (),','                FileType::None => (),\n                #[cfg(feature="headless")] FileType::Deferred{..}=>unreachable!("validated lazy registration"),')
        s=s[:a]+body+s[b:]
    p.write_text(s,encoding='utf-8')
    p=root/'gm8emulator/build.rs';s=p.read_text(encoding='utf-8').replace('"SceTouch_stub"]','"SceTouch_stub","SceAudio_stub"]');p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e024-{n:03}','e025-{n:03}').replace('E024_DIAGNOSTIC_STARTED','E025_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    # E024's sync-per-line instrumentation stalled visible frames. Buffer only
    # routine telemetry; force durable checkpoints at startup, panic, exit and
    # periodic frame boundaries. A mutex serializes audio/render writers.
    s=s.replace('io::{self,Write}','io::{self,Write,BufWriter}').replace('Mutex<Option<File>>','Mutex<Option<BufWriter<File>>>').replace('=Some(file);','=Some(BufWriter::with_capacity(16384,file));')
    s=s.replace('    eprintln!("{args}");','    #[cfg(not(target_os="vita"))] eprintln!("{args}");').replace('LOG.try_lock()','LOG.lock()').replace('writeln!(file,"{args}").and_then(|_|file.sync_all())','writeln!(file,"{args}")')
    s=s.replace('// File is unbuffered; synchronize each phase/service boundary before continuing.','// Routine telemetry is buffered; checkpoints remain explicit and durable.')
    s=s.replace('pub fn check()->io::Result<()> {','''pub fn checkpoint()->io::Result<()> {
    let result=(|| {let mut g=LOG.lock().map_err(|_|io::Error::other("diagnostic mutex poisoned"))?;if let Some(f)=g.as_mut(){f.flush()?;f.get_ref().sync_all()?;}Ok(())})();
    if result.is_err(){FAILED.store(true,Ordering::Relaxed);}result
}
pub fn check()->io::Result<()> {checkpoint()?;''')
    p.write_text(s,encoding='utf-8')
    p=src/'bin/vm_probe.rs';s=p.read_text(encoding='utf-8').replace('diagnostics::native_memory("panic");','diagnostics::native_memory("panic");let _=diagnostics::checkpoint();');p.write_text(s,encoding='utf-8')
    p=src/'game.rs';s=p.read_text(encoding='utf-8').replace('            if completed==1 || completed==60','            if completed%120==0 {crate::diagnostics::check()?;}\n            if completed==1 || completed==60');s=s.replace('crate::diagnostics::native_memory("native_frames");','crate::diagnostics::native_memory("native_frames");self.audio.log_native();');p.write_text(s,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_input_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend_audio(a.output,a.source,a.udon_source.parent);print('E025 existing mixer/MP3/WAV/transforms; real lazy native sink')
if __name__=='__main__':main()
