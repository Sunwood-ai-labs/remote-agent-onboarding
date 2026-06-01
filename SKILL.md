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

- Host/VM reachability: SSH to the target user with the intended key; verify
  `sshd` is enabled/active, port 22 is reachable from the operator machine,
  and `~/.ssh` / `authorized_keys` permissions are sane.
- CLI/app: `codex --version`, app bundle/processes.
- Config: `~/.codex/config.toml` has remote features enabled.
- GUI: X11 `Codex` window is visible through the live display and Xauthority;
  verify the session is active and unlocked, not just that a window exists.
- Browser binary: Chrome exists and launches on X11.
- Persistent Chrome profile: when site session continuity matters, Chrome can launch with the agent profile and CDP on `127.0.0.1:9222`.
- Browser plugin/IAB: `/tmp/codex-browser-use/*.sock` is current and logs show IAB ready.
- Workspace/thread hygiene: if onboarding created smoke-test threads, verify
  whether the user wants them kept. Local thread cleanup must distinguish the
  VM's local SQLite/session state from account/cloud project history.

## Setup vs Operation

Keep setup and operation separate in both the work and the final report.

Setup means making the workstation capable:

- VM identity, SSH, `codex` user, X11/Xfce, and `DISPLAY=:0` are established.
- SSH is not "done" until key login works from the operator machine, `sshd`
  is enabled and active, and port 22 has an external LAN reachability check.
- Codex CLI/Desktop, launchers, and `~/.codex/config.toml` are installed or repaired.
- Default Codex posture is explicitly set and smoke-tested: model, reasoning
  effort, sandbox mode, and approval policy must be visible in an actual
  `codex exec` run log, not only present in config text.
- Desktop proof screenshots are required for user-facing readiness. For Codex
  Desktop work, save a screenshot after the final restart and ensure it shows a
  usable Codex surface, not only process/log output.
- Google Chrome stable is installed and X11 smoke-tested.
- Optional but recommended for browser-heavy agents: `agent-chrome-profile-browser` exists, its helper scripts are executable, and `/home/codex/.config/google-chrome-codex-profile/Default` can be used.
- Browser/IAB pipes and Desktop logs show a ready integration surface.
- A dedicated workspace exists for the agent, with any legacy default path
  symlinked or redirected to it when the app expects a default folder.

Operation means using the prepared workstation safely:

- Start or reuse the persistent Chrome profile for logged-in web tasks.
- Verify the active proof surface before acting: process args, CDP `/json/version`, `chrome://version`, visible window, target site logged-in state, or IAB logs as relevant.
- Do not use `about:blank` as the final desktop proof. It only proves a blank
  browser tab, not that the workstation is ready. Open the requested app or a
  meaningful logged-in/home surface before taking the proof screenshot.
- If screenshots are black, color-shifted, or show only a blank surface, check
  session lock state before diagnosing video drivers. Run `loginctl` and verify
  the target session is `Active=yes` and `LockedHint=no`.
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
- When migrating Codex authentication from another VM, copy only the minimal
  auth material first (`~/.codex/auth.json`) and preserve the target VM's
  launcher/config identity. Back up target auth/state before copying, then
  restart Desktop and verify it reaches an authenticated Codex surface.
- For form submissions, confirm visible UI commitment, especially chips/tokens and uploaded filenames.
- End by reporting which surfaces were actually verified and which were not.

## Completion Guardrails

Before saying an Eclipse/remote-agent VM is ready, run a final live check close
to the report time:

