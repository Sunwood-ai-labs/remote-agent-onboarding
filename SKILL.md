---
name: remote-agent-onboarding
description: Create, onboard, repair, and verify a remote-agent employee Linux VM, from VM provisioning through SSH, Linux GUI, Codex Desktop, Chrome, Browser/IAB, mobile remote control, Automations, and proof-surface checks. Use when the user asks to create a remote agent workstation, prepare or repair Codex Desktop/Chrome/Browser access, or document the end-to-end remote agent onboarding workflow.
---

# Remote Agent Onboarding

Use this skill to turn a fresh Linux VM into a working "remote agent employee" workstation. The finish line is not a created VM or an installed package; the finish line is an agent that can log in, show a real GUI, run Codex Desktop, launch Chrome, and expose Browser/IAB proof.

Default example target:

- VM: `101` when the user uses the default example
- SSH alias: `codex-ubuntu`
- User inside VM: `codex`
- OS family: Ubuntu 24.04 LTS
- Desktop app path: `/home/codex/codex-app`
- Launcher: `/home/codex/.local/bin/codex-desktop-launch`
- Repair launcher: `/home/codex/.local/bin/codex-desktop-force-restart`

## Operating Rule

Separate proof surfaces. Do not say the VM is ready from a single package version.

Report only after the requested surface has been verified. If a step was inferred,
stale, or only partially checked, say that explicitly and do not present it as
confirmed-current.

Required proof surfaces:

- Host/VM reachability: SSH to `codex-ubuntu`.
- CLI/app: `codex --version`, app bundle/processes.
- Config: `~/.codex/config.toml` has remote features enabled.
- GUI: X11 `Codex` window is visible through `DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority`.
- Browser binary: Chrome exists and launches on X11.
- Persistent Chrome profile: when site session continuity matters, Chrome can launch with the agent profile and CDP on `127.0.0.1:9222`.
- Browser plugin/IAB: `/tmp/codex-browser-use/*.sock` is current and logs show IAB ready.

## Setup vs Operation

Keep setup and operation separate in both the work and the final report.

Setup means making the workstation capable:

- VM identity, SSH, `codex` user, X11/Xfce, and `DISPLAY=:0` are established.
- Codex CLI/Desktop, launchers, and `~/.codex/config.toml` are installed or repaired.
- Google Chrome stable is installed and X11 smoke-tested.
- Optional but recommended for browser-heavy agents: `agent-chrome-profile-browser` exists, its helper scripts are executable, and `/home/codex/.config/google-chrome-codex-profile/Default` can be used.
- Browser/IAB pipes and Desktop logs show a ready integration surface.

Operation means using the prepared workstation safely:

- Start or reuse the persistent Chrome profile for logged-in web tasks.
- Verify the active proof surface before acting: process args, CDP `/json/version`, `chrome://version`, visible window, target site logged-in state, or IAB logs as relevant.
- Capture the Xfce desktop through `xfdesktop` when root screenshots are black.
- If you stop Codex Desktop or Chrome to capture a clean screenshot, restart the
  requested app afterward and re-verify process, window, and log readiness before
  reporting completion.
- When the user asks for an image-generated asset, preserve and share the actual
  image generation output path. Do not substitute a locally scripted placeholder
  or report that the generated image was used unless that exact file was copied,
  applied, and visually checked.
- For smartphone/mobile access, separate VM readiness from mobile reachability:
  verify config flags, local service bind addresses, LAN reachability from
  another machine, and phone-side visibility separately. Do not claim phone
  access from `remote_control = true` alone.
- For Codex Automations, separate feature availability from registered job
  state. A VM can show the Automations UI and still have zero runnable jobs.
  Local Mac automations do not imply VM automations; compare the VM's
  `~/.codex/sqlite/codex-dev.db` and `~/.codex/automations/` directly.
- For Codex mobile remote control, verify the CLI-managed daemon too. The CLI
  `codex remote-control start` path requires the standalone Codex install at
  `~/.codex/packages/standalone/current/codex`; an npm-only install can run
  Desktop but fail remote-control daemon startup.
