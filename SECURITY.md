# Security Policy

## Reporting

Report security concerns through GitHub private vulnerability reporting if enabled, or open an issue that describes the class of issue without posting secrets.

Do not include:

- passwords, cookies, OAuth tokens, or API keys
- SSH private keys or VM images
- raw browser profile archives
- private LAN topology that should not be public

## Operational Guidance

This skill contains commands that inspect and sometimes modify a Codex user's local state on a VM. Treat these paths as sensitive:

- `~/.codex/`
- `~/.config/Codex/`
- browser profile directories
- VM disks and snapshots

Back up sqlite databases before modifying automation rows. Prefer harmless smoke-test prompts that only write to a disposable local file.