```bash
ssh codex-ubuntu '
echo "== identity =="; hostname; date; whoami
echo "== ssh =="
systemctl is-enabled ssh 2>/dev/null || systemctl is-enabled sshd 2>/dev/null || true
systemctl is-active ssh 2>/dev/null || systemctl is-active sshd 2>/dev/null || true
ss -ltnp 2>/dev/null | grep ":22 " || true
ls -ld ~/.ssh 2>/dev/null || true
ls -l ~/.ssh/authorized_keys 2>/dev/null || true
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

For dedicated workspace and local thread cleanup, prefer a reversible cleanup:

```bash
ssh codex-ubuntu '
set -euo pipefail
WORK="$HOME/Workspaces/AGENT_NAME"
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="$HOME/.codex/backups/thread-clean-$TS"
export BACKUP
# Space-separated thread IDs that were confirmed as onboarding/smoke-test
# threads. Leave CLEAN_ALL_THREADS unset unless the user explicitly asked for
# every local VM thread to be removed.
THREAD_IDS="REPLACE_WITH_CONFIRMED_SMOKE_THREAD_IDS"
CLEAN_ALL_THREADS="${CLEAN_ALL_THREADS:-no}"
export THREAD_IDS CLEAN_ALL_THREADS
mkdir -p "$WORK/notes" "$WORK/artifacts" "$WORK/tmp" "$BACKUP"
cp -a "$HOME/.codex/state_5.sqlite" "$BACKUP/state_5.sqlite.before-thread-clean" 2>/dev/null || true
python3 - <<'"'"'PY'"'"'
import json, pathlib, sqlite3, shutil, os
home = pathlib.Path.home()
backup = pathlib.Path(os.environ["BACKUP"])
db = home / ".codex/state_5.sqlite"
if db.exists():
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    requested = [x for x in os.environ.get("THREAD_IDS", "").split() if x and x != "REPLACE_WITH_CONFIRMED_SMOKE_THREAD_IDS"]
    if os.environ.get("CLEAN_ALL_THREADS") == "yes":
        rows = list(con.execute("select id, rollout_path from threads"))
    elif requested:
        q = ",".join("?" for _ in requested)
        rows = list(con.execute(f"select id, rollout_path from threads where id in ({q})", requested))
    else:
        print("No THREAD_IDS supplied; leaving local thread DB unchanged.")
        rows = []
    archive = backup / "session-rollouts"
    archive.mkdir(exist_ok=True)
    for r in rows:
        if r["rollout_path"]:
            p = pathlib.Path(r["rollout_path"]).expanduser()
            if p.exists() and str(p.resolve()).startswith(str((home / ".codex").resolve())):
                dest = archive / p.name
                if dest.exists():
                    dest = archive / f"{p.stem}-{r['id']}{p.suffix}"
                shutil.move(str(p), str(dest))
    ids = [r["id"] for r in rows]
    if ids:
        q = ",".join("?" for _ in ids)
        con.execute(f"delete from thread_dynamic_tools where thread_id in ({q})", ids)
        con.execute(f"delete from thread_spawn_edges where parent_thread_id in ({q}) or child_thread_id in ({q})", ids + ids)
        con.execute(f"delete from agent_job_items where assigned_thread_id in ({q})", ids)
        con.execute(f"delete from threads where id in ({q})", ids)
        con.commit()
    print("threads_after", con.execute("select count(*) from threads").fetchone()[0])
p = home / ".codex/.codex-global-state.json"
if p.exists():
    d = json.loads(p.read_text())
    for key in ("projectless-thread-ids", "thread-workspace-root-hints", "thread-projectless-output-directories", "composer-prompt-drafts-v1", "prompt-history"):
        d.pop(key, None)
    d["heartbeat-thread-permissions-by-id"] = {}
    d["unread-thread-ids-by-host-v1"] = {"local": []}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
PY
if [ -e "$HOME/Documents/Codex" ] && [ ! -L "$HOME/Documents/Codex" ]; then
  mv "$HOME/Documents/Codex" "$BACKUP/Documents-Codex-old"
