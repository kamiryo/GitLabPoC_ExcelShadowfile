"""
sample_data.py

ビジネス用途のサンプルデータ生成モジュール
日本の業務で使用される現実的なデータを生成
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


# 日本の姓・名のサンプル
FAMILY_NAMES = [
    '鈴木', '田中', '佐藤', '高橋', '渡辺', '伊藤', '山本', '中村', '小林', '加藤',
    '吉田', '山田', '佐々木', '山口', '松本', '井上', '木村', '林', '斉藤', '清水'
]

FIRST_NAMES = [
    '太郎', '次郎', '三郎', '花子', '美咲', '健太', '翔太', '結衣', '陽菜', '葵',
    '大輔', '智子', '直樹', '美香', '裕也', '麻衣', '拓哉', '由美', '浩二', '真理子'
]

# 部署名
DEPARTMENTS = [
    '営業部', '開発部', '総務部', '人事部', '経理部', '企画部', 
    '製造部', 'マーケティング部', '品質管理部', 'カスタマーサポート部'
]

# 役職
POSITIONS = [
    '部長', '課長', '係長', '主任', '一般', 'リーダー', 'マネージャー', 'スタッフ'
]

# 製品名
PRODUCTS = [
    '製品A', '製品B', '製品C', 'サービスX', 'サービスY', 
    'システムα', 'システムβ', 'パッケージ1', 'パッケージ2', 'ソリューションZ'
]

# 都市名
CITIES = [
    '東京', '大阪', '名古屋', '福岡', '札幌', '仙台', '広島', '京都', '神戸', '横浜',
    '千葉', '埼玉', '川崎', '新潟', '静岡', '岡山', '熊本', '鹿児島', '金沢', '長野'
]

# プロジェクト工程
PROJECT_PHASES = [
    '要件定義', '基本設計', '詳細設計', '実装', '単体テスト', 
    '結合テスト', 'システムテスト', 'UAT', 'リリース準備', '本番移行'
]


def generate_employee_list(num_employees: int = 50, include_imperfections: bool = True) -> List[Dict[str, Any]]:
    """
    従業員リストのサンプルデータを生成
    
    Args:
        num_employees: 生成する従業員数
        include_imperfections: データの不完全さを含めるか
        
    Returns:
        従業員データのリスト
    """
    employees = []
    employee_id_start = 1001
    
    for i in range(num_employees):
        employee = {
            '社員ID': employee_id_start + i,
            '氏名': f"{random.choice(FAMILY_NAMES)} {random.choice(FIRST_NAMES)}",
            '部署': random.choice(DEPARTMENTS),
            '役職': random.choice(POSITIONS),
            '入社日': generate_random_date(2010, 2025),
            '年齢': random.randint(22, 65),
        }
        
        # 不完全さを追加（欠損値など）
        if include_imperfections and random.random() < 0.05:
            # 5%の確率で一部のデータを欠損させる
            field = random.choice(['役職', '年齢'])
            employee[field] = None
            
        employees.append(employee)
    
    return employees


def generate_sales_data(num_records: int = 100, include_imperfections: bool = True) -> List[Dict[str, Any]]:
    """
    売上データのサンプルを生成
    
    Args:
        num_records: 生成するレコード数
        include_imperfections: データの不完全さを含めるか
        
    Returns:
        売上データのリスト
    """
    sales_data = []
    
    for i in range(num_records):
        quantity = random.randint(1, 100)
        unit_price = random.randint(1000, 50000) * 10  # 切りの良い数字
        total = quantity * unit_price
        
        record = {
            '日付': generate_random_date(2024, 2026),
            '製品名': random.choice(PRODUCTS),
            '地域': random.choice(CITIES),
            '数量': quantity,
            '単価': unit_price,
            '売上金額': total,
            '担当者': f"{random.choice(FAMILY_NAMES)} {random.choice(FIRST_NAMES)}",
        }
        
        # 不完全さを追加
        if include_imperfections:
            # 10%の確率で数量や単価が手入力風になる（微妙にずれる）
            if random.random() < 0.1:
                record['数量'] = str(record['数量']) + '  '  # 余分な空白
            
            # 5%の確率で合計額が微妙に間違っている（手計算ミス）
            if random.random() < 0.05:
                record['売上金額'] = total + random.randint(-1000, 1000)
        
        sales_data.append(record)
    
    return sales_data


def generate_project_schedule(num_tasks: int = 30, include_imperfections: bool = True) -> List[Dict[str, Any]]:
    """
    プロジェクト工程表のサンプルデータを生成
    
    Args:
        num_tasks: 生成するタスク数
        include_imperfections: データの不完全さを含めるか
        
    Returns:
        工程表データのリスト
    """
    schedule = []
    start_date = datetime(2026, 2, 1)
    current_date = start_date
    
    for i in range(num_tasks):
        duration = random.randint(3, 30)  # 3～30日
        end_date = current_date + timedelta(days=duration)
        
        task = {
            'タスクID': f'T-{str(i+1).zfill(3)}',
            'タスク名': random.choice(PROJECT_PHASES),
            '担当者': f"{random.choice(FAMILY_NAMES)} {random.choice(FIRST_NAMES)}",
            '開始日': current_date.strftime('%Y/%m/%d'),
            '終了日': end_date.strftime('%Y/%m/%d'),
            '工数(人日)': random.randint(1, 20),
            '進捗率': random.choice([0, 10, 25, 50, 75, 100]),
            'ステータス': random.choice(['未着手', '進行中', '完了', '保留']),
        }
        
        # 不完全さを追加
        if include_imperfections:
            # 10%の確率で日付フォーマットが異なる
            if random.random() < 0.1:
                task['開始日'] = current_date.strftime('%Y-%m-%d')  # ハイフン区切り
            
            # 5%の確率でステータスが空欄
            if random.random() < 0.05:
                task['ステータス'] = ''
        
        schedule.append(task)
        
        # 次のタスクの開始日（少し重複させる）
        current_date = current_date + timedelta(days=random.randint(1, duration // 2))
    
    return schedule


def generate_budget_table(num_items: int = 20, include_imperfections: bool = True) -> List[Dict[str, Any]]:
    """
    予算表のサンプルデータを生成
    
    Args:
        num_items: 生成する予算項目数
        include_imperfections: データの不完全さを含めるか
        
    Returns:
        予算データのリスト
    """
    budget_items = []
    
    categories = ['人件費', '設備費', '通信費', '交通費', '交際費', '広告費', '研修費', '消耗品費', '外注費', '雑費']
    
    for i in range(num_items):
        budget = random.randint(100, 5000) * 1000  # 10万～500万
        actual = int(budget * random.uniform(0.7, 1.2))  # 予算の70%～120%
        variance = actual - budget
        variance_rate = (variance / budget) * 100 if budget != 0 else 0
        
        item = {
            '費目': random.choice(categories),
            '部署': random.choice(DEPARTMENTS),
            '予算額': budget,
            '実績額': actual,
            '差異': variance,
            '差異率(%)': round(variance_rate, 1),
            '備考': '',
        }
        
        # 不完全さを追加
        if include_imperfections:
            # 20%の確率で備考に情報を追加
            if random.random() < 0.2:
                item['備考'] = random.choice([
                    '要確認', '承認済', '調整中', '次月繰越', '削減予定', ''
                ])
            
            # 10%の確率で数値が文字列形式（カンマ区切り）
            if random.random() < 0.1:
                item['予算額'] = f'{budget:,}'
                item['実績額'] = f'{actual:,}'
        
        budget_items.append(item)
    
    return budget_items


def generate_inventory_list(num_items: int = 40, include_imperfections: bool = True) -> List[Dict[str, Any]]:
    """
    在庫リストのサンプルデータを生成
    
    Args:
        num_items: 生成する在庫アイテム数
        include_imperfections: データの不完全さを含めるか
        
    Returns:
        在庫データのリスト
    """
    inventory = []
    
    item_types = ['部品A', '部品B', '部品C', '材料X', '材料Y', '製品P', '製品Q', '消耗品']
    locations = ['倉庫A', '倉庫B', '倉庫C', '工場1', '工場2', '営業所']
    
    for i in range(num_items):
        item_id = f'ITM-{str(i+1).zfill(4)}'
        quantity = random.randint(0, 500)
        unit_price = random.randint(100, 10000)
        
        item = {
            '品目コード': item_id,
            '品名': random.choice(item_types),
            '在庫数': quantity,
            '単価': unit_price,
            '在庫金額': quantity * unit_price,
            '保管場所': random.choice(locations),
            '最終更新日': generate_random_date(2025, 2026),
        }
        
        # 不完全さを追加
        if include_imperfections:
            # 5%の確率で在庫金額の計算が合わない（手計算ミス）
            if random.random() < 0.05:
                item['在庫金額'] = item['在庫金額'] + random.randint(-5000, 5000)
            
            # 3%の確率で在庫数が負（データエラー）
            if random.random() < 0.03:
                item['在庫数'] = -random.randint(1, 10)
        
        inventory.append(item)
    
    return inventory


def generate_random_date(start_year: int, end_year: int) -> str:
    """
    ランダムな日付を生成（YYYY/MM/DD形式）
    
    Args:
        start_year: 開始年
        end_year: 終了年
        
    Returns:
        日付文字列
    """
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    
    random_date = start_date + timedelta(days=random_days)
    
    # 時々フォーマットを変える（人間らしさ）
    if random.random() < 0.1:
        return random_date.strftime('%Y-%m-%d')  # ハイフン区切り
    else:
        return random_date.strftime('%Y/%m/%d')  # スラッシュ区切り


def get_sample_data_generator(template_name: str):
    """
    テンプレート名に対応するデータ生成関数を取得
    
    Args:
        template_name: テンプレート名
        
    Returns:
        データ生成関数
    """
    generators = {
        'employee': generate_employee_list,
        'employee_list': generate_employee_list,
        'sales': generate_sales_data,
        'sales_data': generate_sales_data,
        'project': generate_project_schedule,
        'project_schedule': generate_project_schedule,
        'schedule': generate_project_schedule,
        'budget': generate_budget_table,
        'budget_table': generate_budget_table,
        'inventory': generate_inventory_list,
        'inventory_list': generate_inventory_list,
    }
    
    return generators.get(template_name.lower())
