---
name: remote-agent-onboarding
description: Create, onboard, repair, and verify a remote-agent employee VM such as VM101 codex-ubuntu, from VM provisioning through SSH, Linux GUI, Codex Desktop, Chrome, Browser/IAB, and proof-surface checks. Use when the user asks to create a VM for a remote agent employee, prepare an agent workstation, fix VM101/codex-ubuntu, install Chrome, recover Browser plugin access, or document the end-to-end remote agent onboarding workflow.
---

# Remote Agent Onboarding

Use this skill to turn a fresh Linux VM into a working "remote agent employee" workstation. The finish line is not a created VM or an installed package; the finish line is an agent that can log in, show a real GUI, run Codex Desktop, launch Chrome, and expose Browser/IAB proof.

Default reference target:

- VM: `101` when the user says VM101
- SSH alias: `codex-ubuntu`
- User inside VM: `codex`
- OS family: Ubuntu 24.04 LTS
- Desktop app path: `/home/codex/codex-app`
- Launcher: `/home/codex/.local/bin/codex-desktop-launch`
- Repair launcher: `/home/codex/.local/bin/codex-desktop-force-restart`

## Operating Rule

Separate proof surfaces. Do not say the VM is ready from a single package version.

Required proof surfaces:

- Host/VM reachability: SSH to `codex-ubuntu`.
- CLI/app: `codex --version`, app bundle/processes.
- Config: `~/.codex/config.toml` has remote features enabled.
- GUI: X11 `Codex` window is visible through `DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority`.
- Browser binary: Chrome exists and launches on X11.
- Browser plugin/IAB: `/tmp/codex-browser-use/*.sock` is current and logs show IAB ready.

## Quick Triage

Run read-only checks first:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 codex-ubuntu '
hostname; date; whoami
echo DISPLAY=$DISPLAY XDG_SESSION_TYPE=$XDG_SESSION_TYPE
codex --version || true
command -v google-chrome || true
command -v google-chrome-stable || true
command -v chromium || true
command -v firefox || true
pgrep -a "codex-app/electron|codex app-server|webview-server|node_repl|chrome" || true
'
```

Check GUI from SSH by explicitly setting the live X11 environment:

```bash
ssh codex-ubuntu '
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xwininfo -root -tree 2>&1 |
  egrep "Codex|Google Chrome|electron|Chrome" | head -60
'
```

Check config and launchers:

```bash
ssh codex-ubuntu '
sed -n "1,220p" ~/.codex/config.toml 2>/dev/null
sed -n "1,120p" ~/.local/bin/codex-desktop-launch 2>/dev/null
sed -n "1,180p" ~/.local/bin/codex-desktop-force-restart 2>/dev/null
'
```

Expected config values:

```toml
[features]
remote_connections = true
remote_control = true
workspace_dependencies = false
```

The launcher should use `#!/usr/bin/env bash` and execute `/home/codex/codex-app/start.sh`.

## VM Creation Baseline

When asked to create the VM from scratch, adapt to the actual hypervisor, but preserve these invariants:

- VM id/name should map to the requested agent employee. For VM101, use `101` / `codex-ubuntu`.
- Install Ubuntu 24.04 LTS with a graphical X11 desktop, usually XFCE/LightDM.
- Create user `codex` and ensure SSH access from the host via alias `codex-ubuntu`.
- Ensure the `codex` user can run required maintenance commands with noninteractive sudo, or report the password blocker clearly.
- Ensure X11 is available as `DISPLAY=:0` with `~/.Xauthority`.
- Do not call setup complete until SSH, X11, and GUI proof pass.

If the host appears to be Proxmox/giobox, useful checks may include `qm status 101` and `qm guest cmd 101 ping`, but always verify from inside the VM by SSH as well.

## Codex Desktop Install Or Refresh

Use the current local/project-specific installer path if available. A known working path from prior VM101 maintenance was:

```bash
ssh codex-ubuntu '
mkdir -p ~/src
cd ~/src
test -d codex-desktop-linux || git clone https://github.com/ilysenko/codex-desktop-linux.git
cd codex-desktop-linux
git pull --ff-only || true
'
```

Install/update Codex CLI as needed:

```bash
ssh codex-ubuntu 'sudo npm install -g @openai/codex@latest && codex --version'
```

For Desktop app rebuilds, inspect the repo's current instructions before running them. Back up `~/codex-app` before replacing it:

```bash
ssh codex-ubuntu '
test -d ~/codex-app && cp -a ~/codex-app ~/codex-app.backup-$(date +%Y%m%d-%H%M%S) || true
'
```

