from fastapi import APIRouter, HTTPException
from models.analysis_model import AnalysisResult
from utils.analysis_handler import save_analysis_result, get_analysis_by_id

router = APIRouter()

@router.post("/save", summary="存储AI分析结果")
async def save_result(result: AnalysisResult):
    """
    接收 AI 分析结果并存储。
    前端/AI模块需要发送包含 user_id, image_id, ai_data 的 JSON。
    """
    try:
        saved_data = save_analysis_result(result)
        return {
            "status": "success",
            "message": "分析结果已归档",
            "data": {
                "result_id": saved_data['result_id'],
                "file_path": f"data/results/result_{saved_data['result_id']}.json"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"存储失败: {str(e)}")

@router.get("/{result_id}", summary="根据ID获取详细报告")
async def get_result(result_id: str):
    """
    前端传 result_id，后端返回对应的详细 JSON 数据用于渲染页面。
    """
    data = get_analysis_by_id(result_id)
    if not data:
        raise HTTPException(status_code=404, detail="找不到该分析结果")
    
    return {
        "status": "success",
        "data": data
    }