fi
mkdir -p "$HOME/Documents"
ln -sfn "$WORK" "$HOME/Documents/Codex"
'
```

Cleanup rule: never imply account/cloud project history was deleted when only
local VM SQLite/session state was cleaned. If the sidebar still shows remote
projects, report them as account/cloud history unless separately verified.

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

For public, regulated, or release-sensitive environments, do not blindly run the
remote installer. Inspect the fetched script, prefer pinned versions or checksum
verification where available, and report any remaining supply-chain assumption.

Mobile setup is not complete from any single one of these signals alone:

- `remote_control = true` in `config.toml`
- the Codex Mobile sidebar item being visible
- `has-seen-codex-mobile-announcement = true`
- an `electron-local-remote-control-installation-id` in global state

Completion requires daemon/control-socket proof plus enrollment/visibility
state. At minimum report:

```bash
ssh codex-ubuntu '
echo "== config =="
egrep "remote_connections|remote_control" ~/.codex/config.toml || true
echo "== daemon =="
codex app-server daemon version 2>&1 || true
ls -l ~/.codex/app-server-control 2>/dev/null || true
echo "== remote start =="
codex remote-control start --json 2>&1 || true
echo "== state =="
python3 - <<'"'"'PY'"'"'
import json, pathlib
p=pathlib.Path.home()/".codex/.codex-global-state.json"
if p.exists():
    d=json.loads(p.read_text())
    print("installation", d.get("electron-local-remote-control-installation-id"))
    print("environment", d.get("electron-local-remote-control-environment-id"))
else:
    print("installation", None)
    print("environment", None)
PY
sqlite3 ~/.codex/state_5.sqlite \
  "select server_name, environment_id, updated_at from remote_control_enrollments;" 2>/dev/null || true
'
```

If `codex app-server daemon version` cannot connect to
`~/.codex/app-server-control/app-server-control.sock`, the CLI-managed mobile
daemon is not running. Start/repair it before saying mobile is set up.

When migrating or repairing mobile setup, live daemon output and DB enrollment
must agree. If `codex remote-control start --json` returns one `environmentId`
but `remote_control_enrollments` contains older or duplicate target rows,
stop/start the daemon and keep only the live target row:

```bash
ssh codex-ubuntu '
export PATH="$HOME/.local/bin:$PATH"
codex remote-control stop --json 2>&1 || true
sleep 3
codex remote-control start --json | tee /tmp/remote-control-start.json
python3 - <<'"'"'PY'"'"'
import json, pathlib, sqlite3

home = pathlib.Path.home()
start = json.loads(pathlib.Path("/tmp/remote-control-start.json").read_text())
server = start.get("serverName")
environment = start.get("environmentId")
con = sqlite3.connect(home / ".codex/state_5.sqlite")
rows = list(con.execute(
    "select rowid from remote_control_enrollments "
    "where server_name=? and environment_id=? order by updated_at desc",
    (server, environment),
))
if rows:
    keep = rows[0][0]
    con.execute(
        "delete from remote_control_enrollments where server_name=? and rowid<>?",
        (server, keep),
    )
    con.execute(
        "update remote_control_enrollments set app_server_client_name=? where rowid=?",
        ("Codex Desktop", keep),
    )
    con.commit()
for row in con.execute(
    "select server_name, environment_id, server_id, app_server_client_name, updated_at "
    "from remote_control_enrollments"
):
    print(row)
PY
'
```

If the source VM itself does not have a running standalone daemon, do not treat
its stale enrollment as authoritative. Mirror its portable user preferences, but
use the target VM's standalone daemon to create fresh target-local enrollment.

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
model = "gpt-5.5"
model_reasoning_effort = "low"
sandbox_mode = "danger-full-access"
approval_policy = "never"

[features]
remote_connections = true
remote_control = true
workspace_dependencies = false
```

The launcher should use `#!/usr/bin/env bash` and execute `/home/codex/codex-app/start.sh`.

For remote-agent employee VMs, the default operating posture is full local
workspace access with no interactive approval prompts, unless the user asks for a
safer mode or the target environment is not externally trusted. Verify this with
a lightweight `codex exec` smoke test before reporting completion:

