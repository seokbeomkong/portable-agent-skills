from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from registry_lib import load_json_yaml, validate_registry  # noqa: E402
from package_skills import package_skill  # noqa: E402


def make_skill(root: Path, skill_id: str = "example") -> dict:
    skill_dir = root / "skills" / skill_id
    (skill_dir / "agents").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_id}\ndescription: Test Skill for registry validation and packaging.\n---\n\n# Test\n",
        encoding="utf-8",
    )
    (skill_dir / "agents" / "openai.yaml").write_text(
        'interface:\n  display_name: "Example"\n  short_description: "Example Skill"\n',
        encoding="utf-8",
    )
    (skill_dir / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (skill_dir / "THIRD_PARTY_NOTICES.md").write_text("# Notice\n", encoding="utf-8")
    return {
        "id": skill_id,
        "display_name": "Example",
        "kind": "port",
        "summary": "Example portable Skill.",
        "path": f"skills/{skill_id}",
        "artifact": f"dist/{skill_id}/skill.zip",
        "port_version": "1.0.0",
        "status": "current",
        "targets": {
            "chatgpt_web": {"supported": True, "level": "native", "notes": "Portable."},
            "codex": {"supported": True, "level": "enhanced", "notes": "Repository-aware."},
        },
        "origin": {
            "provider": "github",
            "repository": "owner/repo",
            "ref": "main",
            "release": "v1.0.0",
            "integrated_commit": "a" * 40,
            "original_skill_path": "SKILL.md",
        },
        "license": {
            "spdx": "MIT",
            "redistribution": True,
            "modification": True,
            "notice": f"skills/{skill_id}/THIRD_PARTY_NOTICES.md",
        },
        "validation": {"command": "python -m unittest", "package_limit_mb": 25},
        "update_policy": {
            "strategy": "review_required",
            "watch_release": True,
            "watch_commit": True,
            "automatic_issue": True,
            "automatic_merge": False,
        },
    }


def make_registry(skill: dict) -> dict:
    return {
        "schema_version": 1,
        "registry_name": "portable-agent-skills",
        "maintainer": "tester",
        "repository": {"owner": "tester", "name": "portable-agent-skills", "default_branch": "main"},
        "skills": [skill],
    }


class RegistryToolTests(unittest.TestCase):
    def test_real_registry_loads_and_validates(self) -> None:
        registry = load_json_yaml(ROOT / "registry.yaml")
        self.assertEqual(registry["registry_name"], "portable-agent-skills")
        self.assertEqual(validate_registry(ROOT, registry), [])

    def test_duplicate_skill_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skill = make_skill(root)
            registry = make_registry(skill)
            registry["skills"].append(copy.deepcopy(skill))
            errors = validate_registry(root, registry)
            self.assertTrue(any("duplicate skill id" in error.lower() for error in errors), errors)

    def test_skill_name_must_match_registry_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skill = make_skill(root)
            skill_md = root / skill["path"] / "SKILL.md"
            skill_md.write_text(skill_md.read_text(encoding="utf-8").replace("name: example", "name: wrong-name"), encoding="utf-8")
            errors = validate_registry(root, make_registry(skill))
            self.assertTrue(any("frontmatter name" in error.lower() for error in errors), errors)

    def test_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skill = make_skill(root)
            target = root / "outside.txt"
            target.write_text("outside", encoding="utf-8")
            (root / skill["path"] / "linked.txt").symlink_to(target)
            errors = validate_registry(root, make_registry(skill))
            self.assertTrue(any("symlink" in error.lower() for error in errors), errors)

    def test_packaging_is_reproducible_and_has_one_skill_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skill = make_skill(root)
            destination = root / "dist" / "example" / "skill.zip"
            first = package_skill(root, skill, destination)
            first_hash = hashlib.sha256(first.read_bytes()).hexdigest()
            second = package_skill(root, skill, destination)
            second_hash = hashlib.sha256(second.read_bytes()).hexdigest()
            self.assertEqual(first_hash, second_hash)
            with zipfile.ZipFile(second) as archive:
                names = archive.namelist()
                self.assertTrue(names)
                self.assertEqual({name.split("/", 1)[0] for name in names}, {"example"})
                self.assertIn("example/SKILL.md", names)


if __name__ == "__main__":
    unittest.main()
