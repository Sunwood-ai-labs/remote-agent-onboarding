<div align="center">
  <img src="assets/eclipse-header.png" alt="Remote Agent Onboarding Skill - ECLIPSE -" width="100%">
  <h1>Remote Agent Onboarding Skill - ECLIPSE -</h1>
  <p>
    <a href="README.md">English</a> |
    <a href="README.ja.md">日本語</a>
  </p>
  <p>
    <a href="https://github.com/Sunwood-ai-labs/remote-agent-onboarding/actions/workflows/validate.yml"><img alt="Validate" src="https://github.com/Sunwood-ai-labs/remote-agent-onboarding/actions/workflows/validate.yml/badge.svg"></a>
    <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green.svg"></a>
    <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-111827">
    <img alt="Platform: Ubuntu" src="https://img.shields.io/badge/Platform-Ubuntu-E95420">
    <img alt="Chrome/CDP" src="https://img.shields.io/badge/Chrome-CDP-4285F4">
    <img alt="Automations" src="https://img.shields.io/badge/Automations-Smoke%20Test-7C3AED">
  </p>
</div>

SSH、Linuxデスクトップ表示、Codex Desktop、Chrome、Browser/IAB、モバイルリモート操作、専用ワークスペース、Codex Automationsを備えたリモートエージェントVMを、証跡ベースでセットアップ・修復・検証するためのCodexスキルです。

このスキルは「パッケージが入っている」だけではなく、SSH、GUI、Desktop、Chrome、IAB、Automationsなどの実際の利用面を分けて確認する運用を前提にしています。

## 対象

- Ubuntu/Linux系のリモートエージェントVMのセットアップ/修復
- SSH鍵ログイン、サービス状態、LAN側ポート疎通確認
- Codex CLI/Desktopの起動とGUIスクリーンショット確認
- `gpt-5.5`、low reasoning、フルアクセス、approvalなしの既定値確認
- Chromeの永続プロファイルとCDP確認
- Browser/IABソケットとログ確認
- 別VMからのCodex認証移行。ただし対象VMのidentityはコピーしない
- Codex mobile remote controlのdaemon、socket、登録状態確認
- Codex Automationsのローカル状態、UI、スモーク実行確認
- ブランク画面、ロック画面、黒いスクリーンショットの再発防止
- 専用ワークスペース作成と、復旧可能なローカルスレッド整理
- ProxmoxなどのVMホスト確認

## インストール

Codexのスキルディレクトリへcloneします。

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Sunwood-ai-labs/remote-agent-onboarding.git \
  ~/.codex/skills/remote-agent-onboarding
```

その後、新しいCodexセッションでリモートエージェントVMの作成、修復、検証を依頼してください。

## 使い方の例

```text
remote-agent-onboardingを使って、UbuntuのリモートエージェントVMを検証して。
SSH、Codex Desktop、Chrome、Browser/IAB、Automationsを分けて確認して。
```

## リリース対象の同期方針

`SKILL.md` が実運用手順の正本です。READMEは同じ主要機能を追跡しますが、すべてのコマンドを重複掲載しない方針です。
v0.1.0では、特に以下のガードレールを重視します。

- SSHはProxmox/QGAだけで完了扱いにしない。鍵ログイン、`sshd`
  enabled/active、22番listen、LAN側疎通まで見る。
- Codex Desktopはプロセス出力だけで完了扱いにしない。実画面の
  スクリーンショットを確認し、blank、lock、黒画面を完了証跡にしない。
- フルアクセス既定値はconfigだけで判断しない。model、reasoning、
  sandbox、approvalを実行時スモークで確認する。
- mobile設定は `remote_control = true` だけで完了扱いにしない。
  standalone daemon、control socket、enrollmentを確認する。
- 認証移行で `.codex` 全体をコピーしない。最小のauth情報だけを移し、
  対象VM固有のidentityは維持する。
- ローカルスレッド整理で全threadをデフォルト削除しない。確認済みの
  smoke-test `THREAD_IDS` を対象にし、全履歴削除は明示指示時だけにする。
- 専用ワークスペースを作成し、`~/Documents/Codex` など既定パスを向ける場合は既存内容をバックアップする。

## ファイル構成

- `SKILL.md` - Codexスキル本体
- `agents/openai.yaml` - UIメタデータ
- `references/codex-automations.md` - Automations検証とスモークテスト手順
- `scripts/validate_repo.py` - 公開リポジトリ検証スクリプト
- `.github/workflows/validate.yml` - GitHub Actions検証ワークフロー

## 安全上の注意

ログ、スクリーンショット、VM状態を公開する前に、以下を必ず削除してください。

- 認証情報、パスワード、Cookie、ブラウザプロファイルの秘密情報
- プライベートなIPアドレスやホスト名
- OAuthトークンやAPIキー
- VMイメージ、SSH秘密鍵、`.codex`データベース

AutomationsのスモークテストはCodexのローカルsqlite DBを変更します。必ずDBをバックアップし、検証後はスモークジョブを削除してください。

ローカルスレッド整理は `~/.codex/state_5.sqlite` とsession rolloutを変更する可能性があります。必ずバックアップし、デフォルトでは確認済みのsmoke-test threadだけを対象にしてください。ローカルVM履歴とaccount/cloud側プロジェクト履歴は別の証跡面として扱います。

一部のセットアップ手順は公式インストーラやパッケージを取得します。公開環境、規制環境、リリース用途では、実行前にスクリプト内容、バージョン固定、checksum確認の要否を確認してください。

## 検証

```bash
python3 scripts/validate_repo.py
git diff --check
```

## ライセンス

MIT。詳細は[LICENSE](LICENSE)を参照してください。
