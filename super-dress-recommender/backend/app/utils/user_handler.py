import csv
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
USER_CSV = BASE_DIR / "data" / "users.csv"
FIELDNAMES = ["phone", "password", "user_id", "created_at", "gender", "age", "height", "weight", "body_type", "style_preferences", "analysis_records"]

def ensure_user_file():
    USER_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not USER_CSV.exists():
        with open(USER_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def load_all_users() -> list:
    ensure_user_file()
    users = []
    try:
        with open(USER_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 强制格式化数据，增强鲁棒性
                row["age"] = int(row["age"]) if row.get("age") else 0
                row["height"] = float(row["height"]) if row.get("height") else 0.0
                row["weight"] = float(row["weight"]) if row.get("weight") else 0.0
                row["style_preferences"] = json.loads(row["style_preferences"]) if row.get("style_preferences") else []
                row["analysis_records"] = json.loads(row["analysis_records"]) if row.get("analysis_records") else []
                users.append(row)
    except Exception as e:
        print(f"Critical Error loading users: {e}")
    return users

def get_user_by_phone(phone: str):
    users = load_all_users()
    for u in users:
        if str(u["phone"]) == str(phone):
            return u
    return None

def save_user_data(user_dict: dict):
    users = load_all_users()
    
    # 唯一性处理
    found = False
    for i, u in enumerate(users):
        if str(u["phone"]) == str(user_dict["phone"]):
            users[i] = user_dict
            found = True
            break
    if not found:
        users.append(user_dict)

    with open(USER_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for u in users:
            # 序列化复杂对象
            row_to_write = u.copy()
            row_to_write["style_preferences"] = json.dumps(u.get("style_preferences", []), ensure_ascii=False)
            row_to_write["analysis_records"] = json.dumps(u.get("analysis_records", []), ensure_ascii=False)
            writer.writerow(row_to_write)