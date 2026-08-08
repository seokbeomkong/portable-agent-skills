#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
FAST = ["요약", "기사 요약", "요약 기사", "참고용", "정리", "블로그 초안", "메시지", "빠르게", "가볍게", "fast"]
HEAVY = ["업무", "보고서", "자기소개서", "자소서", "이력서", "경력기술서", "제안서", "ppt", "슬라이드", "발표", "과제", "논문", "제출", "최종본", "정밀", "heavy", "임원 보고"]
FORCE_FAST = ["빠르게", "가볍게", "fast", "최소 수정"]
FORCE_HEAVY = ["정밀하게", "heavy", "최종본", "제출용", "중요 문서"]
def classify(task: str) -> tuple[str,str]:
    t=task.lower()
    if any(x.lower() in t for x in FORCE_HEAVY): return "heavy","user-explicit"
    if any(x.lower() in t for x in FORCE_FAST): return "fast","user-explicit"
    if re.search(r"(보고서|ppt|논문|과제).{0,15}(요약|정리)", t) or re.search(r"(요약|정리).{0,15}(해줘|해 줘)", t):
        return "fast","summary-output"
    hs=sum(1 for x in HEAVY if x.lower() in t); fs=sum(1 for x in FAST if x.lower() in t)
    if hs>fs: return "heavy","final-output-purpose"
    if fs>hs: return "fast","reference-output-purpose"
    return "standard","ambiguous-internal"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--task",required=True); p.add_argument("--json",action="store_true")
    a=p.parse_args(); route,reason=classify(a.task); out={"route":route,"reason":reason}
    print(json.dumps(out,ensure_ascii=False) if a.json else f"{route}: {reason}")
if __name__=="__main__": main()
