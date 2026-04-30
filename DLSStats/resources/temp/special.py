import pandas as pd
import json
import os

# ============================================================
# CẤU HÌNH
# ============================================================

# Thư mục gốc của project DLSStats
PROJECT_DIR = r"C:\Users\123\Desktop\dls_ext_sv\DLSStats"

# File Excel nguồn (đặt cùng thư mục với script này)
EXCEL_FILE = "dls.xlsx"
SHEET_NAME = "Special"

# ============================================================

df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, engine='openpyxl')

# Đổi tên cột cho khớp với SpecialPlayer model
df.rename(columns={
    'first_name':   'fname',
    'last_name':    'lname',
    'nationality':  'nat',
    'position':     'pos',
    'rating':       'rate',
    'height':       'hgt',
    'speed':        'spe',
    'acceleration': 'acc',
    'stamina':      'sta',
    'strength':     'str',
    'control':      'con',
    'passing':      'pas',
    'shooting':     'sho',
    'tackling':     'tac',
}, inplace=True)

# Báo cáo null
null_summary = df.isnull().sum()
total_null = null_summary.sum()
if total_null > 0:
    print(f"⚠️  Sheet {SHEET_NAME}: {total_null} giá trị null")
    print(null_summary[null_summary > 0])
    print("\nCác bản ghi có null:")
    print(df[df.isnull().any(axis=1)])
else:
    print(f"✅ Sheet {SHEET_NAME}: {len(df)} records, không có null")

# Ghi ra resources/data/special.json
output_path = os.path.join(PROJECT_DIR, "resources", "data", "special.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(df.to_dict(orient='records'), f, ensure_ascii=False, indent=4)

print(f"✅ Tạo special.json thành công! Tổng: {len(df)} records → {output_path}")
