# Portable Agent Skills

A transparent, public registry of Agent Skills used by `seokbeomkong`, adapted and maintained for **ChatGPT Web + Codex**.

This repository is not a claim of original authorship over ported Skills. Every entry exposes its upstream source, license, integrated revision, compatibility level, adaptation notes, validation command, and update policy.

## Skills

<!-- REGISTRY:START -->
| Skill | Kind | Upstream | ChatGPT Web | Codex | Port version | Integrated upstream | Status |
|---|---|---|---|---|---:|---|---|
| [UI UX Pro Max](skills/ui-ux-pro-max) | `port` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | ✅ Native | ✅ Enhanced | `1.0.0` | `v2.14.1` | 🟢 Current |
| [Caveman](skills/caveman) | `port` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | ✅ Native | ✅ Native | `1.0.0` | `14d4f2e` | 🟢 Current |
<!-- REGISTRY:END -->

## Why this registry exists

Many useful Skills begin in a provider-specific repository. Copying them without provenance makes licensing, compatibility, and maintenance unclear. This registry keeps the relationship explicit:

```text
upstream source
      ↓
license and suitability review
      ↓
portable ChatGPT Web core
      +
conditional Codex enhancements
      ↓
validation and deterministic package
      ↓
tracked upstream maintenance
```

## Install a Skill

Each release contains an individual ZIP for every redistributable Skill. A Skill archive contains exactly one top-level Skill directory.

### ChatGPT Web

1. Download the Skill ZIP from the latest GitHub Release.
2. In ChatGPT, open **Plugins → Skills**.
3. Select **Create → Upload from computer** and upload the ZIP.
4. Start a new conversation and request a matching task.

See [ChatGPT installation](docs/installation-chatgpt.md).

### Codex

Use the same Agent Skills package. Install it through the Skill installer or Skills UI exposed by your Codex surface. When a Codex session supports the built-in installer, point it at the Skill directory URL in this repository.

See [Codex installation](docs/installation-codex.md).

## Verify locally

```bash
python -m unittest discover -s tests -v
python scripts/validate_registry.py
python scripts/generate_catalog.py --check
python scripts/package_skills.py --check
python skills/ui-ux-pro-max/scripts/check_port.py
python skills/caveman/scripts/check_port.py
```

The tooling uses only the Python standard library.

## Upstream maintenance

A scheduled GitHub Action checks registered upstream releases and branch commits every Monday at **09:15 Asia/Seoul**. It creates or updates one deduplicated `upstream-update` Issue per Skill. No upstream code is executed and no port is modified or merged automatically.

See [Upstream maintenance](docs/upstream-policy.md).

## Registry policies

- [Compatibility policy](docs/compatibility-policy.md)
- [Adaptation policy](docs/adaptation-policy.md)
- [License policy](docs/license-policy.md)
- [Adding a Skill](docs/adding-a-skill.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## License

Registry-authored tooling and documentation are MIT licensed. Ported Skill content remains subject to the license and notices in its own directory. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