```bash
ssh codex-ubuntu '
cd /tmp
codex exec --skip-git-repo-check --color never \
  "Reply exactly: remote-agent Codex OK" 2>&1 | tee /tmp/codex-defaults-smoke.log
'
```

The smoke log should show:

```text
model: gpt-5.5
approval: never
sandbox: danger-full-access
reasoning effort: low
```

For Codex Desktop, config is not the whole truth. The Desktop composer can keep
its own persisted permission state under `~/.codex/.codex-global-state.json`.
After setting `config.toml`, also verify and, when needed, repair:

```bash
ssh codex-ubuntu '
python3 - <<'"'"'PY'"'"'
import json, pathlib
p=pathlib.Path.home()/".codex/.codex-global-state.json"
if p.exists():
    d=json.loads(p.read_text())
    s=d.setdefault("electron-persisted-atom-state", {})
    print("agent-mode-by-host-id", s.get("agent-mode-by-host-id"))
    print("heartbeat-thread-permissions-by-id", s.get("heartbeat-thread-permissions-by-id"))
else:
    print("agent-mode-by-host-id", None)
    print("heartbeat-thread-permissions-by-id", None)
PY
'
```

Expected Desktop state for the default full-access posture:

```json
{
  "agent-mode-by-host-id": {"local": "full-access"},
  "heartbeat-thread-permissions-by-id": {
    "<thread-id>": {
      "approvalPolicy": "never",
      "approvalsReviewer": "user",
      "sandboxPolicy": {"type": "dangerFullAccess"}
    }
  }
}
```

If the UI still shows `Default permissions` / `デフォルト権限`, do not report
full access. Back up `~/.codex/.codex-global-state.json`, update the Desktop
persisted state, restart Codex Desktop, and capture a screenshot that visibly
shows `Full access` / `フルアクセス` plus the expected model setting.

When aligning a target VM with a known-good source VM such as VM101, copy only
the portable settings. Do not copy source-machine remote identity:

Portable:

- `model`, `model_reasoning_effort`, `approval_policy`,
  `approvals_reviewer`, and `sandbox_mode`
- `[features].remote_connections` and `[features].remote_control`
- Desktop persisted `agent-mode-by-host-id.local = full-access`
- Desktop persisted `composer-permission-mode-visibility.full-access = true`
- Desktop thread permissions with `approvalPolicy = never` and
  `sandboxPolicy.type = dangerFullAccess`
- onboarding role/work mode, for example `engineering` / `coding`

Do not copy:

- `electron-local-remote-control-installation-id`
- `electron-local-remote-control-environment-id`
- `remote_control_enrollments.server_id`
- `remote_control_enrollments.environment_id`
- `remote_control_enrollments.server_name`

Copying those identity fields can make the target VM appear as the source VM in
mobile/remote-control surfaces. Keep or regenerate target-local identity and
keep `server_name` equal to the target hostname.

Then restart Codex Desktop and capture a visible proof screenshot:

```bash
ssh codex-ubuntu '
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority gnome-screenshot \
  -f /tmp/codex-desktop-defaults-proof.png
ls -lh /tmp/codex-desktop-defaults-proof.png
'
scp codex-ubuntu:/tmp/codex-desktop-defaults-proof.png .
```

The screenshot must show a normal Codex Desktop surface such as the home screen,
project list, or the task composer. A screenshot of terminal output alone is not
enough when the user asked whether the Desktop app works.

## Desktop Blank/Lock Prevention

Before final screenshots on desktop-agent VMs, make screen blanking and lock
state explicit. A VM can have live GUI processes while the visible console is
locked or showing a greeter on another display.

Read the current state:

```bash
ssh codex-ubuntu '
loginctl list-sessions
loginctl show-user "$USER" -p State -p Sessions -p Display -p RuntimePath || true
for s in $(loginctl list-sessions --no-legend | awk "{print \$1}"); do
  loginctl show-session "$s" -p Name -p Display -p Desktop -p Type -p Active -p State -p LockedHint 2>/dev/null
done
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xset q 2>/dev/null |
  egrep "timeout:|DPMS is|Monitor is" || true
'
```

