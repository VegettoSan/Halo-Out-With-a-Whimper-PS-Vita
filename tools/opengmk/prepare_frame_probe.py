#!/usr/bin/env python3
"""E029: real GML debug sink and conservative viewport culling for every room."""
import argparse,subprocess,shutil
from pathlib import Path
from prepare_vm_probe import close

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--udon-source',type=Path,required=True);a=p.parse_args()
    subprocess.run(['python',str(Path(__file__).with_name('prepare_crop_probe.py')),'--source',str(a.source),'--output',str(a.output),'--udon-source',str(a.udon_source)],check=True)
    src=a.output/'gm8emulator/src';p=src/'gml/kernel.rs';s=p.read_text(encoding='utf-8');start=s.index('    pub fn show_debug_message(');end=close(s,s.index('{',start));body=s[start:end]
    body=body.replace('#[cfg(feature="headless")]','#[cfg(all(feature="headless",not(feature="vita2d")))]').replace('#[cfg(not(feature="headless"))]','#[cfg(any(not(feature="headless"),feature="vita2d"))]')
    marker='        println!("{}", self.decode_str(message.repr().as_ref()));';assert marker in body
    body=body.replace(marker,'''        #[cfg(feature="vita2d")] {
            crate::diagnostic!("[gml-debug] {}",self.decode_str(message.repr().as_ref()));
            crate::diagnostics::status().map_err(|e|gml::Error::FunctionError("show_debug_message".into(),e.to_string()))?;
        }
        #[cfg(not(feature="vita2d"))]
'''+marker)
    s=s[:start]+body+s[end:];p.write_text(s,encoding='utf-8')
    p=src/'diagnostics.rs';s=p.read_text(encoding='utf-8').replace('e028-{n:03}','e029-{n:03}').replace('E028_DIAGNOSTIC_STARTED','E029_DIAGNOSTIC_STARTED')
    s+='\npub fn status()->io::Result<()> {if FAILED.load(Ordering::Relaxed){Err(io::Error::other("persistent diagnostic write failed"))}else{Ok(())}}\n';p.write_text(s,encoding='utf-8')
    shutil.copyfile(Path(__file__).with_name('frame_contract.rs'),src/'bin/frame_contract.rs')
    p=a.output/'gm8emulator/Cargo.toml';s=p.read_text(encoding='utf-8')+'\n[[bin]]\nname="frame-contract"\npath="src/bin/frame_contract.rs"\nrequired-features=["vita2d"]\n';p.write_text(s,encoding='utf-8')
    print('E029 all-room conservative clip rejection + measured temporary pool, genuine buffered GML debug output')
if __name__=='__main__':main()
