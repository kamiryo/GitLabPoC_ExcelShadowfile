# PoC3: Local Recursive Excel Shadow Generator

このディレクトリは、ローカルリポジトリ内の大量のExcelファイルを一括でMarkdown (Shadow) 化するためのツールセットです。
GitLab CIを使わず、ローカルPC上で直接実行することを想定しています。

## 特徴

- 指定したディレクトリ（デフォルト: `doc`）以下のExcelファイルを再帰的に検索します。
- `.env` ファイル (`SHADOW_PASSWORDS`) に記載されたパスワードリストを使って、暗号化されたExcelファイルの復号を試みます。
- 変換結果は元のExcelファイルと同じ場所に `.<filename>.shadow` という名前で保存されます。

## セットアップ手順

1. **Pythonの準備**
   Python 3.10以上が推奨です。

2. **依存ライブラリのインストール**
   コマンドプロンプトやPowerShellで以下を実行します。

   ```powershell
   cd PoC3_LocalShadow
   pip install -r requirements.txt
   ```

3. **パスワード設定（任意・推奨）**
   `.env` ファイルを作成し、暗号化Excel用のパスワードを設定します。
   （サンプルとして `.env.sample` があります）
   
   ```powershell
   copy .env.sample .env
   ```

   `.env` ファイルをテキストエディタで開き、`SHADOW_PASSWORDS` にカンマ区切りでパスワードを記述します。

   ```text
   SHADOW_PASSWORDS=password,123456,admin,secret_key
   ```
   
   ※ `.env` ファイルは `.gitignore` に含まれているため、誤ってGitにコミットされるリスクが低減されます。

   > [!TIP]
   > `.env` ファイルは通常 `PoC3_LocalShadow` 直下に置きますが、`tools/generate_shadow_recursive.py` と同じ場所（`tools` フォルダ内）に置いても読み込まれます。

## 使い方

以下のコマンドを実行すると、`doc` フォルダ（存在しない場合は作成するか、引数で指定）配下のExcelファイルを変換します。

### 基本実行（docフォルダを対象）

```powershell
# カレントディレクトリに doc フォルダがある前提
python tools/generate_shadow_recursive.py
```

### フォルダを指定して実行

```powershell
# 任意のフォルダ（例: C:\MyProject\Specifications）を対象にする場合
python tools/generate_shadow_recursive.py "C:\MyProject\Specifications"
```

## 出力例

```text
Scanning directory: C:\googleantigravity\Poc3_LocalShadow\doc
Found 2 Excel files in 'doc'.
Processing: C:\googleantigravity\Poc3_LocalShadow\doc\Design.xlsx
  Generated Shadow: .Design.xlsx.shadow
```

## オンライン（インターネット接続あり）での実行

## オンライン（インターネット接続あり）での実行

**簡単実行スクリプト** (`run_online.bat`) を用意しました。
これを使うと、必要なライブラリのインストールからツール実行までを一括で行えます。

```powershell
cd PoC3_LocalShadow

# ツールを実行 (対象フォルダを指定)
.\run_online.bat "C:\Path\To\Your\ExcelDocs"
```

※ 初回実行時に `pip install` が自動的に行われます。2回目以降も、ライブラリの不足があれば自動補完します。

> [!NOTE]
> `ModuleNotFoundError: No module named 'msoffcrypto'` などのエラーが出る場合は、上記の `pip install` が完了していないか、失敗しています。必ず最初に実行してください。


## エアギャップ環境（インターネット接続なし）での実行

本環境がインターネットに接続できない場合、以下の手順でセットアップを行ってください。

### 1. 依存ライブラリの準備（インターネット接続可能なPCで実施）

1.  この `PoC3_LocalShadow` フォルダ一式を、インターネットに接続できる別のPCにコピーします。
2.  そのPC上で `download_deps.bat` を実行してください。
    - `packages` フォルダが作成され、必要なファイル（whl）がダウンロードされます。

### 2. インストール（本環境で実施）

1.  `packages` フォルダが含まれた状態の `PoC3_LocalShadow` フォルダ一式を、本環境（エアギャップ環境）にコピーします。
2.  `install_offline.bat` を実行してください。
    - `packages` フォルダ内のファイルを使ってインストールが行われます。

### 3. ツールの実行

通常通り実行できます。

```powershell
python tools/generate_shadow_recursive.py
```

