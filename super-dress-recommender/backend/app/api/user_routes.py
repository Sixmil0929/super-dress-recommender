import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from models.user_model import UserAuthRequest, UserProfileUpdate
from utils.user_handler import load_all_users, save_user_data

router = APIRouter()


# --- 1. 注册接口 (对应 AuthView 的 "注册" 按钮) ---
@router.post("/register", summary="手机号注册")
async def register(auth_data: UserAuthRequest):
    users = load_all_users()

    # 检查手机号是否已被注册
    for user in users:
        if user.get("phone") == auth_data.phone:
            raise HTTPException(status_code=400, detail="该手机号已注册，请直接登录")

    # 创建新用户
    new_user_id = str(uuid.uuid4())
    new_user = {
        "user_id": new_user_id,
        "phone": auth_data.phone,
        "password": auth_data.password,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # 初始化身体数据为空
        "gender": None, "age": None, "height": 0, "weight": 0
    }

    save_user_data(new_user)

    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "user_id": new_user_id,
            "name": "新用户"  # 前端可能需要显示一个昵称
        }
    }


# --- 2. 登录接口 (对应 AuthView 的 "登录" 按钮) ---
@router.post("/login", summary="手机号登录")
async def login(auth_data: UserAuthRequest):
    users = load_all_users()

    for user in users:
        # 匹配手机号和密码
        if user.get("phone") == auth_data.phone and user.get("password") == auth_data.password:
            # 判断用户是否填写过身高体重 (用于前端判断是否跳转到 ProfileSetup)
            has_profile = user.get("height") is not None and user.get("height") > 0

            return {
                "code": 200,
                "message": "登录成功",
                "data": {
                    "user_id": user["user_id"],
                    "phone": user["phone"],
                    "is_profile_completed": has_profile
                }
            }

    raise HTTPException(status_code=400, detail="手机号或密码错误")


# --- 3. 完善资料接口 (对应 ProfileSetup.vue 的 "完成资料" 按钮) ---
@router.post("/profile", summary="保存身体数据")
async def update_profile(profile_data: UserProfileUpdate):
    users = load_all_users()
    target_user = None

    # 在数据库中查找用户
    for user in users:
        if user["user_id"] == profile_data.user_id:
            target_user = user
            break

    if not target_user:
        raise HTTPException(status_code=404, detail="找不到该用户，请重新登录")

    # 更新数据
    target_user["gender"] = profile_data.gender
    target_user["age"] = profile_data.age
    target_user["height"] = profile_data.height
    target_user["weight"] = profile_data.weight
    target_user["style_preferences"] = profile_data.style

    save_user_data(target_user)

    return {
        "code": 200,
        "message": "个人资料已更新，即将进入推荐页"
    }