- For form submissions, confirm visible UI commitment, especially chips/tokens and uploaded filenames.
- End by reporting which surfaces were actually verified and which were not.

## Completion Guardrails

Before saying an Eclipse/remote-agent VM is ready, run a final live check close
to the report time:

```bash
ssh codex-ubuntu '
echo "== identity =="; hostname; date; whoami
echo "== codex =="
codex --version || true
egrep "remote_connections|remote_control|workspace_dependencies" ~/.codex/config.toml || true
pgrep -af "codex-app/electron|codex app-server|webview-server|node_repl" || true
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xwininfo -root -tree 2>&1 |
  egrep "Codex|codex|electron" | head -60 || true
echo "== iab =="
ls -lt /tmp/codex-browser-use 2>/dev/null | head -10 || true
tail -n 160 ~/.cache/codex-desktop/launcher.log 2>/dev/null |
  egrep -i "browser_use_iab_backend_startup_ready|native pipe listening|availability_resolved|error|fail" |
  tail -40 || true
echo "== listen =="
ss -ltnp 2>/dev/null | egrep "codex|electron|node|5175|9222|LISTEN" || true
'
```

For LAN/mobile proof, additionally test from outside the VM:

```bash
for p in 22 5175 9222 3000 8000; do
  printf "%s " "$p"
  nc -vz -w 2 VM_IP "$p" 2>&1 | tail -1
done
```

Interpretation rule: `127.0.0.1` listeners are local-only. A refused LAN probe
means browser access from a phone on the LAN is not proven, even if the VM is
healthy and remote feature flags are enabled.

For mobile remote-control proof, run the CLI daemon path and check enrollment:

```bash
ssh codex-ubuntu '
export PATH="$HOME/.local/bin:$PATH"
test -x ~/.codex/packages/standalone/current/codex ||
  { curl -fsSL https://chatgpt.com/codex/install.sh -o /tmp/codex-install.sh &&
    sed -n "1,80p" /tmp/codex-install.sh &&
    sh /tmp/codex-install.sh; }
codex app-server daemon bootstrap
codex app-server daemon enable-remote-control
codex remote-control start --json
codex app-server daemon version
sqlite3 --version >/dev/null 2>&1 || sudo apt-get update -qq && sudo apt-get install -y sqlite3
sqlite3 ~/.codex/state_5.sqlite "select server_name, environment_id, updated_at from remote_control_enrollments;"
'
```

If `remote-control start` reports `managed standalone Codex install not found`,
install the standalone CLI with the official installer, ensure
`~/.local/bin/codex` points to it, then restart Codex Desktop with:

```bash
export PATH="$HOME/.local/bin:$PATH"
export CODEX_CLI_PATH="$HOME/.local/bin/codex"
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority XDG_RUNTIME_DIR=/run/user/1000 \
  ~/.local/bin/codex-desktop-force-restart
```

When a VM is cloned from a working remote-control VM, do not trust cloned
remote identity state. Compare the clone against the source and remove stale
source identity before final verification:

```bash
python3 - <<'PY'
import json, os, sqlite3
home=os.path.expanduser("~")
state=os.path.join(home, ".codex/.codex-global-state.json")
data=json.load(open(state))
print(data.get("electron-local-remote-control-environment-id"))
print(data.get("electron-local-remote-control-installation-id"))
con=sqlite3.connect(os.path.join(home, ".codex/state_5.sqlite"))
for row in con.execute("select server_name, environment_id, app_server_client_name, updated_at from remote_control_enrollments"):
    print(row)
PY
```

If the clone still has the source VM's `electron-local-remote-control-environment-id`
or a `remote_control_enrollments` row for the source server name, back up
`~/.codex/.codex-global-state.json` and `~/.codex/state_5.sqlite*`, remove the
stale source keys/rows, then restart Desktop so it creates a fresh
`server_name=<clone-name>, app_server_client_name=Codex Desktop` enrollment.

