#!/usr/bin/env python3
"""Deterministic verifier for the standalone humanize-korean skill.

Checks:
- character-level change rate (after whitespace normalization)
- preservation of protected literals: numbers/dates/units, URLs, code blocks,
  direct quotes, and common technical acronyms

Exit codes:
0 pass
1 warning: change rate >= warn threshold and < abort threshold
2 reject: protected literal mismatch or change rate >= abort threshold
3 execution error
"""

from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys
from typing import Iterable

SUMMARY_RE = re.compile(r"<!--\s*HUMANIZE-SUMMARY\b.*?-->", re.DOTALL | re.IGNORECASE)
CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
URL_RE = re.compile(r"https?://[^\s)\]>]+")
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}(?:[+.#/_-][A-Z0-9]+)*\b")
LIST_MARKER_RE = re.compile(r"(?m)^\s*\d+[.)]\s+")
NUMBER_RE = re.compile(
    r"(?<![A-Za-z가-힣])[-+]?\d[\d,]*(?:\.\d+)?"
    r"(?:\s?(?:%|퍼센트|년|월|일|시|분|초|원|만원|억원|조원|명|개|건|회|배|"
    r"kg|g|mg|km|m|cm|mm|GB|MB|TB|Hz|MHz|GHz))?"
)
QUOTE_PATTERNS = [
    re.compile(r'"[^"\n]+"'),
    re.compile(r"“[^”\n]+”"),
    re.compile(r"‘[^’\n]+’"),
    re.compile(r"「[^」\n]+」"),
    re.compile(r"『[^』\n]+』"),
]


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def clean(text: str) -> str:
    text = SUMMARY_RE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def normalize_for_change_rate(text: str) -> str:
    text = clean(text)
    return re.sub(r"\s+", " ", text).strip()


def change_rate(before: str, after: str) -> float:
    a = normalize_for_change_rate(before)
    b = normalize_for_change_rate(after)
    if not a and not b:
        return 0.0
    if not a or not b:
        return 1.0
    return 1.0 - SequenceMatcher(None, a, b, autojunk=False).ratio()


def counted_matches(pattern: re.Pattern[str], text: str) -> Counter[str]:
    return Counter(pattern.findall(text))


def quoted_segments(text: str) -> Counter[str]:
    out: Counter[str] = Counter()
    for pattern in QUOTE_PATTERNS:
        out.update(pattern.findall(text))
    return out


def protected_counts(text: str) -> dict[str, Counter[str]]:
    text = clean(text)
    text_without_list_markers = LIST_MARKER_RE.sub("", text)
    return {
        "numbers_dates_units": counted_matches(NUMBER_RE, text_without_list_markers),
        "urls": counted_matches(URL_RE, text),
        "code_blocks": counted_matches(CODE_BLOCK_RE, text),
        "quotes": quoted_segments(text),
        "acronyms": counted_matches(ACRONYM_RE, text),
    }


def diff_counts(
    before: dict[str, Counter[str]], after: dict[str, Counter[str]]
) -> dict[str, dict[str, dict[str, int]]]:
    diff: dict[str, dict[str, dict[str, int]]] = {}
    for key in before:
        missing = before[key] - after[key]
        added = after[key] - before[key]
        if missing or added:
            diff[key] = {
                "missing": dict(sorted(missing.items())),
                "added": dict(sorted(added.items())),
            }
    return diff


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify humanize-korean output")
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--warn-threshold", type=float, default=0.30)
    parser.add_argument("--abort-threshold", type=float, default=0.50)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        before_text = read_text(args.before)
        after_text = read_text(args.after)
    except (OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    if not (0 <= args.warn_threshold < args.abort_threshold <= 1):
        print("error: thresholds must satisfy 0 <= warn < abort <= 1", file=sys.stderr)
        return 3

    rate = change_rate(before_text, after_text)
    before_protected = protected_counts(before_text)
    after_protected = protected_counts(after_text)
    protected_diff = diff_counts(before_protected, after_protected)

    if protected_diff or rate >= args.abort_threshold:
        status = "reject"
        code = 2
    elif rate >= args.warn_threshold:
        status = "warn"
        code = 1
    else:
        status = "pass"
        code = 0

    report = {
        "status": status,
        "change_rate": round(rate, 6),
        "change_rate_percent": round(rate * 100, 2),
        "warn_threshold_percent": args.warn_threshold * 100,
        "abort_threshold_percent": args.abort_threshold * 100,
        "protected_literal_diff": protected_diff,
    }

    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {status}")
        print(f"change_rate: {rate * 100:.2f}%")
        if protected_diff:
            print("protected_literal_diff:")
            for kind, values in protected_diff.items():
                print(f"  {kind}:")
                if values["missing"]:
                    print(f"    missing: {values['missing']}")
                if values["added"]:
                    print(f"    added: {values['added']}")
        else:
            print("protected_literals: preserved")

    return code


if __name__ == "__main__":
    raise SystemExit(main())
