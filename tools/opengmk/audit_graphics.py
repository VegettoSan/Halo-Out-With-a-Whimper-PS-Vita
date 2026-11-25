#!/usr/bin/env python3
"""Bounded static graphics-call inventory. Never prints or copies recovered GML."""
import argparse,collections,hashlib,json,re
from pathlib import Path
from datetime import datetime,timezone

def without_comments_strings(s):
    # GM8 quoted literals have no C-style backslash escaping.
    return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"[^"]*"|\x27[^\x27]*\x27',' ',s)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--code',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    if not a.code.resolve().is_relative_to(root/'recovered') or not a.report.resolve().is_relative_to(root/'reports/local'):
        p.error('read ignored recovered code; write a NEW reports/local report')
    data=a.code.read_bytes();s=without_comments_strings(data.decode('utf-8'))
    calls=collections.Counter(re.findall(r'\b((?:draw_|sprite_|background_|surface_|texture_|d3d_|screen_|display_|window_)[A-Za-z0-9_]*)\s*\(',s))
    render=(a.source/'gm8emulator/src/render.rs').read_text(encoding='utf-8')
    trait=render.split('pub trait RendererTrait {',1)[1].split('pub struct RendererOptions',1)[0]
    out={'utc':datetime.now(timezone.utc).isoformat(),'input_sha256':hashlib.sha256(data).hexdigest(),
        'static_call_sites':dict(sorted(calls.items())),
        'renderer_trait_methods':re.findall(r'\bfn\s+(\w+)\(',trait),
        'limits':'Lexical call sites, not execution coverage. Engine default draws, DnD opcodes, indirect script execution and runtime values require separate evidence. No absent function is declared impossible.'}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    with a.report.open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
    print(f'Static audit: {sum(calls.values())} graphics-related call sites, {len(calls)} functions; {len(out["renderer_trait_methods"])} trait methods; private report written')
if __name__=='__main__':main()
