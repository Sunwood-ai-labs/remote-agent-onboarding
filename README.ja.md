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

Codex Desktop、Chrome、Browser/IAB、モバイルリモート操作、Codex Automationsを備えたLinuxリモートエージェントVMを、証跡ベースでセットアップ・修復・検証するためのCodexスキルです。

このスキルは「パッケージが入っている」だけではなく、SSH、GUI、Desktop、Chrome、IAB、Automationsなどの実際の利用面を分けて確認する運用を前提にしています。

## 対象

- Ubuntu系のリモートエージェントVMのセットアップ/修復
- Codex CLI/Desktopの起動とGUI表示確認
- Chromeの永続プロファイルとCDP確認
- Browser/IABソケットとログ確認
- Codex mobile remote controlの登録確認
- Codex Automationsのローカル状態、UI、スモーク実行確認
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

## 検証

```bash
python3 scripts/validate_repo.py
git diff --check
```

## ライセンス

MIT。詳細は[LICENSE](LICENSE)を参照してください。
