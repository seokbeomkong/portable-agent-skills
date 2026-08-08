from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CHANGELOG.md",
    "skill.meta.yaml",
    "references/quick-rules.md",
    "references/diagnosis-rules.md",
    "references/heavy-finalizer.md",
    "scripts/verify_output.py",
    "scripts/route_hint.py",
    "scripts/analyze_structure.py",
    "scripts/verify_structure.py",
    "scripts/chunk_text.py",
    "scripts/reassemble_chunks.py",
]

missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
if missing:
    raise SystemExit("missing required files: " + ", ".join(missing))

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
assert skill.startswith("---\nname: humanize-korean\n")
assert "요약" in skill and "자기소개서" in skill and "Heavy" in skill and "Fast" in skill

for script in (ROOT / "scripts").glob("*.py"):
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], check=True)

sys.path.insert(0, str(ROOT / "scripts"))
from route_hint import classify  # noqa: E402

cases = [
    ("이 보고서 3줄로 요약해줘", "fast"),
    ("자기소개서 최종본 자연스럽게 다듬어줘", "heavy"),
    ("임원 보고용 PPT 문구로 작성해줘", "heavy"),
    ("기사 요약을 빠르게 자연스럽게", "fast"),
]
for text, expected in cases:
    got, _ = classify(text)
    assert got == expected, (text, got, expected)

print("humanize-korean port: PASS")
