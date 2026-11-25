#!/usr/bin/env python3
"""E023: original Draw, faithful 2D depth contract and real offscreen GXM proof."""
import argparse,subprocess
from pathlib import Path
from prepare_vm_probe import close

def extend_draw(root):
    src=root/'gm8emulator/src'
    # Static original menu Draw requires these functions. Preserve original
    # conversion, state updates, glyph rendering and call ordering.
    p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8')
    for name in ['draw_set_blend_mode','draw_rectangle','draw_rectangle_color']:
        a=s.index('    pub fn '+name+'(');b=close(s,s.index('{',a));body=s[a:b]
        body=body.replace('#[cfg(feature="headless")]','#[cfg(all(feature="headless",not(feature="vita2d")))]')
        body=body.replace('#[cfg(not(feature="headless"))]','#[cfg(any(not(feature="headless"),feature="vita2d"))]')
        s=s[:a]+body+s[b:]
    for name in ['draw_set_blend_mode','draw_rectangle','draw_rectangle_color','draw_background_ext','draw_background_tiled_ext','draw_sprite_ext','draw_set_font','draw_text']:
        a=s.index('    pub fn '+name+'(');at=s.index('{',a)+1
        s=s[:at]+f'\n        #[cfg(feature="vita2d")] {{static ONCE:std::sync::atomic::AtomicBool=std::sync::atomic::AtomicBool::new(false);if !ONCE.swap(true,std::sync::atomic::Ordering::Relaxed) {{crate::diagnostic!("[original-graphics-call] {name}");}}}}'+s[at:]
    p.write_text(s,encoding='utf-8')
    p=src/'game/draw.rs';s=p.read_text(encoding='utf-8')
    a=s.index('            #[cfg(feature="vita2d")] {\n                crate::diagnostic!("[graphics-stop]')
    b=s.index('self.renderer.clear_zbuf();',a)+len('self.renderer.clear_zbuf();')
    s=s[:a]+'            self.renderer.clear_zbuf();'+s[b:]
    marker='                    // Custom draw event\n'
    assert s.count(marker)==1
    s=s.replace(marker,marker+'                    #[cfg(feature="vita2d")] crate::diagnostic!("[original-object-draw] object={} instance={} event=Draw/0",instance.object_index.get(),instance.id.get());\n')
    p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e022-{n:03}','e023-{n:03}').replace('E022_DIAGNOSTIC_STARTED','E023_DIAGNOSTIC_STARTED');p.write_text(s,encoding='utf-8')
    # Validate PCM during the existing length scan. No hash-based success cache:
    # every candidate is still decoded, including invalid/nonfinite rejection.
    p=src/'game/audio_mp3.rs';s=p.read_text(encoding='utf-8')
    marker='    length: usize,';assert marker in s
    s=s.replace(marker,'    #[serde(default)]\n    scan: Scan,\n'+marker,1)
    marker='            let mut length = 0;'
    s=s.replace(marker,marker+'\n            let mut scan=Scan::default();',1)
    marker='                        length += audio.sample_count();';assert s.count(marker)==1
    s=s.replace(marker,marker+'''
                        for x in audio.samples() {
                            if !x.is_finite() {return Err(Error::InvalidFile);}
                            scan.samples+=1;scan.nonzero+=usize::from(*x!=0.);
                            scan.peak=scan.peak.max(x.abs());scan.squares+=f64::from(*x)*f64::from(*x);
                        }''',1)
    marker='            let buffer = unsafe {'
    s=s.replace(marker,'            if scan.samples==0 || scan.samples!=length*usize::from(channels) {return Err(Error::InvalidFile);}\n\n'+marker,1)
    s=s.replace('                length,','                length,scan,',1)
    s+='''
#[derive(Clone,Default,Serialize,Deserialize)]
pub struct Scan {pub samples:usize,pub nonzero:usize,pub peak:f32,pub squares:f64}
impl Mp3Player {pub fn scan(&self)->&Scan {&self.scan}}
'''
    p.write_text(s,encoding='utf-8')
    p=src/'game/deferred_audio.rs';s=p.read_text(encoding='utf-8').replace('let mut player=match','let player=match')
    a=s.index('        // Reuse the actual OpenGMK streaming player,');b=s.index('        crate::diagnostic!("[mp3-decoded]',a)
    s=s[:a]+'''        let scan=player.scan();
        let (count,nonzero,peak,squares)=(scan.samples,scan.nonzero,scan.peak,scan.squares);
        let channels=player.channel_count().get();let rate=player.sample_rate().get();
        crate::diagnostic!("[mp3-scan] passes=1 validation_in_length_scan=true cached_success=false output_started=false");
'''+s[b:]
    p.write_text(s,encoding='utf-8')
    # Separate CPU contract checks the changed decoder scan against its real
    # streaming output once. This does not run another full registry fixture.
    p=src/'bin/mp3_scan_contract.rs'
    p.write_text('''use gm8emulator::{game::audio::mp3::Mp3Player,audio_source::Source};
fn main() {
    let file=std::fs::read(std::env::args_os().nth(1).expect("original MP3 path")).unwrap();
    assert_eq!(gm8emulator::probe_sha256::digest(&file),"e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0");
    let mut player=Mp3Player::new(file).unwrap_or_else(|_|panic!("valid MP3 rejected"));
    let scan=player.scan().clone();
    let (mut count,mut nonzero,mut peak,mut squares)=(0usize,0usize,0f32,0f64);
    let mut pcm=[0f32;rmp3::MAX_SAMPLES_PER_FRAME];
    loop {let n=player.write_samples(&mut pcm);if n==0 {break;} for x in &pcm[..n] {assert!(x.is_finite());count+=1;nonzero+=usize::from(*x!=0.);peak=peak.max(x.abs());squares+=f64::from(*x)*f64::from(*x);}}
    assert_eq!((scan.samples,scan.nonzero,scan.peak,scan.squares),(count,nonzero,peak,squares));
    assert_eq!((count,nonzero,peak),(7_130_880,7_129_724,1.0173236));
    assert_eq!(player.length(),3_565_440);
    assert!(Mp3Player::new(Vec::new()).is_err());assert!(Mp3Player::new(b"invalid MPEG".to_vec()).is_err());
    println!("SCAN_CONTRACT_PASS samples={count} nonzero={nonzero} peak={peak} rms={} one_pass_matches_streaming=true invalid_rejected=true",(squares/count as f64).sqrt());
}
''',encoding='utf-8')
    p=root/'gm8emulator/Cargo.toml';p.write_text(p.read_text(encoding='utf-8')+'\n[[bin]]\nname="mp3-scan-contract"\npath="src/bin/mp3_scan_contract.rs"\nrequired-features=["vita2d"]\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_mp3_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    extend_draw(a.output)
    print('E023: original 2D Draw restored; real depth contract on native device initialization; single MP3 scan')
if __name__=='__main__':main()
