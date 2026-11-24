#!/usr/bin/env python3
"""Run one ABI/OS comparison in a fresh private child after hash verification.

The reviewed 1KiB DLL has no entry point/TLS and only current-process OS calls.
This is a host-process isolation test, not a security VM.
"""
import argparse,hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
HASH='dac23ed1af08cb7409a18dc09b0c35230e1b314ff49711394c66bd69ae86548c'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--probe',type=Path,required=True);p.add_argument('--dll',type=Path,required=True);p.add_argument('--run-name',required=True);a=p.parse_args()
 root=Path(__file__).resolve().parents[2]
 if not a.run_name.replace('-','').isalnum():p.error('simple new run-name required')
 if hashlib.sha256(a.dll.read_bytes()).hexdigest()!=HASH:p.error('unreviewed DLL baseline')
 work=root/'recovered/cleanmem-probe-20261123'/a.run_name;report=root/'reports/local/cleanmem-probe-20261123'/a.run_name
 if work.exists() or report.exists():p.error('output must be new')
 work.mkdir(parents=True);report.mkdir(parents=True);dll=work/'CleanMem.dll';shutil.copyfile(a.dll,dll)
 temp=work/'temp';temp.mkdir();env=os.environ.copy();env.update(TEMP=str(temp),TMP=str(temp))
 started=datetime.now(timezone.utc).isoformat()
 with (report/'stdout.txt').open('xb') as out,(report/'stderr.txt').open('xb') as err:
  child=subprocess.run([str(a.probe.resolve()),str(dll)],cwd=work,env=env,stdout=out,stderr=err,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
 unchanged=hashlib.sha256(dll.read_bytes()).hexdigest()==HASH
 result={'utc_start':started,'utc_end':datetime.now(timezone.utc).isoformat(),'dll_sha256':HASH,'probe_sha256':hashlib.sha256(a.probe.read_bytes()).hexdigest(),'exit_code':child.returncode,'copied_dll_unchanged':unchanged}
 (report/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));print((report/'stdout.txt').read_text(encoding='utf-8'));print((report/'stderr.txt').read_text(encoding='utf-8'))
 raise SystemExit(0 if child.returncode==0 and unchanged else 1)
if __name__=='__main__':main()
