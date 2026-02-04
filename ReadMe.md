# GitLab ローカル PoC 環境

このプロジェクトは、Windows ローカル環境で動作する GitLab および Shadow Repository パターンの実証実験 (PoC) 環境です。

### 構成

-   **[PoC0: インフラ構築](./PoC0/README.md)**
    -   Docker Compose を使用して、GitLab CE と GitLab Runner をローカルに構築します。
    -   まずはこちらの手順に従って環境を立ち上げてください。

-   **[PoC2: Shadow Repository (実証環境)](./PoC2_GitLab/README.md)**
    -   「設計書リポジトリ (Excel)」をミラーリングし、「Shadow リポジトリ」側で Markdown に変換して管理するパターンを検証します。
    -   必要なスクリプトや CI 設定が含まれています。

-   **[PoC1: ローカル Shadow 開発環境](./PoC1_Local/)**
    -   Shadow Repository パターンのためのスクリプト開発や検証を行うローカル環境です。
    -   CI を通さずに手元で動作確認をするためのスクリプト(TODO.mdなど)が含まれています。

-   **[PoC3: ローカル Shadow ツール](./PoC3_LocalShadow/README.md)**
    -   GitLab CI を使わず、ローカル環境で大量の Excel ファイルを Shadow (Markdown) 化するツールです。
    -   オフライン (Air-gapped) 環境へのセットアップ手順も含まれています。
