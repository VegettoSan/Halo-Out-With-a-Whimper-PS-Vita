#!/usr/bin/env python3
"""Prepare a PRIVATE real-VM diagnostic SELF; VPK requires the owner's TITLE_ID.

No original game files are embedded. Uses only the installed hard-float SDK.
Preparation does not invent an ID, generate an SFO/VPK, install or upload anything.
"""
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
from vita_wsl_link import translate

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--prepare',action='store_true');mode.add_argument('--package',action='store_true')
 p.add_argument('--elf',type=Path);p.add_argument('--velf',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--title-id')
 p.add_argument('--wsl-distro',default='Ubuntu');p.add_argument('--sdk',default='/usr/local/vitasdk-hardfp');a=p.parse_args()
 root=Path(__file__).resolve().parents[2];out=a.output.resolve()
 if not out.is_relative_to(root/'build'):p.error('private output must stay under ignored build/')
 if a.package and (a.title_id is None or not re.fullmatch('[A-Z0-9]{9}',a.title_id)):p.error('owner-selected nine-character uppercase alphanumeric TITLE_ID required')
 def sdk(tool,*args):subprocess.run(['wsl','-d',a.wsl_distro,'--exec',a.sdk+'/bin/'+tool,*map(str,args)],check=True)
 if a.prepare:
  if a.title_id:p.error('preparation does not assign an ID; use --package only after owner selection')
  if not a.elf or not a.velf or out.exists():p.error('ELF, VELF and NEW output directory required')
  elf=a.elf.resolve();velf=a.velf.resolve()
  if not elf.is_relative_to(root/'build') or not velf.is_relative_to(root/'build'):p.error('use preserved ignored build artifacts')
  data=elf.read_bytes()
  if data[:5]!=b'\x7fELF\x01' or int.from_bytes(data[18:20],'little')!=40 or not int.from_bytes(data[36:40],'little')&0x400:p.error('expected ELF32 ARM hard-float')
  if b'E019_DIAGNOSTIC_STARTED' not in data or b'cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f' not in data:p.error('not the E019 original-data diagnostic')
  out.mkdir(parents=True);sdk('vita-make-fself','-s',translate(str(velf)),translate(str(out/'eboot.bin')))
  manifest={'utc_prepared':datetime.now(timezone.utc).isoformat(),'experiment':'E019','title_id':None,'device_execution':'UNTESTED','purpose':'load/verify original EXE, compile real scripts/events, execute startup until actual unavailable dialog','files':{'eboot.bin':{'sha256':sha(out/'eboot.bin'),'bytes':(out/'eboot.bin').stat().st_size}},'elf_sha256':sha(elf),'velf_sha256':sha(velf),'original_exe_sha256':'cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f','data_path':'ux0:data/howaw/HOWaW_FirefightDemov1.exe','logs':'ux0:data/howaw/diagnostics/e019-NNN/run.log','no_original_files_embedded':True,'vpk':None}
  (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
  print('Prepared real VM SELF + manifest; no TITLE_ID, SFO or VPK generated.');return
 manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
 if manifest['experiment']!='E019' or sha(out/'eboot.bin')!=manifest['files']['eboot.bin']['sha256']:p.error('prepared SELF identity mismatch')
 sfo=out/'sce_sys/param.sfo';vpk=out/'e019-private-diagnostic.vpk'
 if sfo.exists() or vpk.exists():p.error('preserve previous packaging; use a new prepared output')
 sfo.parent.mkdir(exist_ok=True)
 sdk('vita-mksfoex','-s','TITLE_ID='+a.title_id,'-s','APP_VER=00.19','HOWaW original VM diagnostic',translate(str(sfo)))
 with zipfile.ZipFile(vpk,'x',compression=zipfile.ZIP_DEFLATED) as archive:
  for name in ['eboot.bin','sce_sys/param.sfo']:archive.write(out/name,name)
 with zipfile.ZipFile(vpk) as archive:
  if archive.namelist()!=['eboot.bin','sce_sys/param.sfo'] or archive.testzip() is not None:raise RuntimeError('VPK validation failed')
 package={'utc':datetime.now(timezone.utc).isoformat(),'owner_title_id':a.title_id,'vpk_sha256':sha(vpk),'self_sha256':sha(out/'eboot.bin'),'device_execution':'UNTESTED','original_files_embedded':False}
 (out/'package.json').write_text(json.dumps(package,indent=2),encoding='utf-8')
 print('Private diagnostic VPK created; install/boot/VM execution still UNTESTED.')
if __name__=='__main__':main()
