from pydantic import BaseModel, Field

class UserAuthRequest(BaseModel):
    # 注册和登录共用：只收手机号和密码
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    password: str = Field(..., min_length=6)

class UserProfileUpdate(BaseModel):
    # --- 重点：这里必须把 user_id 改为 phone ---
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="用户的唯一手机号")
    gender: str
    age: int
    height: float
    weight: float
    body_type: str = ""
    style: list[str] = []