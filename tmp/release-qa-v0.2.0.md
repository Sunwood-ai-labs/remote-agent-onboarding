# Release QA Inventory: v0.2.0

## Scope

- Repository: `Sunwood-ai-labs/remote-agent-onboarding`
- Previous tag: `v0.1.0`
- Target tag: `v0.2.0`
- Release theme: ECLIPSE fleet naming, mobile-visible remote-control identity, per-agent VPN proof separation, and public-safe release evidence.

## v0.1.0 / v0.2.0 Boundary

| Version | Public scope | Evidence |
| --- | --- | --- |
| v0.1.0 | Initial ECLIPSE Skill release for evidence-backed remote-agent VM onboarding. | Existing GitHub release body, `SKILL.md`, `README.md`, `README.ja.md`, article screenshots. |
| v0.2.0 | Fleet release covering ECLIPSE01-AURORA through ECLIPSE07-HARINA, mobile identity refresh, clone/auth migration boundaries, and per-agent VPN proof separation. | Updated `SKILL.md`, README files, `releases/v0.2.0.md`, v0.2.0 header, and fleet mobile screenshot. |

## Claim Matrix

| Claim | Evidence | Status |
| --- | --- | --- |
| ECLIPSE is the `remote-agent-onboarding` Skill, not a different remote-control repository. | Repository README title and GitHub release v0.1.0 body. | pass |
| v0.1.0 is the initial public release. | `gh release view v0.1.0` returned the v0.1.0 release body and URL. | pass |
| v0.2.0 adds the ECLIPSE fleet naming contract. | `SKILL.md`, `README.md`, and `README.ja.md` list the seven public fleet names. | pass |
| Mobile-visible renames require backend registration refresh, not hostname changes alone. | `SKILL.md` now requires target-local installation/environment IDs, live `remote-control start`, enrollment `server_name`, Desktop restart, and current mobile proof. | pass |
| VPN proof is separate from Codex readiness proof. | `SKILL.md` and README files keep VPN service/interface/IP proof separate from setup, identity, mobile, and operation surfaces. | pass |
| Release material avoids private IDs and network/account secrets. | Validation script scans text for Gmail, private LAN IP patterns, and local operator home paths; release text omits identity IDs and credentials. | pass |

## Steady-State Docs Review

| Surface | Review result | Status |
| --- | --- | --- |
| `SKILL.md` | Added fleet naming, mobile-visible identity refresh, clone repair, and proof-surface separation rules. | pass |
| `README.md` | Added v0.2.0 release-surface summary and fleet screenshot. | pass |
| `README.ja.md` | Japanese README synchronized with the v0.2.0 release-surface summary and screenshot. | pass |
| `references/codex-automations.md` | No change needed; v0.2.0 did not alter Automations smoke-test behavior. | pass |
| `agents/openai.yaml` | No change needed; display name remains skill-level, not release-version-specific. | pass |

## Validation Commands

| Command | Result |
| --- | --- |
| `gh release list --repo Sunwood-ai-labs/remote-agent-onboarding --limit 20` | confirmed only `v0.1.0` existed before v0.2.0 work |
| `gh release view v0.1.0 --repo Sunwood-ai-labs/remote-agent-onboarding --json name,tagName,publishedAt,url,body` | confirmed v0.1.0 release body and public URL |
| `./scripts/check-runtime.sh --provider Auto` in `cc-orchestrator-cli-skill` | fallback runtime ready, selected provider Zai |
| `python3 scripts/validate_repo.py` | run before final release publication |
| `git diff --check` | run before final release publication |

## Delegation And Fallback

Spark subagents were requested with the `gpt-5.3-codex-spark` model for release inspection and QA review. Both attempts failed with the current Spark usage limit. The fallback `cc-orchestrator-cli-skill` runtime check passed with `RUNTIME_READY`; no Claude team-mode edits were used for this release.

## Publication Guard

- Do not claim live current status for every ECLIPSE VM from this release material alone.
- Do not expose installation IDs, environment IDs, server IDs, IP addresses, VPN credentials, account emails, passwords, cookies, or browser profile material.
- If publishing or editing a note.com article later, verify the public repo URL, v0.1.0 release URL, v0.2.0 release URL, rendered article body, metadata/index, and URL-card placement separately.
