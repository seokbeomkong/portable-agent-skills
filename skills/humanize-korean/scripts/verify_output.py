#!/usr/bin/env python3
"""Conservative, deterministic fidelity gate for rewritten documents.

This complements the upstream statistical gates. It rejects changes to protected
facts and document syntax that count-only checks can miss, including swapped
numeric claims, headings, inline code, and file paths.
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
INLINE_CODE_RE = re.compile(r"(?<!`)`[^`\n]+`(?!`)")
URL_RE = re.compile(r"https?://[^\s)\]>]+")
PATH_RE = re.compile(
    r"(?<![\w.])(?:[A-Za-z]:[\\/]|\.?\.?[\\/]|[\w.-]+[\\/])"
    r"(?:[\w .@+~-]+[\\/])*[\w .@+~-]+(?:\.[A-Za-z0-9_-]+)?"
)
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}(?:[+.#/_-][A-Z0-9]+)*\b")
HEADING_RE = re.compile(r"(?m)^\s{0,3}#{1,6}\s+.+$")
LIST_MARKER_RE = re.compile(r"(?m)^\s*(?:[-+*]|\d+[.)])\s+")
NUMBER_RE = re.compile(
    r"(?<![A-Za-z가-힣])[-+]?\d[\d,]*(?:\.\d+)?"
    r"(?:\s?(?:%|퍼센트|년|월|일|시|분|초|원|만원|억원|조원|명|개|건|회|배|"
    r"kg|g|mg|km|m|cm|mm|GB|MB|TB|Hz|MHz|GHz))?"
)
QUOTE_PATTERNS = (
    re.compile(r'"[^"\n]+"'),
    re.compile(r"'[^'\n]+'"),
    re.compile(r"“[^”\n]+”"),
    re.compile(r"‘[^’\n]+’"),
)


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def clean(text: str) -> str:
    return SUMMARY_RE.sub("", text).replace("\r\n", "\n").replace("\r", "\n").strip()


def change_rate(before: str, after: str) -> float:
    left = re.sub(r"\s+", " ", clean(before)).strip()
    right = re.sub(r"\s+", " ", clean(after)).strip()
    if not left and not right:
        return 0.0
    if not left or not right:
        return 1.0
    return 1.0 - SequenceMatcher(None, left, right, autojunk=False).ratio()


def matches(pattern: re.Pattern[str], text: str) -> list[str]:
    return pattern.findall(text)


def quoted_segments(text: str) -> list[str]:
    positioned = [
        (match.start(), match.group())
        for pattern in QUOTE_PATTERNS
        for match in pattern.finditer(text)
    ]
    return [value for _, value in sorted(positioned, key=lambda item: item[0])]


def protected_sequences(text: str) -> dict[str, list[str]]:
    text = clean(text)
    text_without_list_markers = LIST_MARKER_RE.sub("", text)
    return {
        "numbers_dates_units": matches(NUMBER_RE, text_without_list_markers),
        "urls": matches(URL_RE, text),
        "code_blocks": matches(CODE_BLOCK_RE, text),
        "inline_code": matches(INLINE_CODE_RE, text),
        "paths": matches(PATH_RE, text),
        "quotes": quoted_segments(text),
        "acronyms": matches(ACRONYM_RE, text),
        "headings": matches(HEADING_RE, text),
        "list_markers": matches(LIST_MARKER_RE, text),
    }


def sequence_diff(before: dict[str, list[str]], after: dict[str, list[str]]) -> dict:
    diff: dict[str, dict] = {}
    for key, left in before.items():
        right = after[key]
        if left == right:
            continue
        missing = Counter(left) - Counter(right)
        added = Counter(right) - Counter(left)
        diff[key] = {
            "before_order": left,
            "after_order": right,
            "missing": dict(sorted(missing.items())),
            "added": dict(sorted(added.items())),
        }
    return diff


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify humanize-korean fidelity")
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
    if not 0 <= args.warn_threshold < args.abort_threshold <= 1:
        print("error: thresholds must satisfy 0 <= warn < abort <= 1", file=sys.stderr)
        return 3

    rate = change_rate(before_text, after_text)
    protected_diff = sequence_diff(
        protected_sequences(before_text), protected_sequences(after_text)
    )
    if protected_diff or rate >= args.abort_threshold:
        status, code = "reject", 2
    elif rate >= args.warn_threshold:
        status, code = "warn", 1
    else:
        status, code = "pass", 0

    report = {
        "status": status,
        "change_rate": round(rate, 6),
        "change_rate_percent": round(rate * 100, 2),
        "protected_literal_diff": protected_diff,
    }
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {status}")
        print(f"change_rate: {rate * 100:.2f}%")
        print("protected_literals: preserved" if not protected_diff else json.dumps(
            protected_diff, ensure_ascii=False, indent=2
        ))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
