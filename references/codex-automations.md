# Codex Automations Verification

Use this reference when a remote-agent VM is expected to use Codex Automations.

Automations have three separate proof surfaces:

- Local state: `~/.codex/sqlite/codex-dev.db` and `~/.codex/automations/`
- Desktop UI: the Automations page lists the job
- Runtime: `automation_runs` receives a row and the job produces an expected harmless artifact

Do not claim Automations are unavailable just because there is no `codex automation` CLI command. The local app can use sqlite rows and `~/.codex/automations/<id>/automation.toml`.

## Read-Only Comparison

```bash
ssh codex-ubuntu '
echo "== automation db =="
sqlite3 ~/.codex/sqlite/codex-dev.db ".schema automations" 2>/dev/null | head -40 || true
sqlite3 ~/.codex/sqlite/codex-dev.db "select count(*) from automations; select count(*) from automation_runs;" 2>/dev/null || true
echo "== automation files =="
find ~/.codex/automations -maxdepth 2 -type f -print 2>/dev/null | head -40
echo "== cli surface =="
codex --help | grep -i automation || true
codex app-server generate-ts --out /tmp/codex-ts-automation-check >/dev/null 2>&1 || true
grep -Rni "automation" /tmp/codex-ts-automation-check 2>/dev/null | head -20 || true
'
```

## Smoke Test

If the VM has the Automations UI but no jobs, register a harmless smoke job only after backing up the DB. A working registration needs both the sqlite row and the TOML directory.

Set `workspace` to a real writable project on the VM before running this snippet.

```bash
ssh codex-ubuntu '
id="remote-agent-automation-smoke-test"
workspace="$HOME/Documents/remote-agent-sandbox"
log_path="$workspace/automation-smoke-test.log"
backup="$HOME/.codex/backup-automation-smoke-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup" "$HOME/.codex/automations/$id" "$workspace"
cp "$HOME/.codex/sqlite/codex-dev.db" "$backup/codex-dev.db"
now=$(date +%s%3N); next=$((now + 20000))
prompt="This is a harmless smoke test. Work in $workspace. Append the current date to $log_path, then report the path. Do not access external services."
cat > "$HOME/.codex/automations/$id/automation.toml" <<EOF
version = 1
id = "$id"
kind = "cron"
name = "Remote agent automation smoke test"
prompt = "$prompt"
status = "ACTIVE"
rrule = "FREQ=HOURLY;INTERVAL=1"
model = "gpt-5.3-codex"
reasoning_effort = "low"
execution_environment = "local"
cwds = ["$workspace"]
created_at = $now
updated_at = $now
EOF
sqlite3 "$HOME/.codex/sqlite/codex-dev.db" <<SQL
insert or replace into automations
(id,name,prompt,status,next_run_at,last_run_at,cwds,rrule,model,reasoning_effort,created_at,updated_at)
values
("$id","Remote agent automation smoke test","$prompt","ACTIVE",$next,NULL,"[\"$workspace\"]","FREQ=HOURLY;INTERVAL=1","gpt-5.3-codex","low",$now,$now);
SQL
'
```

Restart Codex Desktop, open the Automations page, and confirm the sample is listed. Then wait past `next_run_at` and check:

```bash
ssh codex-ubuntu '
id="remote-agent-automation-smoke-test"
sqlite3 ~/.codex/sqlite/codex-dev.db "
select id,status,next_run_at,last_run_at from automations where id=\"$id\";
select automation_id,status,thread_title,source_cwd from automation_runs where automation_id=\"$id\";
"
find "$HOME/Documents" -path "*/automation-smoke-test.log" -maxdepth 4 -type f -print -exec tail -20 {} \; 2>/dev/null || true
'
```

Success criteria:

- the Desktop UI lists the job
- `automation_runs` gets a row
- final status reaches `PENDING_REVIEW` or another non-empty run status
- the target log file is written

## Cleanup

Remove the smoke job immediately so the hourly test does not keep running. Leave the run history and artifact if they are useful as evidence.

```bash
ssh codex-ubuntu '
id="remote-agent-automation-smoke-test"
backup="$HOME/.codex/backup-automation-smoke-cleanup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
cp "$HOME/.codex/sqlite/codex-dev.db" "$backup/codex-dev.db"
test -d "$HOME/.codex/automations/$id" && cp -a "$HOME/.codex/automations/$id" "$backup/$id" || true
sqlite3 "$HOME/.codex/sqlite/codex-dev.db" "delete from automations where id=\"$id\";"
rm -rf "$HOME/.codex/automations/$id"
'
```

## Migration Notes

When moving real automations from one machine to another, rewrite paths before enabling them. For example, a macOS path such as `/Users/example/Prj/...` must be changed to a real Linux VM path such as `/home/codex/...`.

Copying rows unchanged can create jobs that reference nonexistent paths.