For Codex Automations proof, verify local state, Desktop UI, and runtime
execution. Read [references/codex-automations.md](references/codex-automations.md)
before creating, migrating, or smoke-testing automation jobs. That reference
includes the required DB backup, harmless smoke test, cleanup, and path
migration checks.

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

- VM id/name should map to the requested agent employee. For the default example, use `101` / `codex-ubuntu`.
- Install Ubuntu 24.04 LTS with a graphical X11 desktop, usually XFCE/LightDM.
- Create user `codex` and ensure SSH access from the host via alias `codex-ubuntu`.
- Ensure the `codex` user can run required maintenance commands with noninteractive sudo, or report the password blocker clearly.
- Ensure X11 is available as `DISPLAY=:0` with `~/.Xauthority`.
- Do not call setup complete until SSH, X11, and GUI proof pass.

If the host appears to be Proxmox, useful checks may include `qm status <vmid>` and `qm guest cmd <vmid> ping`, but always verify from inside the VM by SSH as well.

## Codex Desktop Install Or Refresh

Use the current local/project-specific installer path if available. One Linux desktop wrapper project has used this shape:

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

When public or regulated environments require supply-chain pinning, inspect
remote installer scripts and prefer pinned package versions or checksum
verification before execution.

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

### Persistent Agent Chrome Profile

Setup goal: ensure the VM has a reusable Chrome profile path and a reliable launcher shape. Operation goal: use that profile for real web tasks and prove session continuity before trusting it.

For tasks that need saved login state, file uploads, screenshots, or Chrome DevTools Protocol control from the VM, use a dedicated agent profile instead of a disposable smoke profile:

```text
USER_DATA_DIR=/home/codex/.config/google-chrome-codex-profile
PROFILE_DIR=Default
DEBUG_PORT=9222
```

#### Setup

If the `agent-chrome-profile-browser` skill exists on the VM, prefer its bundled launcher:

```bash
ssh codex-ubuntu '
cd ~/.codex/skills/agent-chrome-profile-browser
scripts/start_chrome_profile.sh "https://example.com"
pgrep -a -f "chrome.*google-chrome-codex-profile" | head -20
curl -s http://127.0.0.1:9222/json/version
'
```

During setup, verify the profile directory exists after first launch:

```bash
ssh codex-ubuntu '
ls -ld /home/codex/.config/google-chrome-codex-profile \
  /home/codex/.config/google-chrome-codex-profile/Default 2>/dev/null || true
'
```

If the skill is not installed, the launcher shape to preserve is:

```bash
ssh codex-ubuntu '
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority setsid google-chrome \
  --no-sandbox \
  --remote-debugging-port=9222 \
  --user-data-dir=/home/codex/.config/google-chrome-codex-profile \
  --profile-directory=Default \
  --no-first-run \
  --start-maximized \
  "https://example.com" >/tmp/codex-chrome-profile.log 2>&1 < /dev/null &
'
```

#### Operation

For profile proof, do not rely on an `about:blank` screenshot. Confirm the process command line and CDP response, then open `chrome://version` when stronger proof is needed and verify:

```text
Profile Path /home/codex/.config/google-chrome-codex-profile/Default
```

For session persistence, terminate only this profile's Chrome processes, restart with the same profile, then verify the target site reaches the logged-in surface rather than a sign-in prompt:

```bash
ssh codex-ubuntu '
pkill -TERM -f "chrome.*google-chrome-codex-profile" || true
sleep 2
if cd ~/.codex/skills/agent-chrome-profile-browser 2>/dev/null; then
  scripts/start_chrome_profile.sh "https://example.com"
else
  DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority setsid google-chrome \
    --no-sandbox \
    --remote-debugging-port=9222 \
    --user-data-dir=/home/codex/.config/google-chrome-codex-profile \
    --profile-directory=Default \
    --no-first-run \
    --start-maximized \
    "https://example.com" >/tmp/codex-chrome-profile.log 2>&1 < /dev/null &
fi
'
```

Never store or repeat passwords in the skill or final answer. If credentials are needed, use only credentials supplied in the current conversation.

### Xfce Home-Screen Capture

