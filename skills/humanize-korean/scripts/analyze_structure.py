#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,statistics
from pathlib import Path
SENT=re.compile(r"[^.!?\n]+[.!?]?",re.M)
def analyze(text):
    s=[x.strip() for x in SENT.findall(text) if x.strip()]
    lens=[len(re.sub(r"\s+","",x)) for x in s]
    paras=[p for p in re.split(r"\n\s*\n",text) if p.strip()]
    starts=re.findall(r"(?m)^\s*(또한|따라서|즉|나아가|아울러|게다가|하지만|그러나)\b",text)
    antithesis=len(re.findall(r"(?:아니라|인가.{0,30}인가)",text))
    bullets=len(re.findall(r"(?m)^\s*[-*+]\s+",text))
    return {"chars":len(text),"sentences":len(s),"paragraphs":len(paras),"sentence_mean":round(statistics.mean(lens),2) if lens else 0,"sentence_stdev":round(statistics.pstdev(lens),2) if len(lens)>1 else 0,"long_sentences_100plus":sum(1 for n in lens if n>=100),"leading_connectives":len(starts),"antithesis_signals":antithesis,"bullets":bullets}
def main():
    p=argparse.ArgumentParser(); p.add_argument("path"); p.add_argument("--json",action="store_true"); a=p.parse_args(); text=Path(a.path).read_text(encoding="utf-8"); r=analyze(text); print(json.dumps(r,ensure_ascii=False,indent=2) if a.json else "\n".join(f"{k}: {v}" for k,v in r.items()))
if __name__=="__main__": main()
