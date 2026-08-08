# Install in Codex

OpenAI Skills follow the Agent Skills standard, so the same Skill package can be used in Codex. Personal Skills must be added separately from ChatGPT Web.

## Preferred installation

1. Open a Codex session that exposes Skill installation.
2. Use the built-in Skill installer or Skills interface.
3. Point it at the repository Skill directory:

```text
https://github.com/seokbeomkong/portable-agent-skills/tree/main/skills/ui-ux-pro-max
```

4. Restart or open a new session if your Codex surface requires Skill discovery at session start.

Some Codex surfaces expose a `$skill-installer` command. In those environments, use:

```text
$skill-installer install https://github.com/seokbeomkong/portable-agent-skills/tree/main/skills/ui-ux-pro-max
```

Do not hardcode a local discovery directory across every Codex product. Use the installer or Skills UI documented by the specific Codex surface because local discovery behavior can differ by app, extension, and version.

## Smoke test

Open a repository containing a frontend project and ask:

> Review the current interface with UI UX Pro Max, detect the framework, propose a design system, implement the highest-impact accessibility and responsive fixes, then run the relevant project checks.

Codex should use the shared design workflow and additionally inspect files, detect the stack, modify code, and run verification commands.
