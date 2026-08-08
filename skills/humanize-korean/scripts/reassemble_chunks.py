#!/usr/bin/env python3
"""Safe chunk reassembly with upstream and legacy portable CLIs.

Preferred usage is the upstream ``--run-dir`` workflow. The manifest/chunks-dir
form remains supported for older releases, but never substitutes an untouched
source chunk for a missing rewrite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def _fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2


def compatibility_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Humanize KR chunk reassembler")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--chunks-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return _fail(f"invalid manifest: {exc}")
    chunks = manifest.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        return _fail("manifest must contain a non-empty chunks list")

    chunks_dir = Path(args.chunks_dir)
    originals: list[str] = []
    pieces: list[str] = []
    for index, entry in enumerate(chunks, start=1):
        if not isinstance(entry, dict):
            return _fail(f"invalid chunk entry {index}")
        source_name = entry.get("source_file")
        if not source_name:
            return _fail(f"chunk {index} has no source_file")
        source_path = chunks_dir / source_name
        try:
            original = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return _fail(f"missing source chunk {source_name}: {exc}")
        originals.append(original)

        if entry.get("passthrough", False):
            pieces.append(original)
            continue
        rewritten_name = entry.get("rewritten_file")
        if not rewritten_name:
            return _fail(f"chunk {index} has no rewritten_file")
        rewritten_path = chunks_dir / rewritten_name
        if not rewritten_path.is_file():
            return _fail(f"missing rewritten chunk: {rewritten_name}")
        try:
            rewritten = rewritten_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return _fail(f"unreadable rewritten chunk {rewritten_name}: {exc}")
        if original.strip() and not rewritten.strip():
            return _fail(f"empty rewritten chunk: {rewritten_name}")
        pieces.append(
            original[: len(original) - len(original.lstrip())]
            + rewritten.strip()
            + original[len(original.rstrip()) :]
        )

    original_text = "".join(originals)
    expected_sha = manifest.get("source_sha256")
    actual_sha = hashlib.sha256(original_text.encode("utf-8")).hexdigest()
    if expected_sha and expected_sha != actual_sha:
        return _fail("source chunks do not match manifest source_sha256")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(pieces), encoding="utf-8")
    print(output)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--run-dir" in args:
        from reassemble_chunks_upstream import main as upstream_main

        return upstream_main(args)
    return compatibility_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
