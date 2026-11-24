#!/usr/bin/env python3
"""Run the E017 real-data VM probe in a fresh ignored PC directory.

Copies the baseline; does not edit data, supply GML or answer service requests.
Exit 2 is an explicit unavailable service, not a successful game boot.
"""
import argparse,hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
EXE_HASH='cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f'
ZIP_HASH='423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--input-dir',type=Path,required=True);p.add_argument('--run-name',required=True);a=p.parse_args()
 root=Path(__file__).resolve().parents[2]
 if not a.run_name.replace('-','').isalnum():p.error('use a simple unique run-name')
 runtime=a.runtime.resolve();source=a.input_dir.resolve();game=root/'recovered/vm-probe-20261123'/a.run_name;report=root/'reports/local/vm-probe-20261123'/a.run_name
 if game.exists() or report.exists():p.error('run directories must be new')
 if sha(root/'original/HOWaW_FirefightDemov1.zip')!=ZIP_HASH or sha(source/'HOWaW_FirefightDemov1.exe')!=EXE_HASH:p.error('baseline mismatch')
 game.mkdir(parents=True);report.mkdir(parents=True)
 shutil.copyfile(source/'HOWaW_FirefightDemov1.exe',game/'HOWaW_FirefightDemov1.exe')
 if (source/'Music').exists():shutil.copytree(source/'Music',game/'Music')
 env=os.environ.copy();temp=game/'process-temp';temp.mkdir()
 env.update(TEMP=str(temp),TMP=str(temp),RUST_BACKTRACE='1')
 for key in ['APPDATA','LOCALAPPDATA','USERPROFILE']:
  d=temp/key.lower();d.mkdir();env[key]=str(d)
 start=datetime.now(timezone.utc).isoformat()
 with (report/'stdout.txt').open('xb') as out,(report/'stderr.txt').open('xb') as err:
  result=subprocess.run([str(runtime),str(game/'HOWaW_FirefightDemov1.exe')],cwd=game,env=env,stdout=out,stderr=err,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
 summary={'utc_start':start,'utc_end':datetime.now(timezone.utc).isoformat(),'input_sha256':EXE_HASH,'zip_sha256':ZIP_HASH,'runtime_sha256':sha(runtime),'exit_code':result.returncode,'copied_exe_unchanged':sha(game/'HOWaW_FirefightDemov1.exe')==EXE_HASH}
 log=(report/'stderr.txt').read_text(encoding="utf-8");out=(report/'stdout.txt').read_text(encoding="utf-8")
 import re
 match=re.search(r'VM_EXECUTION instructions=(\d+)',out)
 summary['expected_stop_pass']=result.returncode==2 and 'SERVICE_UNAVAILABLE/External' in log and 'external_define' in log and bool(match and int(match[1])>0) and summary['copied_exe_unchanged']
 (report/'result.json').write_text(json.dumps(summary,indent=2), encoding="utf-8");print(json.dumps(summary,indent=2));print((report/'stdout.txt').read_text(encoding="utf-8"));print((report/'stderr.txt').read_text(encoding="utf-8"));raise SystemExit(0 if summary['expected_stop_pass'] else 1)
if __name__=='__main__':main()
