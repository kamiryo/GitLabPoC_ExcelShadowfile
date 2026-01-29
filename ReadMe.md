
# GitLab Local PoC Environment / GitLab ローカル PoC 環境

[English](#english) | [日本語](#japanese)

---

<a name="english"></a>
## English

This project provides a `docker compose` configuration to run GitLab CE and GitLab Runner locally on Windows via WSL2 (Ubuntu).

### Prerequisites
- Windows 10/11
- WSL2 enabled
- Ubuntu distribution installed
- Docker and Docker Compose (v2) installed **inside** the Ubuntu distribution.

> **IMPORTANT WARNING**: 
> This environment **does NOT** have Docker Desktop installed on Windows. 
> You CANNOT run `docker` or `docker compose` commands directly from Windows PowerShell/CMD.
> **ALL Docker commands MUST be executed within the WSL2 (Ubuntu) terminal.**

### Development Environment
The following environment was used for development and verification:
- **OS**: Windows 11 (Build 26200)
- **WSL2**: version 2.6.3.0
- **Linux Distro**: Ubuntu 24.04.1 LTS
- **Docker**: Version 27.3.1
- **Docker Compose**: version v2.29.7
- **Python**:
  - Local: 3.13.9 (Dependencies: `openpyxl` 3.1.5)
  - Container (`gitlab-runner`): 3.12.12
- **Key Libraries (Container)**:
  - `markitdown`: 0.0.2
  - `msoffcrypto-tool`: 5.4.2
  - `openpyxl`: 3.1.5

### Project Structure
```text
GitLabPoC_ExcelShadowfile/
├── PoC1_Local/              # [Moved] Resources for PoC 1 (Single Repo)
│   ├── .gitlab-scripts/
│   ├── config/
│   ├── data/
│   ├── logs/
│   ├── runner-config/
│   ├── docker-compose.yml
│   └── ...
├── PoC2_GitLab/             # [NEW] Resources for PoC 2 (Shadow Repository)
│   ├── scripts/
│   │   ├── mirror_design_repo.py     # 1. Sync Design Repo to Shadow Repo
│   │   ├── update_shadow_branches.py # 2. Generate shadows in _shadow branches
│   │   ├── generate_shadow.py        # Core shadow logic
│   │   └── utils.py                  # Helper functions
│   └── .gitlab-ci.yml       # CI Pipeline for Shadow Repo
├── ReadMe.md                # This documentation
└── TODO.md                  # Task tracking
```

### Usage (PoC 2: Shadow Repository)

PoC 2 implements a **Shadow Repository** pattern. This separates the "Design Repository" (where users work on Excel files) from the "Shadow Repository" (where shadow files are generated and viewed).

#### Architecture
- **Design Repo**: Source of Truth. No CI for shadow generation here.
- **Shadow Repo**:
  - Mirrors branches from Design Repo.
  - Generates `*_shadow` branches containing markdown representations.
  - Runs a scheduled CI job (`mirror_design_repo.py` then `update_shadow_branches.py`) to keep everything in sync.

#### Setup Instructions
1.  **Create a "Shadow Repository"** in GitLab.
2.  **Add `PoC2_GitLab` files** to this repository (e.g., in `main` or a dedicated `sys/ci` branch).
3.  **Configure CI Variables**:
    - `SOURCE_REPO_URL`: URL of the Design Repo (e.g., `https://gitlab.example.com/group/design-repo.git`).
    - `ACCESS_TOKEN`: A Project Access Token (or Personal Access Token) with `read_repository` on Design Repo and `write_repository` on Shadow Repo.
4.  **Set up a Schedule**:
    - Go to CI/CD > Schedules.
    - Create a new schedule (e.g., "Every 5 minutes" -> `*/5 * * * *`).
    - Variable: `TARGET_BRANCHES` (Optional, defaults to `main`).

---

<a name="japanese"></a>
## 日本語 (Japanese)

このプロジェクトは、Windows 上の WSL2 (Ubuntu) 環境にて GitLab CE と GitLab Runner をローカル実行するための `docker compose` 設定を提供します。
PoC 2 では、ユーザーが利用する「設計書リポジトリ」と、閲覧用に変換された「シャドウリポジトリ」を分離する構成を検証します。

### 前提条件 (PoC 1 と同様)
- Windows 10/11
- WSL2 (Ubuntu), Docker, Docker Compose

### プロジェクト構成
```text
GitLabPoC_ExcelShadowfile/
├── PoC1_Local/              # [移動済] PoC 1 用の資材 (単一リポジトリ構成)
│   ├── .gitlab-scripts/
│   ├── docker-compose.yml
│   └── ... (旧ルートディレクトリのファイル群)
├── PoC2_GitLab/             # [新規] PoC 2 用の資材 (Shadow リポジトリ構成)
│   ├── scripts/
│   │   ├── mirror_design_repo.py     # 1. Design Repo の同期スクリプト
│   │   ├── update_shadow_branches.py # 2. Shadow ブランチ更新スクリプト
│   │   ├── generate_shadow.py        # Shadow 生成ロジック
│   │   └── utils.py                  # ヘルパー関数
│   └── .gitlab-ci.yml       # Shadow リポジトリ用の CI 定義
├── ReadMe.md                # 本ドキュメント
└── TODO.md                  # タスク管理
```

### PoC 2: Shadow Repository の概要

PoC 2 では、設計書（Excel）が日々更新される **Design Repo** には変更を加えず、それをミラーリングした **Shadow Repo** 側で Shadow ファイル（Markdown）を生成・管理します。

#### アーキテクチャと動作
1.  **Design Repo (Source)**:
    - ユーザーはここに Excel ファイルをコミットします。
    - ここでは Shadow 生成 CI は動きません。
2.  **Shadow Repo (Destination)**:
    - **`sys/ci`** ブランチ (推奨): CI スクリプトや `.gitlab-ci.yml` を配置する管理用ブランチ。
    - **ミラーリング**: 定期的に Design Repo のブランチ (`main` 等) を取得します。
    - **Shadow 生成**: 対象ブランチ（`main` や Open なマージリクエストのブランチ）に対して、`*_shadow` ブランチ（例: `main_shadow`）を作成し、そこに Shadow ファイルをコミットします。

#### 導入手順

1.  **Shadow リポジトリの作成**:
    - GitLab 上で新規プロジェクト（Shadow Repo）を作成します。

2.  **資材の配置**:
    - `PoC2_GitLab` フォルダの中身を、Shadow Repo の `sys/ci` ブランチ（または `main`）にプッシュします。
    - ディレクトリ構造はそのまま `scripts/` と `.gitlab-ci.yml` がルートに来るように配置してください。

3.  **CI 変数の設定**:
    - **Settings > CI/CD > Variables** にて以下を設定します:
        - `SOURCE_REPO_URL`: Design Repo のクローン用 URL (例: `https://gitlab.example.com/group/design-repo.git`)。
        - `ACCESS_TOKEN`: アクセストークン。Design Repo への Read 権限と、Shadow Repo への Write 権限が必要です。
          - ※ CI ジョブ内で `git clone` や `git push` を行うために使用します。セキュリティのため Mask して登録してください。

4.  **スケジュールの設定**:
    - **Build > Pipeline schedules** に移動します。
    - "New schedule" を作成します。
    - Interval Pattern: `*/5 * * * *` (5分毎) (または任意の Cron 設定)
    - Target Branch: 資材を配置したブランチ (`sys/ci` など)

5.  **動作確認**:
    - スケジュールを手動実行（Play）するか、時間が来るのを待ちます。
    - 実行ログを確認し、Design Repo から変更が取得され、Shadow Repo に `main_shadow` などのブランチが生成されていることを確認します。

### PoC 1 について
PoC 1 (単一リポジトリ内での Shadow 生成) のドキュメントは、以前の README を参照してください。資材は `PoC1_Local` に移動されていますが、ローカルでの Docker Compose 環境構築方法は変わりません。実行時は `cd PoC1_Local` してからコマンドを実行してください。
