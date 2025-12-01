from pydantic import BaseModel, Field
from typing import Dict, List, Any
from datetime import datetime

class AnalysisResult(BaseModel):
    """
    AI 分析结果的数据模型
    """
    user_id: str = Field(..., description="所属用户的ID")
    image_id: str = Field(..., description="关联的图片ID或文件名")
    
    # 这里的 ai_data 使用 Dict[str, Any] 是因为 AI 返回的结构可能很复杂
    # 如果结构固定，也可以定义更详细的 Model 嵌套
    ai_data: Dict[str, Any] = Field(..., description="AI模块返回的核心数据(体型、比例等)")
    
    # 下面这些字段由后端自动生成，前端不需要传
    result_id: str = Field(None, description="结果唯一标识(UUID)")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))