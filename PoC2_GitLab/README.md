# PoC 2: Shadow Repository Pattern

PoC 2 では、設計書（Excel）を管理する「コピー元（Design Repo）」と、変換されたファイルを管理する「Shadow Repo」を分離する構成を検証します。

### 導入手順

1.  **コピー元リポジトリ (Design Repo) の作成**:
    -   GitLab 上で新規プロジェクト（例: `design-repo`）を作成します。
    -   適当な Excel ファイルを追加し、`main` ブランチにコミットしてください。これが同期元となります。

2.  **Shadow リポジトリの作成**:
    -   GitLab 上で別の新規プロジェクト（例: `shadow-repo`）を作成します。
    -   ローカルにクローンします:
        ```bash
        git clone http://localhost/root/shadow-repo.git
        cd shadow-repo
        ```

3.  **Shadow リポジトリのセットアップ**:
    -   CI/CD 資材管理用のブランチ（推奨: `sys/ci`）を作成します。
        ```bash
        git checkout -b sys/ci
        ```
    -   本プロジェクトの `PoC2_GitLab/` 配下のすべてのファイルを、ローカルの `shadow-repo` のルートにコピーします。
        -   `.gitlab-ci.yml` がルートにあることを確認してください。
        -   `scripts/` フォルダなどが含まれていることを確認してください。
    -   コミットしてプッシュします:
        ```bash
        git add .
        git commit -m "Shadow Repository CI 初期化"
        git push origin sys/ci
        ```

4.  **CI/CD の設定**:
    -   Shadow Repo の **Settings > CI/CD > Variables** に移動します。
    -   `SOURCE_REPO_URL` を追加: Copy 元 (Design Repo) の URL (例: `http://gitlab-server/root/design-repo.git`)。
        -   *注意: PoC0 の Docker ネットワーク内からアクセスするため、ホスト名は `localhost` ではなく `gitlab-server` を使用してください。*
    -   `SOURCE_PROJECT_ID` を追加: Copy 元 (Design Repo) の Project ID (例: `123`)。
        -   *Open なマージリクエストを API 経由で取得するために使用します。*
    -   `ACCESS_TOKEN` を追加: Copy 元への Read 権限と、Shadow Repo への Write 権限を持つアクセストークン。
    -   **重要**: Copy 元 (Design Repo) の **Settings > CI/CD > Token Access** にて、Shadow Repo (例: `root/shadow-repo`) からのアクセスを許可してください。

5.  **スケジュールの設定**:
    -   Shadow Repo の **Build > Pipeline schedules** に移動します。
    -   新しいスケジュールを作成し（例: 5分毎）、ターゲットブランチを `sys/ci` に設定して保存します。
