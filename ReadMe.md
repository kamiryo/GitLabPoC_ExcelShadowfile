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
├── .gitlab-scripts/         # Scripts for GitLab CI and shadow file generation
│   ├── generate_shadow.py   # Script to convert Excel to Markdown for diffing
│   ├── passwords.txt        # External password file for decrypting Excel files
│   └── ...                  # Other CI helper scripts & configs
├── config/                  # Configuration files (mounted to containers)
├── data/                    # Persistent data storage for GitLab/Runner
├── logs/                    # Log files
├── runner-config/           # GitLab Runner specific configuration
├── docker-compose.yml       # Defines GitLab CE and Runner services
├── generate_runner_token.sh # Helper to generate registration token via Rails console
├── setup_gitlab_runner.sh   # Automates runner registration
├── start_and_verify.sh      # Starts environment and verifies readiness
├── ReadMe.md                # This documentation
└── TODO.md                  # Task tracking
```

### Usage

#### 1. Start Services
Run the verification script from WSL:
```bash
./start_and_verify.sh
```
Or manually:
```bash
docker compose up -d
```

#### 2. Verify Service Startup & Access GitLab
Open your browser and navigate to:
http://localhost

*Note: For the initial login, you will need the `root` account. Please refer to the [Admin Credentials](#admin-credentials) section below to retrieve the initial password.*

### 3. Setup GitLab Runner (Automated)
After GitLab is ready (step 1), register the runner automatically:
```bash
./setup_gitlab_runner.sh
```
This script will:
- Generate a registration token via Rails console.
- Detect the Docker network.
- Register the runner in non-interactive mode.

> **Architecture Note (Executor Type)**:
> This script configures the runner to use the **`docker` executor** (defined by `RUNNER_EXECUTOR="docker"` in the script). 
> This means every CI job runs in a fresh, isolated Docker container. Changes made (like installing packages) are lost after the job finishes.
> This is why the `.gitlab-ci.yml` must explicitly install dependencies (`git`, `pip`, etc.) every time, unlike a `shell` executor which runs directly on the host machine.

**Verification:**
To confirm the runner is successfully registered and online, check the GitLab UI:
1. Go to **Admin Area** (the wrench icon on the top bar or sidebar).
2. Navigate to **CI/CD > Runners**.
3. You should see "Docker-Runner-PoC" listed with a green circle (online).

### 4. Shadow File Generation Tool PoC
This environment also includes a PoC for a "Shadow File Generation Tool" that converts Excel files to Markdown shadow files for better diffing.

#### Real Verification on GitLab CI (Recommended)
To test the actual CI pipeline behavior, create a project on your local GitLab instance and push the files.

1.  **Create Project**: 
    - Log in to GitLab (http://localhost) as `root`.
    - Click "New Project" > "Create blank project".
    - Project name: `shadow-poc-demo`.
    - Visibility: Public or Private.
    - **Important Configuration (Required for CI Push)**:
      - Go to **Settings > CI/CD > Job token permissions**.
      - Scroll down to the **"Additional permissions"** section.
      - Check the box for **"Allow Git push requests to the repository"**.
      - Click **"Save changes"**.
      - *Reason*: The `generate_runner_token.sh` script registers the runner but does not configure project-level permissions. This manual step is required for the CI job to push shadow files back to the repo.

    - **Important Configuration (Protected Branches)**:
      - Go to **Settings > Repository > Protected branches**.
      - Enable **"Allowed to force push"** for the `main` branch OR click **"Unprotect"**.
      - *Reason*: To allow the initial `git push -f` or to simplify the PoC setup.

2.  **Prepare Files & Push**:
    Run the following commands in your local terminal (Windows PowerShell) to prepare a clean directory and push it to GitLab:
    ```powershell
    # 1. Create a temporary folder for the repo
    mkdir dist-repo
    cd dist-repo

    # 2. Copy files (Adjusting structure for standard usage)
    # (Current Directory: dist-repo)
    # Copy CI config and gitattributes to ROOT
    copy ..\.gitlab-scripts\.gitlab-ci.yml .
    copy ..\.gitlab-scripts\.gitattributes .
    
    # Copy scripts to a subfolder
    mkdir .gitlab-scripts
    copy ..\.gitlab-scripts\generate_shadow.py .\.gitlab-scripts\
    copy ..\.gitlab-scripts\create_sample_excel.py .\.gitlab-scripts\

    # 3. Create a sample Excel file
    # (Prerequisite: Python and openpyxl must be installed locally)
    # pip install openpyxl
    python .\.gitlab-scripts\create_sample_excel.py

    # Move generated file to root if it is in .gitlab-scripts (handling environment differences)
    if (Test-Path .\.gitlab-scripts\sample.xlsx) { move .\.gitlab-scripts\sample.xlsx . }

    # 4. Initialize Git and Push
    git init
    git config merge.ours.driver true
    
    git add .
    git commit -m "Initial commit for PoC"

    # Rename branch to main (avoid master/main mismatch)
    git branch -M main
    
    # Note: Use the URL provided by GitLab, but replace 'gitlab.example.com' with 'localhost'
    git remote add origin http://localhost/root/shadow-poc-demo.git

    # Initial Push (Authentication Required)
    # Username: root
    # Password: The initial password retrieved in the "Admin Credentials" section
    # Note: Normally 'git push -u origin main' is sufficient, but we use force push here to ensure success during the initial push in case of conflicts or protection issues.
    git push -f origin main
    ```

3.  **Verify Pipeline**:
    - Go to **Build > Pipelines** in your GitLab project.
    - You should see a pipeline running `shadow-file-generation`.
    - Once finished, check the repository. You should see `.sample.xlsx.shadow` generated and committed by the CI bot.

#### Developer Setup (Required for Local)
To ensure shadow file conflicts are resolved automatically (keeping local changes), developers must configure a custom merge driver.
To ensure shadow file conflicts are resolved automatically (keeping local changes), developers must configure a custom merge driver.
Run the following command once on your local machine:
```bash
git config --global merge.ours.driver true
```
This works in conjunction with the `.gitattributes` file (located in `.gitlab-scripts/`) which defines `*.shadow merge=ours`.

#### CI Pipeline Integration (Recommended)
This project is configured to generate shadow files automatically using GitLab CI.
The configuration file `.gitlab-ci.yml` is located at the root of the repository (or in `.gitlab-scripts/` in this specific setup).

**Configuration File:**
See [.gitlab-scripts/.gitlab-ci.yml](.gitlab-scripts/.gitlab-ci.yml) for the complete configuration.

**Prerequisites & Important Configuration:**
1.  **Project Access Token / Job Token Scope**:
    (Configured in Step 1 of "Real Verification on GitLab CI" above)
2.  **GitLab Server Hostname**:
    The push URL uses `gitlab-server`. This hostname must be resolvable by the runner. 
    In this Docker Compose setup, `gitlab-server` is the service name, so it resolves correctly within the Docker network.
3.  **Preventing Infinite Loops**:
    The commit message includes `[skip ci]` to ensure the push does not trigger another pipeline run.

#### Manual Verification (Simulating CI)
To manually verify the script without pushing to a repo:

1. Copy the scripts to the runner container (simulating checking out the repo):
   ```bash
   docker compose cp .gitlab-scripts/ gitlab-runner:/tmp/.gitlab-scripts
   ```

2. Generate a sample Excel file inside the container:
   ```bash
   docker compose exec -w /tmp/.gitlab-scripts gitlab-runner python3 create_sample_excel.py
   ```

3. Run the shadow generation script:
   ```bash
   docker compose exec -w /tmp/.gitlab-scripts gitlab-runner python3 generate_shadow.py
   ```

4. Verify the shadow file was created:
   ```bash
   docker compose exec -w /tmp/.gitlab-scripts gitlab-runner ls -la .sample.xlsx.shadow
   ```

### 5. Admin Credentials
<a name="admin-credentials"></a>
If you are logging in for the first time:
- **Username**: `root`
- **Password**: Initially generated in the container. Retrieve it with:
  ```bash
  docker compose exec gitlab-server grep 'Password:' /etc/gitlab/initial_root_password
  ```

#### 6. Stop Services (Keep Data)
```bash
docker compose stop
```

#### 7. Destroy Environment (Delete All Data)
To remove containers and **permanently delete** all data volumes:
```bash
docker compose down -v
```

---

<a name="japanese"></a>
## 日本語 (Japanese)

このプロジェクトは、Windows 上の WSL2 (Ubuntu) 環境にて GitLab CE と GitLab Runner をローカル実行するための `docker compose` 設定を提供します。

### 前提条件
- Windows 10/11
- WSL2 が有効化されていること
- Ubuntu ディストリビューションがインストールされていること
- Docker および Docker Compose (v2) が **Ubuntu 環境内に** インストールされていること

> **重要**:
> この環境は Windows 側にインストールされた Docker Desktop を **使用しません**。
> Windows の PowerShell や CMD から `docker` や `docker compose` コマンドを直接実行することはできません。
> **すべての Docker コマンドは WSL2 (Ubuntu) のターミナル内で実行してください。**

### 開発環境情報
開発および検証に使用した環境情報は以下の通りです:
- **OS**: Windows 11 (Build 26200)
- **WSL2**: version 2.6.3.0
- **Linux ディストリビューション**: Ubuntu 24.04.1 LTS
- **Docker**: Version 27.3.1
- **Docker Compose**: version v2.29.7
- **Python**:
  - ローカル: 3.13.9 (依存ライブラリ: `openpyxl` 3.1.5)
  - コンテナ (`gitlab-runner`): 3.12.12
- **主要ライブラリ (コンテナ内)**:
  - `markitdown`: 0.0.2
  - `msoffcrypto-tool`: 5.4.2
  - `openpyxl`: 3.1.5

### プロジェクト構成
```text
GitLabPoC_ExcelShadowfile/
├── .gitlab-scripts/         # GitLab CI および Shadow ファイル生成用スクリプト
│   ├── generate_shadow.py   # Excel を Markdown に変換するスクリプト
│   ├── passwords.txt        # 暗号化 Excel 復号用のパスワードリスト
│   └── ...                  # その他 CI 補助スクリプト
├── config/                  # 設定ファイル群 (コンテナにマウント)
├── data/                    # GitLab/Runner の永続化データ
├── logs/                    # ログファイル
├── runner-config/           # GitLab Runner 固有設定
├── docker-compose.yml       # GitLab CE と Runner のサービス定義
├── generate_runner_token.sh # Rails コンソール経由でトークンを生成するヘルパー
├── setup_gitlab_runner.sh   # Runner 登録の自動化スクリプト
├── start_and_verify.sh      # 環境起動とステータス確認用スクリプト
├── ReadMe.md                # 本ドキュメント
└── TODO.md                  # タスク管理
```

### 使用方法

#### 1. サービスの起動
WSL 上で検証用スクリプトを実行します:
```bash
./start_and_verify.sh
```
または手動で起動します:
```bash
docker compose up -d
```

#### 2. サービスの起動確認と GitLab へのアクセス
ブラウザを開き、以下のアドレスにアクセスしてください:
http://localhost

この手順はサービスが正常に起動しているかの確認です。
*注意: 初回ログインには `root` アカウントが必要です。初期パスワードの取得方法は、後述の [管理者アカウント情報](#jp-admin-credentials) セクションを参照してください。*

#### 3. GitLab Runner のセットアップ (自動)
GitLab の起動完了後 (ステップ1の後)、Runner を自動登録します:
```bash
./setup_gitlab_runner.sh
```
このスクリプトは以下を実行します:
- Rails コンソール経由で登録トークンを生成
- Docker ネットワークを検出
- 非対話モードで Runner を登録

> **アーキテクチャに関する注記 (Executor タイプ)**:
> 本スクリプトは、Runner を **`docker` executor** として構成します (スクリプト内の `RUNNER_EXECUTOR="docker"` で定義)。
> これにより、各 CI ジョブは毎回クリーンな隔離された Docker コンテナ内で実行されます。ジョブ内で行った変更（パッケージインストール等）は、ジョブ終了とともに破棄されます。
> そのため `.gitlab-ci.yml` では、ホストマシンの環境を直接使う `shell` executor とは異なり、毎回 `git` や `pip` などの依存関係をインストールする手順が必要となります。

**登録確認:**
Runner が正しく登録されオンラインになっていることを確認します:
1. GitLab 画面で **Admin Area** (スパナアイコン) に移動します。
2. **CI/CD > Runners** を選択します。
3. "Docker-Runner-PoC" が緑色の丸（オンライン状態）で表示されていれば成功です。

#### 4. Shadow ファイル生成ツールの PoC (概念実証)
この環境には、Excel ファイルを diff 可能な Markdown 形式 ("Shadow File") に変換するツールの検証も含まれています。

#### GitLab 上での検証手順 (実環境)
実際の CI パイプラインが動作するか確認するために、ローカルの GitLab 上にプロジェクトを作成し、ファイルをプッシュします。

1.  **プロジェクト作成**:
    - GitLab (http://localhost) に `root` でログインします。
    - "New Project" > "Create blank project" を選択します。
    - プロジェクト名: `shadow-poc-demo`
    - Visibility: Public または Private
    - **重要な設定 (CI プッシュに必須)**:
      - **Settings > CI/CD > Job token permissions** に移動します。
      - **"Additional permissions"** セクションまでスクロールします。
      - **"Allow Git push requests to the repository"** にチェックを入れます。
      - **"Save changes"** をクリックします。
      - *理由*: `generate_runner_token.sh` は Runner 登録のみを行い、プロジェクトの権限設定は変更しません。CI ジョブが Shadow ファイルをリポジトリにプッシュし返すためには、この手動設定が必須となります。

    - **Important Configuration (Protected Branches)**:
      - **Settings > Repository > Protected branches** に移動します。
      - `main` ブランチに対して **"Allowed to force push"** を有効にするか、**"Unprotect"** をクリックして保護を解除します。
      - *理由*: 初回の `git push -f` を許可するため、または PoC における構成の簡略化のため。

2.  **ファイルの準備とプッシュ**:
    ローカルターミナル (PowerShell) で以下を実行し、ファイル構成を整えてプッシュします。
    ※ CI 設定ファイルなどはリポジトリのルートに配置し、スクリプト類はサブフォルダに配置する構成を作ります。

    ```powershell
    # 1. 配布用の一時フォルダ作成
    mkdir dist-repo
    cd dist-repo

    # 2. ファイルのコピー (標準的な構成に合わせる)
    # (カレントディレクトリ: dist-repo)
    # .gitlab-ci.yml と .gitattributes をルートにコピー
    copy ..\.gitlab-scripts\.gitlab-ci.yml .
    copy ..\.gitlab-scripts\.gitattributes .
    
    # スクリプトをサブフォルダにコピー
    mkdir .gitlab-scripts
    copy ..\.gitlab-scripts\generate_shadow.py .\.gitlab-scripts\
    copy ..\.gitlab-scripts\create_sample_excel.py .\.gitlab-scripts\

    # 3. サンプル Excel の生成
    # (前提: ローカル環境に Python と openpyxl がインストールされている必要があります)
    # pip install openpyxl
    python .\.gitlab-scripts\create_sample_excel.py
    
    # 生成されたファイルが .gitlab-scripts 内にある場合はルートに移動 (環境依存の可能性への対応)
    if (Test-Path .\.gitlab-scripts\sample.xlsx) { move .\.gitlab-scripts\sample.xlsx . }

    # 4. Git 初期化とプッシュ
    git init
    # 開発者設定: マージドライバを有効化 (コンフリクト回避)
    git config merge.ours.driver true
    
    git add .
    git commit -m "Initial commit for PoC"

    # ブランチ名を main に変更 (デフォルトが master の場合のエラー回避)
    git branch -M main
    
    # 注: URL は GitLab 画面の指示に従いますが、ホストは localhost にしてください
    git remote add origin http://localhost/root/shadow-poc-demo.git

    # 初回プッシュ (認証が求められます)
    # ユーザー名: root
    # パスワード: 前述の「管理者アカウント情報」で取得した初期パスワード
    # 注: 本来であれば、「git push -u origin main」で十分ですが、初回のプッシュ時に
    #     エラーが発生する可能性があるため、強制的にプッシュしています。
    git push -f origin main
    ```

3.  **パイプラインの確認**:
    - GitLab プロジェクトの **Build > Pipelines** を確認します。
    - `shadow-file-generation` ジョブが実行されているはずです。
    - 完了後、リポジトリを確認すると CI ボットによってコミットされた `.sample.xlsx.shadow` ファイルが確認できます。

#### 開発者セットアップ (ローカル作業用)
Shadow ファイルのコンフリクトを自動解決（ローカル優先）するため、開発者は以下のコマンドをローカル環境で一度実行する必要があります:
```bash
git config --global merge.ours.driver true
```
これは `.gitlab-scripts/` フォルダに含まれる `.gitattributes` ファイル（`*.shadow merge=ours` 設定）と組み合わせて機能します。

#### CI パイプライン設定 (推奨)
本プロジェクトは、GitLab CI を使用して Shadow ファイルを自動生成するように構成されています。
本来の構成では `.gitlab-ci.yml` はリポジトリのルートに配置されます（本環境では便宜上 `.gitlab-scripts/` に格納されています）。

**設定ファイル:**
完全な設定内容は [.gitlab-scripts/.gitlab-ci.yml](.gitlab-scripts/.gitlab-ci.yml) を参照してください。

**前提条件と重要な設定:**
1.  **Project Access Token / Job Token の権限**:
    (上記「GitLab 上での検証手順」のステップ 1 で設定済み)
2.  **GitLab サーバーのホスト名**:
    プッシュ先 URL には `gitlab-server` を使用しています。Runner がこのホスト名を解決できる必要があります。
    この Docker Compose 環境では、サービス名が `gitlab-server` であるため、Docker ネットワーク内で正しく解決されます。
3.  **無限ループの防止**:
    コミットメッセージに `[skip ci]` を含めることで、プッシュによって新たなパイプラインがトリガーされるのを防いでいます。

#### 手動検証 (CI の模倣)
リポジトリへプッシュせずにスクリプトの動作のみを確認する手順は以下の通りです:

1. スクリプトを Runner コンテナにコピーします (リポジトリのチェックアウトを模倣):
   ```bash
   docker compose cp .gitlab-scripts/ gitlab-runner:/tmp/.gitlab-scripts
   ```

2. コンテナ内でサンプル Excel ファイルを生成します:
   ```bash
   docker compose exec -w /tmp/.gitlab-scripts gitlab-runner python3 create_sample_excel.py
   ```

3. Shadow 生成スクリプトを実行します:
   ```bash
   docker compose exec -w /tmp/.gitlab-scripts gitlab-runner python3 generate_shadow.py
   ```

4. Shadow ファイルが作成されたことを確認します:
   ```bash
   docker compose exec -w /tmp/.gitlab-scripts gitlab-runner ls -la .sample.xlsx.shadow
   ```

#### 5. 管理者アカウント情報
<a name="jp-admin-credentials"></a>
初回ログイン時:
- **ユーザー名**: `root`
- **パスワード**: コンテナ内で初期生成されます。以下のコマンドで確認できます:
  ```bash
  docker compose exec gitlab-server grep 'Password:' /etc/gitlab/initial_root_password
  ```

#### 6. サービスの停止 (データ保持)
```bash
docker compose stop
```

#### 7. 環境の破棄 (全データ削除)
コンテナを削除し、すべてのデータボリュームを **完全に削除** するには:
```bash
docker compose down -v
```
