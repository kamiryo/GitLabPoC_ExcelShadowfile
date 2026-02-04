# Excel生成・加工ツール

人間が作成したような特徴を持つExcelファイルを生成・加工するツールです。PoC2の検証用に、商用ブランチをシミュレートする現実的なテストデータを作成できます。

## 特徴

このツールは以下の「人間らしい」特徴をExcelファイルに付与します：

- **列幅・行高さのばらつき**: 手動調整を模したランダムな変動
- **フォント・色のバリエーション**: 業務でよく使われるフォントと色の自然な混在
- **データ入力の不規則性**: 余分な空白、全角半角の混在、日付フォーマットの揺れ
- **自然な配置**: 左揃え、中央、右揃えの適切な使い分け
- **タイプミス風の要素**: データの一部に欠損値や計算ミスを含む

## 必要な環境

- Python 3.8以上
- 依存ライブラリ: `openpyxl`

### インストール

```bash
pip install openpyxl
```

## 使用方法

### 1. 新規Excelファイルの作成

テンプレートを指定して、サンプルデータ入りのExcelファイルを生成します。

```bash
# 売上データを生成
python excel_generator.py create --template sales --output sales_data.xlsx

# 従業員リストを100件生成
python excel_generator.py create --template employee --rows 100 --output employees.xlsx

# プロジェクト工程表を生成
python excel_generator.py create --template project --output schedule.xlsx

# 予算表を生成
python excel_generator.py create --template budget --output budget.xlsx

# 在庫リストを生成
python excel_generator.py create --template inventory --output inventory.xlsx
```

### 2. 既存Excelファイルの修正

既存のExcelファイルにデータを追加したり、人間らしい特徴を再適用したりできます。

```bash
# 既存ファイルに売上データを50行追加
python excel_generator.py modify --file data.xlsx --add-rows 50 --template sales

# 既存ファイルに人間らしい特徴を再適用（強度: heavy）
python excel_generator.py modify --file data.xlsx --randomize --intensity heavy

# 特定のシートだけを修正
python excel_generator.py modify --file data.xlsx --sheet-name "売上" --randomize
```

### 3. テストモード

全テンプレートのサンプルファイルを一括生成します。

```bash
python excel_generator.py test
```

これにより、以下のファイルが生成されます：
- `test_employee.xlsx` - 従業員リスト
- `test_sales.xlsx` - 売上データ
- `test_project.xlsx` - プロジェクト工程表
- `test_budget.xlsx` - 予算表
- `test_inventory.xlsx` - 在庫リスト

## テンプレート一覧

| テンプレート名 | 説明 | 生成されるデータ |
|--------------|------|----------------|
| `employee` | 従業員リスト | 社員ID、氏名、部署、役職、入社日、年齢 |
| `sales` | 売上データ | 日付、製品名、地域、数量、単価、売上金額、担当者 |
| `project` | プロジェクト工程表 | タスクID、タスク名、担当者、開始日、終了日、工数、進捗率、ステータス |
| `budget` | 予算表 | 費目、部署、予算額、実績額、差異、差異率、備考 |
| `inventory` | 在庫リスト | 品目コード、品名、在庫数、単価、在庫金額、保管場所、最終更新日 |

## コマンドラインオプション

### `create` コマンド

新規Excelファイルを作成します。

```bash
python excel_generator.py create [オプション]
```

**オプション:**
- `--template <name>`: 使用するテンプレート名
- `--rows <num>`: 生成する行数（デフォルト: テンプレートごとに異なる）
- `--output <path>`, `-o <path>`: 出力ファイルパス（デフォルト: `output.xlsx`）
- `--sheet-name <name>`: シート名（デフォルト: テンプレート名）
- `--no-human-features`: 人間らしい特徴を適用しない
- `--intensity <level>`: 人間らしさの強度（`light`, `medium`, `heavy`）

### `modify` コマンド

既存のExcelファイルを修正します。

```bash
python excel_generator.py modify --file <path> [オプション]
```

**オプション:**
- `--file <path>`, `-f <path>`: 対象ファイルパス（必須）
- `--add-rows <num>`: 追加する行数
- `--template <name>`: 追加データのテンプレート
- `--sheet-name <name>`: 対象シート名（デフォルト: 最初のシート）
- `--randomize`: 人間らしい特徴を再適用
- `--no-human-features`: 人間らしい特徴を適用しない
- `--intensity <level>`: 人間らしさの強度
- `--output <path>`, `-o <path>`: 出力ファイルパス（指定しない場合は上書き）

### `test` コマンド

テストモードで全テンプレートのサンプルを生成します。

```bash
python excel_generator.py test
```

## 人間らしさの強度

`--intensity` オプションで、人間らしい特徴の適用度合いを調整できます。

- **`light`**: 控えめな変動（10%程度のセルに適用）
- **`medium`**: 中程度の変動（30%程度のセルに適用）※デフォルト
- **`heavy`**: 強めの変動（50%程度のセルに適用）

## 使用例

### シナリオ1: 売上レポートの作成

```bash
# 2024年の売上データ150件を生成
python excel_generator.py create --template sales --rows 150 --output 2024_sales_report.xlsx
```

### シナリオ2: 既存の従業員リストに新入社員を追加

```bash
# 既存のemployees.xlsxに20人の新入社員データを追加
python excel_generator.py modify --file employees.xlsx --add-rows 20 --template employee --output employees_updated.xlsx
```

### シナリオ3: きれいすぎるExcelを「人間らしく」する

```bash
# 機械生成されたクリーンなExcelに人間らしさを追加
python excel_generator.py modify --file clean_data.xlsx --randomize --intensity heavy
```

## Shadow生成との連携

このツールで生成したExcelファイルは、PoC2の`generate_shadow.py`スクリプトと完全に互換性があります。

```bash
# 1. Excelファイルを生成
cd PoC2_GitLab/tools
python excel_generator.py create --template sales --output ../../test_data.xlsx

# 2. Shadow生成（設計書リポジトリ側で実行）
cd ../scripts
python generate_shadow.py ../../test_data.xlsx
```

## モジュール構成

このツールは以下の3つのPythonモジュールで構成されています：

- **`excel_generator.py`**: メインツール（CLIインターフェース）
- **`human_like_features.py`**: 人間らしい特徴を追加するモジュール
- **`sample_data.py`**: ビジネス用サンプルデータ生成モジュール

## トラブルシューティング

### `ModuleNotFoundError: No module named 'openpyxl'`

openpyxlがインストールされていません。以下を実行してください：

```bash
pip install openpyxl
```

### 生成されたファイルが開けない

ファイルパスやアクセス権限を確認してください。また、既存ファイルを修正する場合は、そのファイルが他のプログラムで開かれていないことを確認してください。

### 人間らしい特徴が適用されていない

`--no-human-features` オプションが指定されていないか確認してください。また、`--intensity`を`heavy`に変更して、より顕著な効果を確認できます。

## ライセンス

このツールはPoC2プロジェクトの一部として提供されています。
