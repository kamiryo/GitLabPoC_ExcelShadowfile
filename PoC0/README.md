# PoC0: GitLab Local Docker Environment

このディレクトリには、Windows 上で GitLab CE と GitLab Runner をローカル実行するための `docker compose` 設定が含まれています。

### 前提条件 (Windows)
-   **Docker Desktop for Windows** がインストールされ、実行されていること。
-   **Git** がインストールされていること。
-   **PowerShell** が利用可能であること。

### 導入手順

1.  **GitLab 環境の起動**:
    このディレクトリ (`PoC0`) で PowerShell を開き、以下を実行します:
    ```powershell
    docker compose up -d
    ```
    `gitlab-server` (GitLab CE) と `gitlab-runner` が起動します。GitLab の起動には数分（2〜5分）かかります。

2.  **GitLab Runner の登録**:
    セットアップスクリプトを実行して、ローカルの GitLab インスタンスに Runner を自動登録します。
    ```powershell
    .\setup_gitlab_runner.ps1
    ```
    (Bash 環境がある場合は、旧来の `setup_gitlab_runner.sh` も利用可能です)

3.  **GitLab へのログイン**:
    -   ブラウザで [http://localhost](http://localhost) にアクセスします。
    -   **ユーザー名**: `root`
    -   **パスワード**:
        初期ルートパスワードを確認するには以下を実行します:
        ```powershell
        docker compose exec gitlab-server grep 'Password:' /etc/gitlab/initial_root_password
        ```
    -   初回ログイン後、パスワードを変更してください。
