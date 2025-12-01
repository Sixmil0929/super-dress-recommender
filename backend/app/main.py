from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import json
import os
from datetime import datetime
from typing import List

# === 1. 导入或定义模型 ===
try:
    from models.user_model import UserProfile
except ImportError:
    from pydantic import BaseModel


    class UserProfile(BaseModel):
        user_id: str
        gender: str
        age: int
        height: float
        weight: float
        style_preferences: List[str] = []

from api import analysis_routes

# === 2. 初始化配置 ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "users.json")

app = FastAPI(title="智能服装推荐系统 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 3. 工具函数 ===
def load_users() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_users(users: List[dict]):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


# === 4. 路由接口 ===

# 👇 新增：自动跳转，防止你看到 "Not Found"
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.post("/api/user/profile", summary="保存用户基本信息")
async def save_user_profile(profile: UserProfile):
    try:
        # 👇 修复：使用 model_dump() 消除黄色警告
        new_user_data = profile.model_dump()
        print(f"收到数据: {new_user_data}")

        users = load_users()
        new_user_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_exists = False
        for index, user in enumerate(users):
            if user["user_id"] == new_user_data["user_id"]:
                if "analysis_records" in user:
                    new_user_data["analysis_records"] = user["analysis_records"]
                else:
                    new_user_data["analysis_records"] = []
                users[index] = new_user_data
                user_exists = True
                break

        if not user_exists:
            new_user_data["analysis_records"] = []
            users.append(new_user_data)

        save_users(users)

        return {
            "status": "success",
            "message": "保存成功",
            "data": new_user_data
        }
    except Exception as e:
        print(f"错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    users = load_users()
    for user in users:
        if user["user_id"] == user_id:
            return {"status": "success", "data": user}
    return {"status": "error", "message": "用户不存在"}

app.include_router(analysis_routes.router, prefix="/api/analysis", tags=["AI分析结果"])

if __name__ == "__main__":
    import uvicorn
    print("正在启动服务...")
    print(f"数据文件路径: {DATA_FILE}")

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)