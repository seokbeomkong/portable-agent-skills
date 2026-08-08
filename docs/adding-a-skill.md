# Adding a Skill

1. Analyze the upstream repository and decide whether the workflow has repeatable value.
2. Pass the license gate in [license-policy.md](license-policy.md).
3. Classify the entry as `native`, `port`, `extended`, or `tracked`.
4. Create `skills/<id>/SKILL.md` and `agents/openai.yaml`.
5. Add only the scripts, references, and assets that materially improve reliability.
6. Add `LICENSE`, `THIRD_PARTY_NOTICES.md`, `CHANGELOG.md`, and `skill.meta.yaml` for ports.
7. Add matching records to `registry.yaml`, `upstream/upstream-lock.json`, and `upstream/upstream-observed.json`.
8. Run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_registry.py
python scripts/generate_catalog.py
python scripts/generate_catalog.py --check
python scripts/package_skills.py --check
```

9. Run the Skill's own test command from its registry entry.
10. Submit a PR containing provenance, compatibility, validation evidence, and the intended update policy.
