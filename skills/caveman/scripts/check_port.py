from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "SKILL.md",
    ROOT / "agents" / "openai.yaml",
    ROOT / "LICENSE",
    ROOT / "THIRD_PARTY_NOTICES.md",
    ROOT / "CHANGELOG.md",
    ROOT / "skill.meta.yaml",
]

missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.is_file()]
if missing:
    raise SystemExit(f"missing required files: {', '.join(missing)}")

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
if not skill.startswith("---\nname: caveman\n"):
    raise SystemExit("SKILL.md frontmatter must start with name: caveman")
if "description:" not in skill.split("---", 2)[1]:
    raise SystemExit("SKILL.md frontmatter missing description")

required_terms = ["lite", "full", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra"]
for term in required_terms:
    if term not in skill:
        raise SystemExit(f"SKILL.md missing intensity level: {term}")

for protected in ["numbers", "commands", "citations", "safety"]:
    if not re.search(protected, skill, re.IGNORECASE):
        raise SystemExit(f"SKILL.md missing portability safeguard: {protected}")

openai = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
for term in ["display_name", "short_description", "default_prompt", "allow_implicit_invocation"]:
    if term not in openai:
        raise SystemExit(f"agents/openai.yaml missing: {term}")

license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
if "MIT License" not in license_text or "Julius Brussee" not in license_text:
    raise SystemExit("upstream MIT attribution missing")

print("caveman port validation: OK")