After install, reassert the launcher shape and config. Do not overwrite unrelated user auth/session files.

## Chrome Install

Prefer Google Chrome stable over snap Chromium for profile-oriented browser work:

```bash
ssh codex-ubuntu '
set -euo pipefail
cd /tmp
wget -q -O google-chrome-stable_current_amd64.deb \
  https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get update -qq
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
google-chrome --version
command -v google-chrome
command -v google-chrome-stable
update-alternatives --query x-www-browser 2>/dev/null | awk "/Value:/{print \$2}"
'
```

X11 smoke test with a disposable profile:

```bash
ssh codex-ubuntu '
set -euo pipefail
rm -rf /tmp/chrome-profile-codex-smoke
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority nohup google-chrome \
  --user-data-dir=/tmp/chrome-profile-codex-smoke \
  --no-first-run --no-default-browser-check --disable-dev-shm-usage \
  about:blank >/tmp/chrome-smoke.out 2>/tmp/chrome-smoke.err < /dev/null &
sleep 4
google-chrome --version
pgrep -a "google-chrome|/opt/google/chrome/chrome" | head -20 || true
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xwininfo -root -tree 2>&1 |
  egrep "Google Chrome|about:blank|chrome" | head -40 || true
pkill -f "[c]hrome-profile-codex-smoke" 2>/dev/null || true
'
```

Use the bracketed `pkill` pattern so the cleanup command does not kill its own SSH shell.

## Browser/IAB Repair

If Browser plugin exists but available browsers are `[]`, check for stale IAB pipes and old app-server/node_repl processes:

```bash
ssh codex-ubuntu '
ls -lt /tmp/codex-browser-use 2>/dev/null | head -20
pgrep -a "codex app-server|node_repl|codex-app/electron|webview-server" || true
tail -n 160 ~/.cache/codex-desktop/launcher.log 2>/dev/null |
  egrep -i "browser_use|iab|native pipe|availability|backend|error|fail" | tail -120
'
```

Repair with the VM's force-restart helper:

```bash
ssh codex-ubuntu '~/.local/bin/codex-desktop-force-restart'
```

If the SSH command remains attached to the launched GUI, stop only the local SSH process and then verify the VM state. For a detached start:

```bash
ssh codex-ubuntu '
nohup ~/.local/bin/codex-desktop-launch \
  >/tmp/codex-desktop-restart.out 2>/tmp/codex-desktop-restart.err < /dev/null &
'
```

If stale old app-server/node_repl processes remain after restart, kill only the old PIDs after confirming the new process tree exists. Never broad-kill `codex` without checking PIDs.

## Final Verification Bundle

End every setup/repair with this bundle:

```bash
ssh codex-ubuntu '
echo "== versions =="
codex --version || true
google-chrome --version || true
echo "default_browser=$(update-alternatives --query x-www-browser 2>/dev/null | awk "/Value:/{print \$2}")"
echo "== config =="
egrep "remote_connections|remote_control|workspace_dependencies" ~/.codex/config.toml || true
echo "== processes =="
pgrep -a "codex-app/electron|codex app-server|webview-server|node_repl" | head -30 || true
echo "== iab =="
ls -lt /tmp/codex-browser-use 2>/dev/null | head -8 || true
tail -n 80 ~/.cache/codex-desktop/launcher.log 2>/dev/null |
  egrep -i "browser_use_iab_backend_startup_ready|native pipe listening|availability_resolved|error|fail" | tail -40 || true
echo "== windows =="
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xwininfo -root -tree 2>&1 |
  egrep "Codex|Google Chrome|electron|Chrome" | head -60 || true
'
```

Report the exact proof surfaces in the final answer:

- CLI version
- Chrome version and path
- default browser path
- Codex Desktop process/window status
- latest IAB pipe path and ready log line
- anything not verified, with the reason

## Common Failures

- `DISPLAY=` empty over SSH: normal for SSH. Use `DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority` for GUI proof.
- `Browser plugin exists but browsers=[]`: often stale IAB pipe/session or app-server/node_repl mismatch. Restart Codex Desktop and confirm a new `/tmp/codex-browser-use/*.sock`.
- Chrome not found: install Google Chrome stable, not just Firefox/snap browser.
- `xwininfo` cannot parse display: missing explicit `DISPLAY` or Xauthority.
- Old `/run/current-system/sw/bin/bash` errors in logs: stale launcher log from older Nix-style shebang; verify current launcher before diagnosing.
- SSH command hangs after launching Desktop: GUI process is attached to the SSH session; prefer detached `nohup` launch for final state.
