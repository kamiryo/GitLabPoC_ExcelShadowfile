# PoC0: ローカル GitLab & Runner 環境

このディレクトリには、DockerベースのGitLab Runnerを使用したローカルGitLabインスタンスを実行するために必要な設定とスクリプトが含まれています。

## クイックスタート (WSL)

1.  **サービスの起動**:
    ```powershell
    wsl bash -c "cd /mnt/c/GoogleAntigravity/ExcelShadow/PoC0 && docker compose up -d"
    ```
2.  **初期化の待機**:
    GitLabの起動には数分かかります。`http://localhost` にアクセスできるまでお待ちください。
3.  **Runnerの登録**:
    修正されたセットアップスクリプトを使用して自動的に登録できます。
    ```powershell
    wsl bash -c "cd /mnt/c/GoogleAntigravity/ExcelShadow/PoC0 && ./setup_gitlab_runner.sh"
    ```
    実行後、GitLabの管理画面 (CI/CD > Runners) で `Docker-Runner-PoC` が登録されていることを確認してください。

## ファイル説明

| ファイル/ディレクトリ | 用途・説明 |
| :--- | :--- |
| `docker-compose.yml` | **構成定義**: GitLab本体とRunnerを起動するための設定ファイル。 |
| `runner-config/` | **Docker設定**: Runnerが使用するカスタムDockerイメージ（Python環境など）の定義。 |
| `setup_gitlab_runner.sh`| **セットアップ**: Runnerのトークン生成から登録までを一括で行う自動化スクリプト。 |
| `generate_runner_token.sh` | **補助ツール**: トークン生成のみを行うスクリプト（デバッグ用）。 |
| `gen_token.rb` | **内部ファイル**: スクリプトが内部で使用するRubyコード（一時ファイル）。 |
| `start_and_verify.sh` | **補助ツール**: サービスの起動とヘルスチェックを行うスクリプト。 |

## アクセス情報
*   **GitLab URL**: http://localhost
*   **ユーザー**: `root`
*   **パスワード**:
    ```powershell
    wsl docker exec gitlab-server grep 'Password:' /etc/gitlab/initial_root_password
    ```

## 環境の削除 (Cleanup)

PoC環境を完全に削除（コンテナ、ネットワーク、および**全てのデータ**を含むボリュームの削除）するには、以下のコマンドを実行してください。

```powershell
wsl bash -c "cd /mnt/c/GoogleAntigravity/ExcelShadow/PoC0 && docker compose down -v"
```

> [!WARNING]
> `-v` オプションを付けると、GitLabのリポジトリデータやRunnerの設定など、ボリュームに保存された全てのデータが**永久に失われます**。

