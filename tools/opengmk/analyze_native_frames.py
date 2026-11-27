#!/usr/bin/env python3
"""Summarize private native logs without exporting original GML/debug text."""
import argparse,hashlib,json,re,struct
from pathlib import Path
def quant(values):
    values=sorted(values);n=len(values)
    return None if not n else {'n':n,'p50':values[n//2],'p95':values[max(0,(n*95+99)//100-1)],'peak':values[-1]}
def numbers(line):return {k:int(v) for k,v in re.findall(r'([a-zA-Z0-9_]+)=(-?\d+)',line)}
def analyze(path):
    lines=path.read_text(encoding='utf-8').splitlines();samples=[];frame=None;stage='';windows={};mode='legacy';exit_code=None
    for line in lines:
        if '[perf-policy]' in line:mode=re.search(r'mode=(\w+)',line)[1]
        if '[original-frame]' in line:frame=numbers(line)
        if '[graphics-cull]' in line:stage=re.search(r'stage=(\w+)',line)[1]
        if '[graphics-timing]' in line and frame and stage=='native_frames':samples.append(dict(frame,**numbers(line)))
        if '[graphics-memory] stage=native_frames' in line and samples:samples[-1].update(numbers(line))
        if '[heap] stage=native_frames' in line and samples:samples[-1].update(numbers(line))
        if any(tag in line for tag in ['[perf-load]','[perf-stage]','[perf-render]']):
            n=numbers(line);key=f'{n["room"]}:{n["last"]}';w=windows.setdefault(key,{'stages':{}})
            if '[perf-stage]' in line:w['stages'][re.search(r'stage=(\w+)',line)[1]]=n
            elif '[perf-load]' in line:
                w['load']=n
                for name in ['total_us','instructions','collection_us','outside_frame_sync_us']:
                    m=re.search(name+r'=(\[[^\]]*\])',line)
                    if m:w['load'][name]=json.loads(m[1])
            else:
                m=re.search(r'values=(\[\[.*\]\]) allocations=',line)
                if m:w['render_p50_p95_peak']=json.loads(m[1])
        if 'DIAGNOSTIC_END exit_code=' in line:exit_code=numbers(line)['exit_code']
    joined='\n'.join(lines)
    if 'Builtin/instruction_budget' in joined:kind='diagnostic_total_instruction_limit'
    elif 'DIAGNOSTIC_WATCHDOG instruction_limit' in joined:kind='diagnostic_frame_watchdog'
    elif exit_code==0:kind='normal_frame_limit' if '[native-session-end]' in joined else 'normal_engine_completion'
    elif 'SERVICE_UNAVAILABLE/' in joined:kind='unimplemented_service'
    elif 'GXM error=' in joined or 'GRAPHICS_FAIL' in joined:kind='graphics_error'
    elif 'ALLOCATION_FAILED' in joined:kind='allocation_failure'
    elif 'AUDIO_FAIL' in joined or 'AUDIO_PCM_FAIL' in joined:kind='audio_error'
    elif 'PANIC_STOP' in joined:kind='panic_other'
    elif exit_code is not None:kind='engine_error'
    else:kind='incomplete_log_uncertain'
    summaries={}
    for room in sorted({s['room'] for s in samples}):
        rows=[s for s in samples if s['room']==room and s['completed']>120]
        summaries[str(room)]={k:quant([s[k] for s in rows]) for k in ['cpu_gpu_wait_us','end_gpu_wait_us','swap_queue_wait_us']}
        summaries[str(room)]['main_thread_residual_us']=quant([s['cpu_gpu_wait_us']-s['end_gpu_wait_us']-s['swap_queue_wait_us'] for s in rows])
    return {'log_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':mode,'exit_code':exit_code,'termination':kind,'last_completed_checkpoint':max((s['completed'] for s in samples),default=None),'profile_invalid':sum('PROFILE_INVALID' in l for l in lines),'sparse_checkpoint_summary':summaries,'checkpoint_rows':samples,'exclusive_windows':windows,'methodology':'Sparse checkpoint quantiles are not full-window quantiles. Exclusive stage times are instrumented main-thread wall time, not CPU cycles. Native waits include driver work; no GPU-only or displayed-FPS claim. Audio-window quantiles are separate asynchronous 1ms-bin upper bounds.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--installed-self',type=Path);p.add_argument('--sfo',type=Path);p.add_argument('--package',type=Path);p.add_argument('--version');a=p.parse_args();root=Path(__file__).resolve().parents[2]
    if not a.log.resolve().is_relative_to(root/'reports/local') or not a.output.resolve().is_relative_to(root/'reports/local') or a.output.exists():p.error('read ignored local report; write NEW ignored local report')
    result=analyze(a.log)
    if a.installed_self:
        result['installed_self_sha256']=hashlib.sha256(a.installed_self.read_bytes()).hexdigest()
        if a.package:
            pkg=json.loads(a.package.read_text(encoding='utf-8'));result['installed_identity_match']=result['installed_self_sha256']==pkg['self_sha256'];assert result['installed_identity_match'],'installed SELF mismatch'
    if a.sfo:
        b=a.sfo.read_bytes();magic,_,keys,values,n=struct.unpack_from('<5I',b);assert magic==0x46535000 and n<1024;info={}
        for i in range(n):
            k,fmt,l,_,o=struct.unpack_from('<HHIII',b,20+16*i)
            if fmt==0x204:info[b[keys+k:].split(b'\0',1)[0].decode()]=b[values+o:values+o+l].rstrip(b'\0').decode('utf-8')
        result['title_id']=info['TITLE_ID'];result['app_version']=info['APP_VER'];assert info['TITLE_ID']=='HOWAW1178'
        if a.version:assert info['APP_VER']==a.version
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:result.get(k) for k in ['termination','exit_code','last_completed_checkpoint','mode','title_id','app_version','installed_identity_match','profile_invalid','sparse_checkpoint_summary']},indent=2))
if __name__=='__main__':main()
