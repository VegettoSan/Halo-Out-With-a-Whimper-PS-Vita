#!/usr/bin/env python3
"""Summarize private collision measurements; never subtract calibration from frames."""
import argparse,json,re,statistics
from pathlib import Path

def numbers(s):return {k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',s)}
def analyze(path):
    rows=[];calibration=[];benches={};context={};reference=None
    for line in path.read_text(encoding='utf-8').splitlines():
        if '[collision-policy]' in line:reference=re.search(r'reference=(true|false)',line)[1]=='true'
        if '[collision-window]' in line:context=numbers(line)
        if '[collision-method]' in line:
            r=numbers(line);r.update(context);r['kind']=re.search(r'kind=(\w+)',line)[1];r['stage']=re.search(r'stage=(\S+)',line)[1]
            r['early_rejection_rate']=r['early_reject']/r['calls'] if r['calls'] else None;r['stale_query_rate']=r['stale_queries']/r['calls'] if r['calls'] else None
            r['sampled_inclusive_mean_ns']=r['sampled_inclusive_ns']/r['samples'] if r['samples'] else None;rows.append(r)
        if '[collision-calibration]' in line:
            r=numbers(line);n=r['iterations'];r['sampled_minus_empty_ns_per_call']=(r['sampled_ns']-r['empty_ns'])/n
            r['legacy_timed_minus_empty_ns_per_call']=(r['legacy_timed_ns']-r['empty_ns'])/n
            if 'combined_nested_ns' in r:r['added_detail_ns_per_nested_call']=(r['combined_nested_ns']-r['legacy_nested_ns'])/n
            calibration.append(r)
        if 'DETAIL_BENCH label=' in line:
            r=numbers(line);label=re.search(r'label=(\w+)',line)[1];r['reduction_percent']=100*(1-r['after_us']/r['before_us']);benches.setdefault(label,[]).append(r)
    summary={k:{'rounds':len(v),'calls_per_round':v[0]['calls'],'before_median_us':statistics.median(r['before_us'] for r in v),'after_median_us':statistics.median(r['after_us'] for r in v),'paired_reduction_median_percent':statistics.median(r['reduction_percent'] for r in v),'paired_reduction_range_percent':[min(r['reduction_percent'] for r in v),max(r['reduction_percent'] for r in v)]} for k,v in benches.items()}
    return {'collision_reference_mode':reference,'methods':rows,'calibration':calibration,'benchmarks':summary,'methodology':'Generated CPU scenarios are not native Firefight frequency. Per-method sampled wall times are inclusive and overlap for nested calls; never sum or claim CPU cycles. Sampling uses first call plus hashed~1/128. Native windows follow global60-frame checkpoints, may include scene handling outside Game::frame, and are not necessarily aligned with per-room perf windows; skip startup/transition intervals. Calibration loop differences include noise/scheduling; not subtracted from frame metrics. Benchmark percentages are medians of paired trial reductions; unpaired median ratio can mislead. Negative reduction is a regression, not suppressed.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[2]/'reports/local'
    if not all(x.resolve().is_relative_to(root) for x in [a.log,a.output]) or a.output.exists():p.error('read private report; write NEW ignored report')
    r=analyze(a.log)
    with a.output.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2)
    print(json.dumps({'method_rows':len(r['methods']),'calibration_rounds':len(r['calibration']),'benchmark_loads':len(r['benchmarks'])}))
if __name__=='__main__':main()
