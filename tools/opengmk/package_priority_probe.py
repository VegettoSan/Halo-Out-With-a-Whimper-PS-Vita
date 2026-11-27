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
 p.add_argument('--elf',type=Path);p.add_argument('--velf',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--title-id');p.add_argument('--app-version',default='00.19')
 p.add_argument('--wsl-distro',default='Ubuntu');p.add_argument('--sdk',default='/usr/local/vitasdk-hardfp');p.add_argument('--experiment',choices=['E019','E020','E021','E022','E023','E024','E025','E026','E027','E028','E029','E030','E031','E032'],default='E019');a=p.parse_args()
 root=Path(__file__).resolve().parents[2];out=a.output.resolve()
 if not out.is_relative_to(root/'build'):p.error('private output must stay under ignored build/')
 if not re.fullmatch(r'\d{2}\.\d{2}',a.app_version):p.error('APP_VER must have NN.NN format')
 if a.package and (a.title_id is None or not re.fullmatch('[A-Z0-9]{9}',a.title_id)):p.error('owner-selected nine-character uppercase alphanumeric TITLE_ID required')
 if a.experiment in ['E020','E021','E022','E023','E024','E025','E026','E027','E028','E029','E030','E031','E032'] and a.package and a.title_id!='HOWAW1178':p.error('retain owner-selected HOWAW1178')
 if a.experiment=='E021' and a.package and a.app_version!='00.22':p.error('E021 private diagnostic requires 00.22')
 if a.experiment=='E022' and a.package and a.app_version!='00.23':p.error('E022 private diagnostic requires 00.23')
 if a.experiment=='E023' and a.package and a.app_version!='00.24':p.error('E023 private diagnostic requires 00.24')
 if a.experiment=='E024' and a.package and a.app_version!='00.25':p.error('E024 private diagnostic requires 00.25')
 if a.experiment=='E025' and a.package and a.app_version!='00.26':p.error('E025 private diagnostic requires 00.26')
 if a.experiment=='E026' and a.package and a.app_version!='00.27':p.error('E026 private diagnostic requires 00.27')
 if a.experiment=='E027' and a.package and a.app_version!='00.28':p.error('E027 private diagnostic requires 00.28')
 if a.experiment=='E028' and a.package and a.app_version!='00.29':p.error('E028 private diagnostic requires 00.29')
 if a.experiment=='E029' and a.package and a.app_version!='00.30':p.error('E029 private diagnostic requires 00.30')
 if a.experiment=='E030' and a.package and a.app_version!='00.31':p.error('E030 private diagnostic requires 00.31')
 if a.experiment=='E031' and a.package and a.app_version!='00.32':p.error('E031 private diagnostic requires 00.32')
 if a.experiment=='E032' and a.package and a.app_version!='00.33':p.error('E032 private diagnostic requires 00.33')
 def sdk(tool,*args):subprocess.run(['wsl','-d',a.wsl_distro,'--exec',a.sdk+'/bin/'+tool,*map(str,args)],check=True)
 if a.prepare:
  if a.title_id:p.error('preparation does not assign an ID; use --package only after owner selection')
  if not a.elf or not a.velf or out.exists():p.error('ELF, VELF and NEW output directory required')
  elf=a.elf.resolve();velf=a.velf.resolve()
  if not elf.is_relative_to(root/'build') or not velf.is_relative_to(root/'build'):p.error('use preserved ignored build artifacts')
  data=elf.read_bytes()
  if data[:5]!=b'\x7fELF\x01' or int.from_bytes(data[18:20],'little')!=40 or not int.from_bytes(data[36:40],'little')&0x400:p.error('expected ELF32 ARM hard-float')
  if (a.experiment+'_DIAGNOSTIC_STARTED').encode() not in data or b'cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f' not in data:p.error('not the selected original-data diagnostic')
  if a.experiment=='E020' and b'VISUAL_PROBE_COMPLETED' not in data:p.error('E020 visual diagnostic marker missing')
  if a.experiment=='E021' and (b'[priority-effects]' not in data or b'e021-profile' not in data or b'VISUAL_PROBE_COMPLETED' in data):p.error('E021 services required; E020 visual fixture must be absent')
  if a.experiment=='E022' and (b'[sound-replace-registered]' not in data or b'[original-draw-enter]' not in data or b'VISUAL_PROBE_COMPLETED' in data):p.error('E022 actual MP3 registry/Draw path required, no repeated logo fixture')
  if a.experiment=='E023' and (any(m not in data for m in [b'[depth-contract]',b'[original-object-draw]',b'[mp3-scan]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E023 depth proof, original Draw and one-pass scan required; no logo fixture')
  if a.experiment=='E024' and (any(m not in data for m in [b'[input-sample]',b'[original-frame]',b'[depth-proof-reuse]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E024 actual input + original frame loop required, no repeated logo fixture')
  if a.experiment=='E025' and (any(m not in data for m in [b'[audio-native-open]',b'[audio-output]',b'[input-sample]',b'[original-frame-error]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E025 actual native sink, real input/frame/error paths required')
  if a.experiment=='E026' and (any(m not in data for m in [b'[color-clear-contract]',b'[original-room-load]',b'[audio-native-open]',b'[input-sample]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E026 real active clear, room entry, audio/input required')
  if a.experiment=='E027' and (any(m not in data for m in [b'[atlas-pools]',b'[atlas-upload]',b'[frame-window]',b'[original-room-load]',b'[color-clear-proof-reuse]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E027 actual bounded residency/frame telemetry/room path required')
  if a.experiment=='E028' and (any(m not in data for m in [b'[graphics-outline]',b'[graphics-sprite-clamp]',b'[atlas-pools]',b'[original-room-load]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E028 real original outline/clamped-crop/room paths required')
  if a.experiment=='E029' and (any(m not in data for m in [b'[gml-debug]',b'[graphics-cull]',b'[graphics-pool]',b'[original-room-load]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E029 genuine debug sink and all-room clip/pool metrics required')
  if a.experiment=='E030' and (b'[graphics-per-vertex]' not in data or b'VISUAL_PROBE_COMPLETED' in data):p.error('E030 real per-vertex GXM path required')
  if a.experiment=='E031' and (any(m not in data for m in [b'[graphics-line]',b'[graphics-timing]',b'[graphics-per-vertex]']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E031 genuine line/color and timing paths required')
  if a.experiment=='E032' and (any(m not in data for m in [b'[perf-stage]',b'[perf-policy]',b'[diagnostic-policy]',b'DIAGNOSTIC_WATCHDOG']) or b'VISUAL_PROBE_COMPLETED' in data):p.error('E032 genuine phase profiling and explicit frame watchdog required')
  out.mkdir(parents=True);sdk('vita-make-fself','-s',translate(str(velf)),translate(str(out/'eboot.bin')))
  manifest={'utc_prepared':datetime.now(timezone.utc).isoformat(),'experiment':'E019','title_id':None,'device_execution':'UNTESTED','purpose':'load/verify original EXE, compile real scripts/events, execute startup until actual unavailable dialog','files':{'eboot.bin':{'sha256':sha(out/'eboot.bin'),'bytes':(out/'eboot.bin').stat().st_size}},'elf_sha256':sha(elf),'velf_sha256':sha(velf),'original_exe_sha256':'cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f','data_path':'ux0:data/howaw/HOWaW_FirefightDemov1.exe','logs':'ux0:data/howaw/diagnostics/e019-NNN/run.log','no_original_files_embedded':True,'vpk':None}
  if b'OWNER_POLICY_HIGH' in data:
   manifest.update(dialog_policy='owner selected High/button 3',purpose='original startup through explicitly configured High response; next real service expected Process/set_program_priority')
  if a.experiment=='E020':
   manifest.update(experiment='E020',purpose='preserve original startup stop; draw original engine-loaded sprite through Game.renderer/libvita2d; log GPU readback, atlas memory and wait-inclusive frame times',logs='ux0:data/howaw/diagnostics/e020-NNN/run.log')
  if a.experiment=='E021':
   manifest.update(experiment='E021',purpose='original startup through explicit unsupported priority effect and real persistent file/INI services; next measured PC gate Audio/sound_replace; no repeated logo fixture',logs='ux0:data/howaw/diagnostics/e021-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E022':
   manifest.update(experiment='E022',purpose='real original MP3 decode/registration in unchanged VM startup; automatic original Draw entry, next native depth-clear gate; audio output unavailable',logs='ux0:data/howaw/diagnostics/e022-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E023':
   manifest.update(experiment='E023',purpose='offscreen real GXM depth/color/occlusion contract, faithful original 2D clear guard, original object Draw until next actual service; single validated MP3 scan; no manual menu',logs='ux0:data/howaw/diagnostics/e023-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E024':
   manifest.update(experiment='E024',purpose='real Vita controller/touch mapping and original Step/Draw/frame loop until next actual service or bounded session end; no fabricated input/audio',logs='ux0:data/howaw/diagnostics/e024-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E025':
   manifest.update(experiment='E025',purpose='existing mixer/MP3/WAV and actual SceAudioOut output; original frames and real input; buffered routine diagnostics with durable checkpoints',logs='ux0:data/howaw/diagnostics/e025-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E026':
   manifest.update(experiment='E026',purpose='real in-scene color/depth contract, original room transition, full physical display/touch policy and camera translation; existing music/input/frame flow',logs='ux0:data/howaw/diagnostics/e026-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E027':
   manifest.update(experiment='E027',purpose='actual fifth-atlas request uses bounded GPU-mapped main RAM, CDRAM64MiB/main32MiB; real original level/customization paths and frame-window metrics; no repeated clear fixture',logs='ux0:data/howaw/diagnostics/e027-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E028':
   manifest.update(experiment='E028',purpose='original customization closed rectangle outline and room per-sprite edge-clamped crops; existing real audio/input and bounded memory; first completed arena frame still unverified',logs='ux0:data/howaw/diagnostics/e028-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E029':
   manifest.update(experiment='E029',purpose='real persistent GML debug output, conservative all-room viewport rejection and measured1MiB temporary vertex pool; preserve original events and bounded atlas residency',logs='ux0:data/howaw/diagnostics/e029-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E030':
   manifest.update(experiment='E030',purpose='original per-vertex textured color after arena countdown, cached native GXM programs and existing renderer/VM',logs='ux0:data/howaw/diagnostics/e030-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E031':
   manifest.update(experiment='E031',purpose='original line/width/gradient family and circles, separated GPU completion/display queue timings; same original VM/atlas/audio/input',logs='ux0:data/howaw/diagnostics/e031-NNN/run.log',profile='ux0:data/howaw/e021-profile')
  if a.experiment=='E032':
   manifest.update(experiment='E032',purpose='original sustained frame execution with explicit per-frame instruction guard, exclusive subsystem windows and one-binary baseline/optimized renderer comparison; no game changes',logs='ux0:data/howaw/diagnostics/e032-NNN/run.log',profile='ux0:data/howaw/e021-profile',baseline_flag='ux0:data/howaw/e032-baseline.flag',default_mode='optimized')
  (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
  print('Prepared real VM SELF + manifest; no TITLE_ID, SFO or VPK generated.');return
 manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
 if manifest['experiment']!=a.experiment or sha(out/'eboot.bin')!=manifest['files']['eboot.bin']['sha256']:p.error('prepared SELF identity mismatch')
 sfo=out/'sce_sys/param.sfo';vpk=out/(a.experiment.lower()+'-private-diagnostic.vpk')
 if sfo.exists() or vpk.exists():p.error('preserve previous packaging; use a new prepared output')
 sfo.parent.mkdir(exist_ok=True)
 sdk('vita-mksfoex','-s','TITLE_ID='+a.title_id,'-s','APP_VER='+a.app_version,'HOWaW original VM diagnostic',translate(str(sfo)))
 with zipfile.ZipFile(vpk,'x',compression=zipfile.ZIP_DEFLATED) as archive:
  for name in ['eboot.bin','sce_sys/param.sfo']:archive.write(out/name,name)
 with zipfile.ZipFile(vpk) as archive:
  if archive.namelist()!=['eboot.bin','sce_sys/param.sfo'] or archive.testzip() is not None:raise RuntimeError('VPK validation failed')
 package={'utc':datetime.now(timezone.utc).isoformat(),'owner_title_id':a.title_id,'vpk_sha256':sha(vpk),'self_sha256':sha(out/'eboot.bin'),'device_execution':'UNTESTED','original_files_embedded':False}
 (out/'package.json').write_text(json.dumps(package,indent=2),encoding='utf-8')
 print('Private diagnostic VPK created; install/boot/VM execution still UNTESTED.')
if __name__=='__main__':main()
