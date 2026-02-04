# PoC3: Local Recursive Excel Shadow Generator

このディレクトリは、ローカルリポジトリ内の大量のExcelファイルを一括でMarkdown (Shadow) 化するためのツールセットです。
GitLab CIを使わず、ローカルPC上で直接実行することを想定しています。

## 特徴

- 指定したディレクトリ（デフォルト: `doc`）以下のExcelファイルを再帰的に検索します。
- `passwords.txt` に記載されたパスワードリストを使って、暗号化されたExcelファイルの復号を試みます。
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

3. **パスワードリストの準備（任意）**
   `passwords.txt` を作成し、考えられるパスワードを1行に1つずつ記述してください。  
   （サンプルとして `passwords.txt.sample` があります）
   
   - **複数設定**: 1行につき1つのパスワードを書くことで、複数のパスワードを順に試行します。
   - **ファイルなし**: `passwords.txt` がなくてもツールは動作します（暗号化ファイルはスキップされます）。

   ```powershell
   copy passwords.txt.sample passwords.txt
   # その後、passwords.txt をエディタで編集して実際のパスワードを追記してください
   ```

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

