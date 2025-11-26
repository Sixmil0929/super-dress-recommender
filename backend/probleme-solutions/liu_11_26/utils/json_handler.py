import json
import os

# 获取当前文件所在目录的上上级目录作为基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "users.json")


def ensure_data_file():
    """确保数据目录和文件存在"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_all_users() -> list:
    """读取所有用户数据"""
    ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_user_data(new_user_dict: dict):
    """保存或更新用户数据"""
    users = load_all_users()

    # 检查是否已存在（如果存在则更新，不存在则追加）
    user_exists = False
    for index, user in enumerate(users):
        if user["user_id"] == new_user_dict["user_id"]:
            users[index] = new_user_dict  # 更新信息
            user_exists = True
            break

    if not user_exists:
        users.append(new_user_dict)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)