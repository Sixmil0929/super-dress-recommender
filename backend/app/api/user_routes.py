from fastapi import APIRouter, HTTPException
from models.user_model import UserProfile
from utils.json_handler import save_user_data, load_all_users

# 创建一个路由器
router = APIRouter()


@router.post("/profile", summary="保存/更新用户信息")
async def update_profile(profile: UserProfile):
    try:
        # 1. 将Pydantic模型转换为字典
        user_data = profile.dict()

        # 2. 调用工具函数保存
        save_user_data(user_data)

        return {
            "status": "success",
            "message": "用户信息保存成功",
            "data": {
                "user_id": profile.user_id,
                "saved_at": user_data["created_at"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.get("/{user_id}", summary="获取单个用户信息")
async def get_user(user_id: str):
    users = load_all_users()
    for user in users:
        if user["user_id"] == user_id:
            return {"status": "success", "data": user}

    raise HTTPException(status_code=404, detail="用户不存在")