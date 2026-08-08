#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
def chunks(text,limit):
    units=re.findall(r".*?(?:\n\s*\n|\Z)",text,flags=re.S)
    units=[u for u in units if u]
    out=[]; cur=""
    for u in units:
        if cur and len(cur)+len(u)>limit:
            out.append(cur); cur=u
        else: cur+=u
    if cur: out.append(cur)
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("path"); p.add_argument("--out-dir",required=True); p.add_argument("--limit",type=int,default=6000); a=p.parse_args(); text=Path(a.path).read_text(encoding="utf-8"); od=Path(a.out_dir); od.mkdir(parents=True,exist_ok=True); cs=chunks(text,a.limit); files=[]
    for i,c in enumerate(cs,1):
        f=od/f"chunk_{i:03d}.txt"; f.write_text(c,encoding="utf-8"); files.append(f.name)
    (od/"manifest.json").write_text(json.dumps({"source":str(Path(a.path)),"chunks":files,"original_length":len(text)},ensure_ascii=False,indent=2),encoding="utf-8"); print(len(files))
if __name__=="__main__": main()
