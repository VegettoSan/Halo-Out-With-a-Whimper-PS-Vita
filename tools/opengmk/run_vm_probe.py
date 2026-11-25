#!/usr/bin/env python3
"""Run the E017 real-data VM probe in a fresh ignored PC directory.

Copies the baseline; does not edit data, supply GML or answer service requests.
Exit 2 is an explicit unavailable service, not a successful game boot.
"""
import argparse,hashlib,json,os,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
EXE_HASH='cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f'
ZIP_HASH='423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def assess(log,out,interactive,service,operation):
 stop=re.search(r'STARTUP_STOP (\w+): SERVICE_UNAVAILABLE/(\w+)',log)
 response=re.search(r'\[dialog-response\] result=([0-3]) instructions_before=(\d+) instructions_after=(\d+) pending_ms=(\d+)',log)
 instructions=re.search(r'VM_EXECUTION instructions=(\d+)',out+'\n'+log)
 expected=bool(stop) and (bool(response and response[2]==response[3]) if interactive else stop[2]==service and stop[1]==operation)
 return {'expected_stop':expected and bool(instructions and int(instructions[1])>0),
         'observed_service':stop[2] if stop else None,'observed_operation':stop[1] if stop else None,
         'instructions':int(instructions[1]) if instructions else 0,
         'human_response':int(response[1]) if response else None,
         'dialog_vm_paused':response[2]==response[3] if response else None}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--input-dir',type=Path,required=True);p.add_argument('--run-name',required=True)
 p.add_argument('--experiment',default='vm-probe-20261123');p.add_argument('--expected-service',default='External');p.add_argument('--expected-operation',default='external_define');p.add_argument('--interactive-dialog',action='store_true');p.add_argument('--require-persistent',action='store_true');p.add_argument('--owner-dialog-high',action='store_true');p.add_argument('--diagnostic-prefix',choices=['e019','e020','e021','e022'],default='e019');p.add_argument('--native-priority-contract',action='store_true');p.add_argument('--files-contract',action='store_true');a=p.parse_args()
 if a.interactive_dialog and a.owner_dialog_high:p.error('human interaction and owner default policy are separate modes')
 root=Path(__file__).resolve().parents[2]
 if not a.run_name.replace('-','').isalnum() or not a.experiment.replace('-','').isalnum():p.error('use a simple unique run-name')
 runtime=a.runtime.resolve();source=a.input_dir.resolve();game=root/'recovered'/a.experiment/a.run_name;report=root/'reports/local'/a.experiment/a.run_name
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
  command=[str(runtime),str(game/'HOWaW_FirefightDemov1.exe')]+(['--interactive-dialog'] if a.interactive_dialog else [])+(['--owner-dialog-high'] if a.owner_dialog_high else [])
  if a.native_priority_contract:command.append('--native-priority-contract')
  if a.files_contract:command.append('--files-contract')
  result=subprocess.Popen(command,cwd=game,env=env,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
  (report/'process.json').write_text(json.dumps({'pid':result.pid,'utc_start':start,'command':command},indent=2),encoding='utf-8')
  print(f'VM probe PID {result.pid}; human-dialog={a.interactive_dialog}; evidence {a.experiment}/{a.run_name}',flush=True)
  result.wait(timeout=None if a.interactive_dialog else 60)
 summary={'utc_start':start,'utc_end':datetime.now(timezone.utc).isoformat(),'input_sha256':EXE_HASH,'zip_sha256':ZIP_HASH,'runtime_sha256':sha(runtime),'exit_code':result.returncode,'copied_exe_unchanged':sha(game/'HOWaW_FirefightDemov1.exe')==EXE_HASH}
 log=(report/'stderr.txt').read_text(encoding="utf-8");out=(report/'stdout.txt').read_text(encoding="utf-8")
 assessment=assess(log,out,a.interactive_dialog,a.expected_service,a.expected_operation)
 summary.update(assessment)
 summary['expected_stop_pass']=result.returncode==2 and assessment['expected_stop'] and summary['copied_exe_unchanged']
 summary['expected_service']=None if a.interactive_dialog else a.expected_service;summary['human_dialog']=a.interactive_dialog
 if a.owner_dialog_high:
  summary['owner_dialog_policy_pass']='[dialog-policy-response] OWNER_POLICY_HIGH result=3' in log and '[dialog-response]' not in log
  summary['expected_stop_pass']=summary['expected_stop_pass'] and summary['owner_dialog_policy_pass']
 if a.native_priority_contract:
  summary['native_priority_contract_pass']='[priority-unavailable]' in log and 'process=Unavailable thread=Unavailable' in log and '[priority-readback]' not in log
  summary['expected_stop_pass']=summary['expected_stop_pass'] and summary['native_priority_contract_pass']
 if a.files_contract:
  summary['files_contract_pass']=bool(re.search(r'FILES_CONTRACT_PASS .* VM instructions unchanged='+str(summary['instructions'])+r'\b',log))
  summary['expected_stop_pass']=summary['expected_stop_pass'] and summary['files_contract_pass']
 if a.require_persistent:
  logs=list((game/'diagnostics').glob(a.diagnostic_prefix+'-*/run.log'))
  saved=logs[0].read_text(encoding='utf-8') if len(logs)==1 else ''
  persisted=assess(saved,'',a.interactive_dialog,a.expected_service,a.expected_operation)
  summary['persistent_pass']=persisted==assessment and '[data-verify]' in saved and 'pass=true' in saved and 'PREPARED scripts=' in saved and 'DIAGNOSTIC_END exit_code=2' in saved
  summary['expected_stop_pass']=summary['expected_stop_pass'] and summary['persistent_pass']
 (report/'result.json').write_text(json.dumps(summary,indent=2), encoding="utf-8");print(json.dumps(summary,indent=2));print((report/'stdout.txt').read_text(encoding="utf-8"));print((report/'stderr.txt').read_text(encoding="utf-8"));raise SystemExit(0 if summary['expected_stop_pass'] else 1)
if __name__=='__main__':main()
