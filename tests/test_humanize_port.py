from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "humanize-korean"
SCRIPTS = SKILL / "scripts"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


class HumanizePortTests(unittest.TestCase):
    def test_upstream_metrics_run_from_an_arbitrary_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            run_dir.mkdir()
            (run_dir / "01_input.txt").write_text(
                "이 보고서는 2026년 매출 10억원을 검토한다.", encoding="utf-8"
            )
            result = run_script(
                "prepare_monolith_input.py",
                "--run-dir",
                str(run_dir),
                "--genre",
                "report",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            metrics = json.loads((run_dir / "00_metrics.json").read_text(encoding="utf-8"))
            self.assertIn(metrics["route_hint"], {"light", "standard", "heavy"})
            self.assertTrue((run_dir / "01_input_with_metrics.txt").is_file())

    def test_upstream_four_axis_gate_executes_from_packaged_paths(self) -> None:
        text = "이 문서는 2026년 매출 10억원을 사실대로 기록한다."
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            before = base / "before.md"
            after = base / "after.md"
            before.write_text(text, encoding="utf-8")
            after.write_text(text, encoding="utf-8")
            result = run_script(
                "verify_gates.py",
                "--before",
                str(before),
                "--after",
                str(after),
                "--genre",
                "report",
                "--json",
            )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn('"exit_code": 0', result.stdout)

    def test_upstream_chunk_workflow_round_trips_on_windows(self) -> None:
        text = "## 제목\n\n" + ("첫 문단은 의미를 보존한다. " * 300) + "\n\n[^1]: 각주 원문\n"
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            (run_dir / "01_input.txt").write_text(text, encoding="utf-8")
            prepared = run_script(
                "prepare_monolith_input.py", "--run-dir", str(run_dir), "--chunk"
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            manifest = json.loads(
                (run_dir / "chunk_manifest.json").read_text(encoding="utf-8")
            )
            for chunk in manifest["chunks"]:
                if not chunk["passthrough"]:
                    original = text[chunk["start"] : chunk["end"]]
                    (run_dir / chunk["rewritten_file"]).write_text(
                        original, encoding="utf-8"
                    )
            assembled = run_script(
                "reassemble_chunks.py", "--run-dir", str(run_dir), "--strict"
            )
            self.assertEqual(assembled.returncode, 0, assembled.stderr)
            self.assertEqual(
                (run_dir / "03_reassembled.md").read_text(encoding="utf-8"), text
            )

    def test_final_artifact_purpose_wins_over_generic_cleanup_word(self) -> None:
        result = run_script(
            "route_hint.py",
            "--task",
            "자기소개서를 자연스럽게 정리해줘",
            "--json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["route"], "heavy")

    def test_requested_summary_wins_over_source_document_type(self) -> None:
        result = run_script(
            "route_hint.py", "--task", "이 보고서 3줄로 요약해줘", "--json"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["route"], "fast")

    def test_fidelity_gate_rejects_swapped_numeric_claims(self) -> None:
        before = (
            "A 부서 매출은 10억원이고 B 부서 매출은 20억원이다. "
            "이 수치는 2026년 결산 자료이며 나머지 조건은 동일하다."
        )
        after = (
            "A 부서 매출은 20억원이고 B 부서 매출은 10억원이다. "
            "이 수치는 2026년 결산 자료이며 나머지 조건은 동일하다."
        )
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            before_path = base / "before.md"
            after_path = base / "after.md"
            before_path.write_text(before, encoding="utf-8")
            after_path.write_text(after, encoding="utf-8")
            result = run_script(
                "verify_output.py",
                "--before",
                str(before_path),
                "--after",
                str(after_path),
            )
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_fidelity_gate_rejects_inline_code_path_and_heading_changes(self) -> None:
        stable = "검토자는 사실과 조건을 확인한다. " * 12
        before = f"## 실행 절차\n\n`render_page()`를 실행하고 `src/render/page.py`를 보존한다. {stable}"
        after = f"## 최종 절차\n\n`render_screen()`을 실행하고 `lib/view/screen.py`를 보존한다. {stable}"
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            before_path = base / "before.md"
            after_path = base / "after.md"
            before_path.write_text(before, encoding="utf-8")
            after_path.write_text(after, encoding="utf-8")
            result = run_script(
                "verify_output.py",
                "--before",
                str(before_path),
                "--after",
                str(after_path),
            )
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_fidelity_gate_rejects_mixed_quote_style_reordering(self) -> None:
        stable = "검토자는 나머지 조건을 그대로 확인한다. " * 20
        before = f'관계자는 "Alpha"라고 했고 이후 ‘Beta’라고 덧붙였다. {stable}'
        after = f'관계자는 ‘Beta’라고 했고 이후 "Alpha"라고 덧붙였다. {stable}'
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            before_path = base / "before.md"
            after_path = base / "after.md"
            before_path.write_text(before, encoding="utf-8")
            after_path.write_text(after, encoding="utf-8")
            result = run_script(
                "verify_output.py",
                "--before",
                str(before_path),
                "--after",
                str(after_path),
            )
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_reassembly_rejects_missing_rewritten_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            chunk = base / "chunk_001.txt"
            chunk.write_text("원문 청크", encoding="utf-8")
            manifest = {
                "source_sha256": hashlib.sha256("원문 청크".encode("utf-8")).hexdigest(),
                "chunks": [
                    {
                        "source_file": chunk.name,
                        "rewritten_file": "chunk_001.rewritten.txt",
                        "passthrough": False,
                    }
                ],
            }
            manifest_path = base / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            result = run_script(
                "reassemble_chunks.py",
                "--manifest",
                str(manifest_path),
                "--chunks-dir",
                str(base),
                "--output",
                str(base / "result.md"),
            )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("missing rewritten chunk", result.stderr.lower())

    def test_full_upstream_core_is_bundled(self) -> None:
        required = [
            "references/ai-tell-taxonomy.md",
            "references/baseline.json",
            "references/baseline_v2.json",
            "references/metrics.py",
            "references/metrics_v2.py",
            "references/scholarship.md",
            "scripts/prepare_monolith_input.py",
            "scripts/verify_change_rate.py",
            "scripts/verify_gates.py",
        ]
        missing = [path for path in required if not (SKILL / path).is_file()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
