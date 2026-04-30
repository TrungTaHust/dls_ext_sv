import pandas as pd
import json
import subprocess
import shutil
import os
import glob

# ============================================================
# CẤU HÌNH — chỉnh sửa ở đây khi cần
# ============================================================

# Thư mục gốc của project DLSStats (chứa resources/data/)
PROJECT_DIR = r"C:\Users\123\Desktop\dls_ext_sv\DLSStats"

# Thư mục chứa build output và deploy target
BUILD_OUTPUT_DIR = os.path.join(PROJECT_DIR, "build", "production", "DLSStats")
DEPLOY_FRONTEND_DIR = r"C:\Users\123\Desktop\dls-ext"
DEPLOY_SERVER_DIR   = r"C:\Users\123\Desktop\dls_ext_sv"

# File Excel nguồn (đặt cùng thư mục với script này)
EXCEL_FILE = "dls.xlsx"
ID_SHEET   = "ID"

# Các sheet version cần xử lý — để None để tự động đọc tất cả sheet có tên là số
# Ví dụ: SHEET_NAMES = ['20262']  để chỉ xử lý 1 sheet
SHEET_NAMES = None  # None = tự động

# ============================================================

price_map = {
    861: 2800, 862: 2600, 863: 0, 864: 0,
    851: 2625, 852: 2440, 853: 2165, 854: 1975,
    841: 2460, 842: 2285, 843: 2030, 844: 1850,
    831: 2300, 832: 2130, 833: 1900, 834: 1730,
    821: 2145, 822: 1985, 823: 1770, 824: 1615,
    811: 1995, 812: 1850, 813: 1650, 814: 1500,
    801: 1850, 802: 1715, 803: 1535, 804: 1395,
    791: 1715, 792: 1585, 793: 1420, 794: 1290,
    781: 1585, 782: 1465, 783: 1315, 784: 1195,
    771: 1460, 772: 1345, 773: 1215, 774: 1100,
    761: 1340, 762: 1235, 763: 1115, 764: 1010,
    751: 1225, 752: 1130, 753: 1020, 754: 925,
    741: 1115, 742: 1030, 743: 935, 744: 840,
    731: 1015, 732: 935, 733: 850, 734: 765,
    721: 920, 722: 845, 723: 770, 724: 690,
    711: 830, 712: 760, 713: 695, 714: 620,
    701: 745, 702: 680, 703: 625, 704: 555,
    691: 665, 692: 605, 693: 555, 694: 495,
    681: 590, 682: 535, 683: 495, 684: 435,
    671: 520, 672: 470, 673: 435, 674: 385,
    661: 455, 662: 410, 663: 380, 664: 335,
    651: 400, 652: 355, 653: 335, 654: 290,
    641: 345, 642: 310, 643: 285, 644: 245,
    631: 300, 632: 265, 633: 245, 634: 210,
    621: 255, 622: 220, 623: 210, 624: 175,
    611: 215, 612: 185, 613: 175, 614: 145,
    601: 185, 602: 155, 603: 145, 604: 115,
    591: 155, 592: 130, 593: 120, 594: 90,
    581: 130, 582: 105, 583: 95, 584: 70,
    571: 110, 572: 85, 573: 75, 574: 55,
    561: 95, 562: 75, 563: 60, 564: 40,
    551: 85, 552: 60, 553: 50, 554: 25,
    541: 75, 542: 55, 543: 40, 544: 20,
    531: 70, 532: 50, 533: 35, 534: 15,
    521: 0, 522: 50, 523: 0, 524: 10
}

# ============================================================
# Đọc ID mapping
# ============================================================
df_id = pd.read_excel(EXCEL_FILE, sheet_name=ID_SHEET, engine='openpyxl')
df_id['full_name'] = df_id['full_name'].astype(str).str.replace(' ', '').str.lower()
full_name_to_id = dict(zip(df_id['full_name'], df_id['ID']))

# ============================================================
# Tự động phát hiện sheet version nếu SHEET_NAMES = None
# ============================================================
if SHEET_NAMES is None:
    xl = pd.ExcelFile(EXCEL_FILE, engine='openpyxl')
    SHEET_NAMES = [s for s in xl.sheet_names if s.isdigit()]
    SHEET_NAMES.sort()
    print(f"Tự động phát hiện {len(SHEET_NAMES)} sheet version: {SHEET_NAMES}")