On Xfce VMs, root screenshots can be black even after `xset dpms force on`. The useful proof surface is the `xfdesktop` window, not the X11 root window. If the `agent-chrome-profile-browser` skill is installed, use:

```bash
ssh codex-ubuntu '
cd ~/.codex/skills/agent-chrome-profile-browser
scripts/capture_xfce_home_screen.sh /tmp/remote-agent-home-screen.png
ls -l /tmp/remote-agent-home-screen.png
'
```

The expected desktop proof includes the Xfce wallpaper and icons such as `File System`, `Home`, and `Codex Desktop`. If the helper is absent, find the `xfdesktop` window from `_NET_CLIENT_LIST`, capture it with `xwd -id`, and convert the XWD to PNG.

### CDP And Form Interaction Notes

When using Chrome DevTools Protocol on `127.0.0.1:9222`, list tabs with:

```bash
ssh codex-ubuntu 'curl -s http://127.0.0.1:9222/json'
```

Before submitting forms or sending content, verify visible UI state, not only JavaScript values:

- required fields are visibly populated
- chip/token fields such as recipients are committed after Enter or Tab
- attachment filenames are visible after upload
- success or final confirmation text appears after submit

If a site reports a required field is missing despite inserted text, treat it as a UI commit failure and re-enter through the visible field with the same keyboard action a human would use.

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
echo "== agent chrome profile =="
pgrep -a -f "chrome.*google-chrome-codex-profile" | head -12 || true
curl -s --max-time 2 http://127.0.0.1:9222/json/version 2>/dev/null || true
echo "== automations =="
sqlite3 ~/.codex/sqlite/codex-dev.db "select count(*) from automations; select count(*) from automation_runs;" 2>/dev/null || true
find ~/.codex/automations -maxdepth 2 -name automation.toml -print 2>/dev/null | head -20 || true
echo "== windows =="
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xwininfo -root -tree 2>&1 |
  egrep "Codex|Google Chrome|electron|Chrome" | head -60 || true
'
```

Report the exact proof surfaces in the final answer:

- setup status: installed/repaired pieces and setup-only blockers
- operation status: live surfaces used in the current task and operation-only blockers
- CLI version
- Chrome version and path
- default browser path
- persistent Chrome profile/CDP status, if used or relevant
- Codex Desktop process/window status
- latest IAB pipe path and ready log line
- Automations DB/file/UI/run status, if Automations were requested or expected
- anything not verified, with the reason

## Common Failures

- `DISPLAY=` empty over SSH: normal for SSH. Use `DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority` for GUI proof.
- `Browser plugin exists but browsers=[]`: often stale IAB pipe/session or app-server/node_repl mismatch. Restart Codex Desktop and confirm a new `/tmp/codex-browser-use/*.sock`.
- Chrome not found: install Google Chrome stable, not just Firefox/snap browser.
- Profile proof is weak if it is only an `about:blank` screenshot. Use process args, CDP `/json/version`, and `chrome://version` profile path.
- Login/session persistence is not proven by a Chrome process alone. Restart this profile's Chrome and verify the target site opens to the logged-in surface.
- X11 root screenshots can be black on Xfce. Capture the `xfdesktop` window or use `agent-chrome-profile-browser/scripts/capture_xfce_home_screen.sh`.
- Web form automation can fail when visible text is not committed as a chip/token. Type into the visible field and press Enter or Tab before submitting.
- Automations UI exists but the list is empty: this usually means no local jobs
  are registered on the VM. Check both sqlite and `~/.codex/automations/`.
- A manually inserted automation does not appear until Codex Desktop restarts:
  the Desktop/app-server may cache automation state at startup.
- A Mac automation copied to Linux fails: the stored `cwds` and prompt paths may
  still point at source-host paths instead of real VM paths.
- `xwininfo` cannot parse display: missing explicit `DISPLAY` or Xauthority.
- Old `/run/current-system/sw/bin/bash` errors in logs: stale launcher log from older Nix-style shebang; verify current launcher before diagnosing.
- SSH command hangs after launching Desktop: GUI process is attached to the SSH session; prefer detached `nohup` launch for final state.
