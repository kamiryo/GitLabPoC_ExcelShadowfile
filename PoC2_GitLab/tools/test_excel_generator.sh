#!/bin/bash
# test_excel_generator.sh
# WSL2/Ubuntu環境でExcelツールをテストするスクリプト

echo "========================================="
echo "Excel Generator Tool - Test Script"
echo "========================================="
echo ""

# カレントディレクトリを確認
echo "[1] Checking current directory..."
pwd
echo ""

# Pythonバージョン確認
echo "[2] Checking Python version..."
python3 --version
echo ""

# openpyxlがインストールされているか確認
echo "[3] Checking openpyxl installation..."
python3 -c "import openpyxl; print(f'openpyxl version: {openpyxl.__version__}')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "openpyxl is not installed. Installing..."
    pip3 install openpyxl
fi
echo ""

# ツールディレクトリに移動
cd PoC2_GitLab/tools || exit 1

# テストモード実行
echo "[4] Running test mode - generating all sample files..."
python3 excel_generator.py test
echo ""

# 生成されたファイルを確認
echo "[5] Checking generated files..."
ls -lh test_*.xlsx 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Test files generated successfully!"
else
    echo "✗ No test files found"
fi
echo ""

# 個別テスト: 売上データ生成
echo "[6] Testing: Create sales data (50 records)..."
python3 excel_generator.py create --template sales --rows 50 --output sample_sales.xlsx
echo ""

# 個別テスト: 従業員リスト生成
echo "[7] Testing: Create employee list (30 records)..."
python3 excel_generator.py create --template employee --rows 30 --output sample_employees.xlsx
echo ""

# 個別テスト: 既存ファイル修正
echo "[8] Testing: Modify existing file..."
python3 excel_generator.py modify --file sample_sales.xlsx --add-rows 20 --template sales --randomize --intensity heavy
echo ""

echo "========================================="
echo "Test completed!"
echo "========================================="
echo ""
echo "Generated files:"
ls -lh *.xlsx 2>/dev/null