# ============================================================
# Xử lý từng sheet, ghi ra data/<version>.txt
# ============================================================
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(output_dir, exist_ok=True)

for sheet in SHEET_NAMES:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, engine='openpyxl')
    df['first_name'] = df['first_name'].fillna("")
    df['last_name']  = df['last_name'].fillna("")
    df['full_name']  = (df['first_name'] + df['last_name']).str.replace(" ", "").str.lower()

    # Đánh dấu cầu thủ chưa update
    df['last_name'] = df.apply(
        lambda row: f"{row['last_name']} (old)" if row['updated'] == 0 else row['last_name'],
        axis=1
    )

    df['price']   = df['price_id'].map(price_map)
    df['id']      = df['full_name'].map(full_name_to_id)
    df['version'] = int(sheet)

    df.rename(columns={
        'first_name':  'fname',
        'last_name':   'lname',
        'nationality': 'nat',
        'position':    'pos',
        'rating':      'rate',
        'height':      'hgt',
        'speed':       'spe',
        'acceleration':'acc',
        'stamina':     'sta',
        'strength':    'str',
        'control':     'con',
        'passing':     'pas',
        'shooting':    'sho',
        'tackling':    'tac',
        'price':       'prc'
    }, inplace=True)

    # Báo cáo null
    drop_cols = [c for c in ['updated', 'pos_id', 'price_id', 'full_name'] if c in df.columns]
    df_out = df.drop(columns=drop_cols)
    null_summary = df_out.isnull().sum()
    total_null = null_summary.sum()
    if total_null > 0:
        print(f"\n⚠️  Sheet {sheet}: {total_null} giá trị null")
        print(null_summary[null_summary > 0])
    else:
        print(f"✅ Sheet {sheet}: {len(df_out)} records, không có null")

    # Ghi ra file .txt
    output_file = os.path.join(output_dir, f"{sheet}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(df_out.to_dict(orient='records'), f, ensure_ascii=False, indent=4)

# ============================================================
# Concat tất cả .txt → data.json
# ============================================================
all_records = []
for file in sorted(glob.glob(os.path.join(output_dir, "*.txt"))):
    with open(file, 'r', encoding='utf-8') as f:
        records = json.load(f)
        all_records.extend(records)

data_json_path = os.path.join(PROJECT_DIR, "resources", "data", "data.json")
os.makedirs(os.path.dirname(data_json_path), exist_ok=True)
with open(data_json_path, 'w', encoding='utf-8') as f:
    json.dump(all_records, f, ensure_ascii=False, indent=4)

print(f"\n✅ Tạo data.json thành công! Tổng: {len(all_records)} records → {data_json_path}")

# ============================================================
# Build + Deploy (bỏ comment nếu muốn chạy tự động)
# ============================================================
def run_git_push(directory, message="update"):
    os.chdir(directory)
    subprocess.run(["git", "add", "."], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", message], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "push"], check=True, stdout=subprocess.DEVNULL)
    print(f"✅ Git push: {directory}")

def build_and_deploy():
    os.chdir(PROJECT_DIR)
    print("🔨 Building...")
    subprocess.run(["sencha", "app", "clean"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["sencha", "app", "build"], check=True, stdout=subprocess.DEVNULL)

    # Copy build output sang deploy dir
    for root, dirs, files in os.walk(BUILD_OUTPUT_DIR):
        rel_path = os.path.relpath(root, BUILD_OUTPUT_DIR)
        dest_path = os.path.join(DEPLOY_FRONTEND_DIR, rel_path)
        os.makedirs(dest_path, exist_ok=True)
        for file in files:
            shutil.copy2(os.path.join(root, file), os.path.join(dest_path, file))
    print(f"✅ Copied build → {DEPLOY_FRONTEND_DIR}")

    run_git_push(DEPLOY_FRONTEND_DIR)
    run_git_push(DEPLOY_SERVER_DIR)

# build_and_deploy()  # ← bỏ comment dòng này để build + deploy tự động