If the target user session is locked or inactive, unlock it and return to the
desktop TTY before capturing proof:

```bash
ssh codex-ubuntu '
sudo loginctl unlock-sessions || true
sudo loginctl unlock-session SESSION_ID || true
sudo chvt 7 || true
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xset s off -dpms s noblank || true
'
```

For persistent no-blank setup, apply both desktop settings and an autostart
hook. Adapt `$HOME`, user, and Xauthority paths for non-default users such as
`eclipse`:

```bash
ssh codex-ubuntu '
mkdir -p ~/.config/autostart ~/.local/bin
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority \
  gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null || true
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority \
  gsettings set org.gnome.desktop.screensaver lock-enabled false 2>/dev/null || true
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority \
  gsettings set org.gnome.desktop.lockdown disable-lock-screen true 2>/dev/null || true
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority xset s off -dpms s noblank || true
cat > ~/.local/bin/remote-agent-no-blank.sh <<'"'"'SH'"'"'
#!/usr/bin/env bash
export DISPLAY=${DISPLAY:-:0}
export XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority}
xset s off -dpms s noblank 2>/dev/null || true
gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null || true
gsettings set org.gnome.desktop.screensaver lock-enabled false 2>/dev/null || true
gsettings set org.gnome.desktop.lockdown disable-lock-screen true 2>/dev/null || true
SH
chmod +x ~/.local/bin/remote-agent-no-blank.sh
cat > ~/.config/autostart/remote-agent-no-blank.desktop <<DESKTOP
[Desktop Entry]
Type=Application
Name=Remote Agent No Blank
Exec=$HOME/.local/bin/remote-agent-no-blank.sh
X-GNOME-Autostart-enabled=true
NoDisplay=true
DESKTOP
'
```

If `gnome-screenshot` or VNC capture returns black while `xwininfo` shows
windows, first re-check `LockedHint` and `Active`. In one verified elementary
OS/Pantheon VM, `DISPLAY=:0` held the user session while a LightDM greeter was
active on `:1`; `loginctl unlock-sessions` and `chvt 7` restored a normal VNC
screenshot.

Screenshot proof should be visually meaningful:

- Codex proof: authenticated Codex home, project list, or the requested Codex UI.
- Chrome proof: target page, `chrome://version`, or real logged-in surface.
- Desktop proof: wallpaper/panel/dock plus the requested application.

Do not accept a blank browser page, lock screen, greeter, or all-black PNG as
completion proof.

## Codex Auth Migration

When the user asks to bring Codex authentication from another VM, migrate the
smallest useful auth surface first. Do not copy the entire `~/.codex` directory
unless the user explicitly asks for all history/state; whole-directory copies can
carry stale installation IDs, remote-control enrollments, paths, automations,
logs, and source-VM identity.

Recommended flow from source `codex-ubuntu` to target `eclipse@VM_IP`:

```bash
ts=$(date +%Y%m%d-%H%M%S)
mkdir -p "./auth-migration-$ts"

ssh codex-ubuntu '
python3 - <<'"'"'PY'"'"'
import json, pathlib
p=pathlib.Path.home()/".codex/auth.json"
d=json.loads(p.read_text())
print("source_auth_bytes", p.stat().st_size)
print("source_auth_keys", sorted(d.keys()))
print("source_auth_mode", d.get("auth_mode"))
PY
'

scp codex-ubuntu:/home/codex/.codex/auth.json "./auth-migration-$ts/auth.json.from-source"

ssh -i KEY eclipse@VM_IP '
mkdir -p ~/.codex/backups
[ ! -f ~/.codex/auth.json ] ||
  cp -a ~/.codex/auth.json ~/.codex/backups/auth.json.before-migration-'"$ts"'
'

scp -i KEY "./auth-migration-$ts/auth.json.from-source" eclipse@VM_IP:/home/eclipse/.codex/auth.json

ssh -i KEY eclipse@VM_IP '
chmod 600 ~/.codex/auth.json
python3 - <<'"'"'PY'"'"'
import json, pathlib
p=pathlib.Path.home()/".codex/auth.json"
d=json.loads(p.read_text())
print("target_auth_bytes", p.stat().st_size)
print("target_auth_keys", sorted(d.keys()))
print("target_auth_mode", d.get("auth_mode"))
PY
'
```

