# Contributing

Keep this repository focused on reusable remote-agent onboarding workflows.

## Guidelines

- Keep `SKILL.md` concise and move long procedures into `references/`.
- Do not commit real credentials, VM images, browser profiles, `.codex` databases, or private screenshots.
- Prefer variables such as `<vmid>`, `<vm_ip>`, and `codex-ubuntu` over personal infrastructure names.
- Preserve proof-surface separation: SSH, GUI, Codex Desktop, Chrome, Browser/IAB, mobile, and Automations should be verified independently.
- For commands that modify state, include backup and cleanup steps.

## Validation

Before opening a PR, run:

```bash
git diff --check
python3 - <<'PY'
from pathlib import Path
for path in [Path("SKILL.md"), Path("agents/openai.yaml")]:
    text = path.read_text()
    assert text.strip(), path
print("basic file check ok")
PY
rg -n -i "password|secret|token|api.?key|private key|credential|cookie" . -g '!/.git/**' || true
```
