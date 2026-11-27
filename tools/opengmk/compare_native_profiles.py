#!/usr/bin/env python3
"""Report full native windows; load-matched candidates are not deterministic replays."""
import argparse,json
from pathlib import Path

RENDER=['visible','culled','batches','vertices','gxm_draws','shader_changes','texture_changes','state_requests','state_changes','tint_calls']

def windows(analysis):
    out=[]
    for key,w in analysis['exclusive_windows'].items():
        load=w.get('load',{});r=w.get('render_p50_p95_peak',[])
        if not load or len(r)!=len(RENDER):continue
        out.append({'key':key,'mode':analysis['mode'],'load':load,'stages_p50_p95_peak_us':{name:[s['p50_us'],s['p95_us'],s['peak_us']] for name,s in w['stages'].items()},'render_p50_p95_peak':dict(zip(RENDER,r)),'allocations_p50_p95_peak':w.get('allocations_p50_p95_peak'),'heap_live_max':w.get('render',{}).get('heap_live_max'),'heap_peak':w.get('render',{}).get('heap_peak')})
    return out

def compare(baseline,optimized):
    assert baseline['mode']=='baseline' and optimized['mode']=='optimized','expected actual baseline then optimized policy logs'
    assert not baseline['profile_invalid'] and not optimized['profile_invalid'],'invalid profiler scopes'
    assert baseline.get('installed_identity_match') and optimized.get('installed_identity_match'),'verify installed SELF first'
    assert baseline['installed_self_sha256']==optimized['installed_self_sha256'],'same executable required'
    before=windows(baseline);after=windows(optimized);matches=[]
    for b in before:
        # Full room-local windows, object p50 within10% and executed instruction p50
        # within10%. Report candidates, do not treat live controller input as replay.
        if b['load']['n']!=60:continue
        candidates=[]
        for a in after:
            x=b['load'];y=a['load']
            if y['n']!=60 or x['room']!=y['room']:continue
            ratios=[abs(y[field][0]/max(x[field][0],1)-1) for field in ['instructions']]
            ratios.append(abs(y['objects_p50']/max(x['objects_p50'],1)-1))
            if max(ratios)<=.1:candidates.append((sum(ratios),a))
        if candidates:
            score,a=min(candidates,key=lambda pair:pair[0]);x=b['load']['total_us'];y=a['load']['total_us']
            matches.append({'before':b['key'],'after':a['key'],'relative_load_difference_sum':score,'before_total_p50_p95_peak_us':x,'after_total_p50_p95_peak_us':y,'p50_change_percent':round(100*(y[0]/max(x[0],1)-1),2)})
    return {'baseline_termination':baseline['termination'],'optimized_termination':optimized['termination'],'baseline_windows':before,'optimized_windows':after,'load_matched_candidates':matches,'methodology':'Each window retains its measured quantiles; quantiles are never averaged or recomputed from window summaries. Candidate windows share room,60 samples and object/instruction p50 within10%; live input, enemy state, visibility and draw workload still differ. Candidates may reuse a window and are descriptive only, not independent samples or controlled causal speedup. Inspect render counts and high-load peaks before conclusions; limiter is excluded.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('baseline',type=Path);p.add_argument('optimized',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();private=Path(__file__).resolve().parents[2]/'reports/local'
    for path in [a.baseline,a.optimized,a.output]:
        if not path.resolve().is_relative_to(private):p.error('use ignored reports/local paths')
    if a.output.exists():p.error('preserve previous results; use NEW output')
    result=compare(json.loads(a.baseline.read_text(encoding='utf-8')),json.loads(a.optimized.read_text(encoding='utf-8')))
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({'baseline_windows':len(result['baseline_windows']),'optimized_windows':len(result['optimized_windows']),'descriptive_load_matched_candidates':len(result['load_matched_candidates']),'baseline_termination':result['baseline_termination'],'optimized_termination':result['optimized_termination']},indent=2))
if __name__=='__main__':main()
