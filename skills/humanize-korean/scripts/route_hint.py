#!/usr/bin/env python3
"""Choose the Humanize workflow from user intent, without an LLM call."""

from __future__ import annotations

import argparse
import json
import re


FAST = (
    "요약", "기사 요약", "참고용", "메모", "초안", "빠르게", "가볍게", "fast",
)
HEAVY = (
    "업무", "보고서", "자기소개서", "자소서", "이력서", "경력기술서", "제안서",
    "ppt", "슬라이드", "발표", "과제", "논문", "제출", "최종본", "공식", "공문",
)
FORCE_FAST = ("빠르게", "가볍게", "fast", "최소 수정")
FORCE_HEAVY = ("정밀하게", "heavy", "최종본", "제출용", "중요 문서")


def classify(task: str) -> tuple[str, str]:
    text = task.lower()
    if any(token in text for token in FORCE_HEAVY):
        return "heavy", "user-explicit"
    if any(token in text for token in FORCE_FAST):
        return "fast", "user-explicit"

    # The intended artifact outranks generic verbs such as 정리/요약.
    if re.search(r"(ppt|슬라이드|자기소개서|자소서|이력서|경력기술서|제안서|발표|제출용|최종본)", text):
        return "heavy", "final-output-purpose"
    if re.search(r"(보고서|논문|기사|자료).{0,20}(\d+\s*줄\s*)?(요약|요약해|요약본)", text):
        return "fast", "summary-output"
    if any(token in text for token in HEAVY):
        return "heavy", "final-output-purpose"
    if any(token in text for token in FAST):
        return "fast", "reference-output-purpose"
    return "standard", "ambiguous-internal"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    route, reason = classify(args.task)
    result = {"route": route, "reason": reason}
    print(json.dumps(result, ensure_ascii=False) if args.json else f"{route}: {reason}")


if __name__ == "__main__":
    main()
