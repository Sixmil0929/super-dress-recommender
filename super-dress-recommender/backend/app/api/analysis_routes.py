from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from utils.analysis_handler import save_analysis_result, get_analysis_by_id, save_uploaded_image
from ai_module.Body_Analysis import process_image
from models.analysis_model import AnalysisResponse
from datetime import datetime 

import uuid # 生成随机文件名

router = APIRouter()


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


# 上传图片到ai端，存储ai端分析结果
@router.post("/upload", response_model=AnalysisResponse, summary="上传用户照片")
async def upload_analysis_photo(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        
        # file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg" # 根据参数file的文件名通过点号切片获取最后一部分(后缀名),若没有点，设置成jpg
        # unique_filename = f"{uuid.uuid4()}.{file_extension}" # 生成唯一文件名
        file_path = save_uploaded_image(file) # 获取保存的文件路径


        ai_result = process_image(file_path)
        if ai_result.get("status") == "error":
            raise HTTPException(status_code=400, detail=ai_result.get("msg", "AI分析失败"))

        # 组装数据
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat() # 数据时间
        final_data = {
            "analysis_id" : analysis_id,
            "user_id" : user_id,
            "timestamp" : timestamp,
            "image_path" : file_path,
            "ai_result" : ai_result
        }

        # 存储数据
        save_analysis_result(final_data)

        # 返回响应
        return AnalysisResponse(
            code=200,
            message="分析成功",
            data=final_data
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传或分析失败: {str(e)}")
