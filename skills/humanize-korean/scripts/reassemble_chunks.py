#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser(); p.add_argument("--manifest",required=True); p.add_argument("--chunks-dir",required=True); p.add_argument("--output",required=True); a=p.parse_args(); m=json.loads(Path(a.manifest).read_text(encoding="utf-8")); d=Path(a.chunks_dir); parts=[]
    for name in m["chunks"]:
        source=d/name; rewritten=d/(Path(name).stem+".rewritten.txt"); parts.append((rewritten if rewritten.exists() else source).read_text(encoding="utf-8"))
    out="".join(parts); Path(a.output).write_text(out,encoding="utf-8"); print(a.output)
if __name__=="__main__": main()
