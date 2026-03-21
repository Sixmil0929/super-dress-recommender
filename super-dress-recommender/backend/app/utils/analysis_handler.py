import json
import os
import uuid
import shutil

from fastapi import UploadFile
from models.analysis_model import BodyAnalysisResult
from utils.user_handler import load_all_users, save_user_data  # 复用之前的用户工具

# 定义存储目录: 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 定位到backend/
RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")
UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")    
    

# 储存分析结果 backend/data/results/result_{file_id}.json
def save_analysis_result(data : dict):
    """
    1. data : BodyAnalysisResult 实例
    2. 保存独立的 result_xxx.json 文件
    """
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    file_id = data.get("analysis_id", str(uuid.uuid4()))
    file_path = os.path.join(RESULTS_DIR, f"result_{file_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 存储用户上传图片到 backend/data/uploads/
# 返回保存的文件路径方便routes里面传递参数给ai端
def save_uploaded_image(file: UploadFile) -> str:
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg" # 根据参数file的文件名通过点号切片获取最后一部分(后缀名),若没有点，设置成jpg
    filename = f"{uuid.uuid4()}.{file_extension}" # 生成唯一文件名
    file_path = os.path.join(UPLOADS_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path



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
        # from  utils.json_handler import save_user_data
        # save_user_data(target_user)