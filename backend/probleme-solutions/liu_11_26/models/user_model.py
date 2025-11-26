from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserProfile(BaseModel):
    """用户基础信息模型"""
    user_id: str = Field(..., description="用户唯一标识(如手机号或随机ID)")
    gender: str = Field(..., description="性别: male/female")
    age: int = Field(..., ge=1, le=120, description="年龄")
    height: float = Field(..., gt=0, description="身高(cm)")
    weight: float = Field(..., gt=0, description="体重(kg)")

    # 以下字段设为可选，注册时可能还没生成
    body_type: Optional[str] = Field(None, description="AI分析出的体型代码")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # 预留给后续功能的字段
    style_preferences: List[str] = Field(default=[], description="喜好风格")