import json
import os
import uuid
from datetime import datetime
from utils.json_handler import load_all_users, save_user_data # 复用之前的用户工具

# 定义存储目录: backend/data/results/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")

def ensure_results_dir():
    """确保结果文件夹存在"""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

def save_analysis_result(data_model):
    """
    1. 生成唯一ID
    2. 保存独立的 result_xxx.json 文件
    3. 把这个 ID 记录到用户的 analysis_records 列表中
    """
    ensure_results_dir()
    
    # 1. 生成唯一 ID (UUID)
    result_id = str(uuid.uuid4())
    
    # 2. 准备要写入的数据
    final_data = data_model.dict()
    final_data['result_id'] = result_id
    # 如果没时间戳，补一个
    if not final_data.get('created_at'):
        final_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 3. 写入独立文件
    file_path = os.path.join(RESULTS_DIR, f"result_{result_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
    
    # 4. 【关键】关联到用户 (更新 users.json)
    # 这一步是为了让用户能看到自己的历史记录列表
    _link_result_to_user(final_data['user_id'], result_id, final_data['created_at'])

    return final_data

def get_analysis_by_id(result_id: str):
    """读取单个结果文件"""
    file_path = os.path.join(RESULTS_DIR, f"result_{result_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def _link_result_to_user(user_id, result_id, created_at):
    """辅助函数：将结果ID追加到用户的记录里"""
    users = load_all_users() # 复用之前的工具
    target_user = None
    
    for user in users:
        if user['user_id'] == user_id:
            target_user = user
            break
    
    if target_user:
        # 确保有这个字段
        if "analysis_records" not in target_user:
            target_user["analysis_records"] = []
            
        # 只存简略信息，不存整个大结果
        record_summary = {
            "result_id": result_id,
            "created_at": created_at
        }
        target_user["analysis_records"].append(record_summary)
        
        # 保存回 users.json
        # 注意：这里我们调用 save_user_data 会触发全量写入，
        # 在真实高并发场景下不推荐，但在 json 文件存储模式下只能这样。
        from utils.json_handler import save_user_data
        save_user_data(target_user)