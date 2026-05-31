![Remote Agent Onboarding Skill - ECLIPSE -](assets/eclipse-header.png)

# Remote Agent Onboarding Skill - ECLIPSE -

Codex skill for creating, repairing, and verifying a Linux remote-agent workstation with SSH, X11/Xfce, Codex Desktop, Chrome, Browser/IAB, mobile remote-control, and Codex Automations proof surfaces.

The skill is written for operators who need evidence-backed VM readiness rather than package-version-only checks.

## What This Covers

- Ubuntu-style remote agent VM setup and repair
- Codex CLI/Desktop launch and live GUI verification
- Persistent Chrome profile setup and CDP checks
- Browser/IAB socket and log verification
- Mobile remote-control enrollment checks
- Codex Automations local-state, UI, and smoke-run verification
- Proxmox-oriented VM checks where available

## Install

Clone this repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Sunwood-ai-labs/remote-agent-onboarding.git \
  ~/.codex/skills/remote-agent-onboarding
```

Then start a new Codex session and ask for a remote-agent VM setup, repair, or verification task.

## Files

- `SKILL.md` - main Codex skill entrypoint
- `agents/openai.yaml` - UI metadata
- `references/codex-automations.md` - detailed Automations verification and smoke-test procedure

## Safety Notes

This skill intentionally separates proof surfaces. Do not report a VM as ready until the requested surface has been verified directly.

Before publishing logs, screenshots, or copied VM state, remove:

- credentials, passwords, cookies, and browser profile secrets
- real IPs or hostnames if they identify private infrastructure
- account-specific tokens and OAuth artifacts
- VM images, SSH keys, and `.codex` database files

Automation smoke tests modify the local Codex sqlite database and must back up the DB first. Remove smoke jobs after verification so they do not continue running.

## License

MIT. See [LICENSE](LICENSE).
