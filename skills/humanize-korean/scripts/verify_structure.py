#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from analyze_structure import analyze
SENT=re.compile(r"[^.!?\n]+[.!?]?",re.M)
def norm(s): return re.sub(r"\s+"," ",s).strip()
def touch(before,after):
    bs=[norm(x) for x in SENT.findall(before) if norm(x)]; aset={norm(x) for x in SENT.findall(after) if norm(x)}
    n=sum(1 for x in bs if x not in aset); return (n/len(bs) if bs else 0,n,len(bs))
def main():
    p=argparse.ArgumentParser(); p.add_argument("--before",required=True); p.add_argument("--after",required=True); p.add_argument("--json",action="store_true"); a=p.parse_args()
    b=Path(a.before).read_text(encoding="utf-8"); c=Path(a.after).read_text(encoding="utf-8"); rb,ra=analyze(b),analyze(c); tr,n,total=touch(b,c)
    annihilation=rb["antithesis_signals"]>=5 and ra["antithesis_signals"]==0
    warn=annihilation or (total >= 5 and tr>=0.75)
    out={"status":"warn" if warn else "pass","sentence_touch_rate":round(tr,4),"touched":n,"total":total,"antithesis_before":rb["antithesis_signals"],"antithesis_after":ra["antithesis_signals"],"antithesis_annihilated":annihilation}
    print(json.dumps(out,ensure_ascii=False,indent=2) if a.json else "\n".join(f"{k}: {v}" for k,v in out.items())); raise SystemExit(1 if warn else 0)
if __name__=="__main__": main()