After copying auth, restart Codex Desktop using a detached launcher. Avoid broad
`pkill -f codex` patterns that can match the SSH command itself; kill exact old
PIDs or launch a fresh Desktop if none is running:

```bash
ssh -i KEY eclipse@VM_IP '
export DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000
for xauth in "$HOME/.Xauthority" /var/run/lightdm/root/:0; do
  [ -r "$xauth" ] && export XAUTHORITY="$xauth" && break
done
nohup /home/eclipse/codex-app/start.sh \
  >~/.cache/codex-desktop-auth-migration.log 2>&1 < /dev/null &
sleep 10
pgrep -af "/home/eclipse/codex-app|codex app-server|webview-server" | head -40
DISPLAY=:0 xwininfo -root -tree 2>&1 |
  egrep "Codex|codex" | head -60
'
```

Verification is visual and state-based:

- `~/.codex/auth.json` exists, is `0600`, and has the expected auth keys.
- Codex Desktop restarts and shows an authenticated surface, not only a
  sign-in page.
- First-run onboarding is acceptable after auth migration; complete or skip it,
  then capture the normal Codex home/project surface.
- If the source and target app versions differ, state this explicitly. A working
  `auth.json` can survive version skew, but version mismatch is a residual risk.
- Do not report mobile remote-control migration complete from auth migration
  alone. Remote-control identity/enrollment must be checked separately.

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
- default model, reasoning effort, sandbox mode, and approval policy from the
  latest `codex exec` smoke log
- screenshot path for the final visible Desktop proof, with what is visible in
  the image
- Chrome version and path
- default browser path
- persistent Chrome profile/CDP status, if used or relevant
- Codex Desktop process/window status
- latest IAB pipe path and ready log line
- Automations DB/file/UI/run status, if Automations were requested or expected
- anything not verified, with the reason

## Common Failures

- Config text exists but runtime uses different defaults: run `codex exec` and
  read the session header. Do not infer defaults from `config.toml` alone.
- SSH is not proven by a successful Proxmox console or QGA ping. Verify
  key-based login from the operator machine, `sshd` active/enabled, port 22
  listening, and a LAN `nc -vz VM_IP 22` check.
- Existing threads are not fully cleaned by deleting only prompt history in
  `.codex-global-state.json`. Also inspect `~/.codex/state_5.sqlite` and
  archive/delete related rollout files. Keep a DB backup before changing it.
- A clean local thread list does not mean account/cloud project history was
  deleted. Treat sidebar project entries as a separate proof surface.
- A dedicated workspace is not proven by creating a folder alone. Verify the
  path exists and any legacy default such as `~/Documents/Codex` resolves to it.
- `gpt-5.5 low` default not proven: the smoke log must show both
  `model: gpt-5.5` and `reasoning effort: low`.
- Full-access default not proven: the smoke log must show
  `sandbox: danger-full-access` and `approval: never`. `--strict-config`
  only validates keys; it does not prove runtime behavior.
- `codex exec` outside a git repository stops before model proof: include
  `--skip-git-repo-check` for `/tmp` smoke tests.
- `codex exec --no-alt-screen` fails under the `exec` subcommand: `--no-alt-screen`
  is a top-level interactive option, not an `exec` option in the verified CLI.
  Use `--color never` for readable noninteractive logs.
- CLI smoke succeeds but no screenshot is captured: not enough for Desktop
  readiness. Capture a final image showing the Codex Desktop home/project/task
  surface and inspect it before reporting completion.
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
