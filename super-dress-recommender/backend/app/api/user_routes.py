from fastapi import APIRouter, HTTPException
from models.user_model import UserAuthRequest, UserProfileUpdate
from utils.user_handler import get_user_by_phone, save_user_data
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/register", summary="用户注册")
async def register(auth: UserAuthRequest):
    # 1. 唯一性检查
    if get_user_by_phone(auth.phone):
        # 返回 400 状态码，并给出明确信息，方便前端展示
        return {
            "code": 400, 
            "message": "该手机号已注册，请直接登录",
            "data": None
        }
    
    # 2. 创建用户对象（这里不再需要 nickname，完全以 phone 为准）
    new_user = {
        "phone": auth.phone,
        "password": auth.password,
        "user_id": str(uuid.uuid4()), # 内部保留一个UUID用于可能的扩展，但对外以phone为主
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gender": "",
        "age": 0,
        "height": 0.0,
        "weight": 0.0,
        "body_type": "",
        "style_preferences": [],
        "analysis_records": []
    }
    
    try:
        save_user_data(new_user)
        return {"code": 200, "message": "注册成功", "data": {"phone": auth.phone}}
    except Exception as e:
        return {"code": 500, "message": f"系统保存失败: {str(e)}"}

@router.post("/login", summary="用户登录")
async def login(auth: UserAuthRequest):
    user = get_user_by_phone(auth.phone)
    
    if not user:
        return {"code": 404, "message": "用户不存在，请先注册"}
    
    if user["password"] != auth.password:
        return {"code": 401, "message": "密码错误"}
    
    return {
        "code": 200, 
        "message": "登录成功", 
        "data": {
            "phone": user["phone"],
            "is_profile_completed": user["height"] > 0 # 逻辑：没填过身高的用户需要去完善资料
        }
    }

@router.post("/profile", summary="保存身体数据")
async def update_profile(profile_data: UserProfileUpdate):
    # 核心：现在从 Request Body 拿到的是 phone 了
    user = get_user_by_phone(profile_data.phone)
    
    if not user:
        # 鲁棒性：如果手机号不存在，报错
        return {"code": 404, "message": "未找到该手机号对应的用户，请重新登录"}

    # 更新数据
    user["gender"] = profile_data.gender
    user["age"] = profile_data.age
    user["height"] = profile_data.height
    user["weight"] = profile_data.weight
    user["body_type"] = profile_data.body_type
    user["style_preferences"] = profile_data.style

    # 存回 CSV
    save_user_data(user)

    return {
        "code": 200,
        "message": "资料已通过手机号匹配并成功更新"
    }