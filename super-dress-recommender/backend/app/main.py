import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- 1. 环境路径修正 ---
# 将 app 目录加入系统路径，确保能正确导入同级目录下的 api、models 等模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from api import user_routes, analysis_routes

# 初始化应用
app = FastAPI(
    title="智能服装推荐系统后端 API",
    description="提供用户认证、AI身材分析及图片上传服务",
    version="1.0.0"
)

# --- 2. 跨域配置 (CORS) ---
# 允许前端开发环境(5173)及其他设备(*)调用后端接口
origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. 路由挂载 ---
# 注册各模块的接口路由
app.include_router(user_routes.router, prefix="/api/user", tags=["用户管理"])
app.include_router(analysis_routes.router, prefix="/api/analysis", tags=["AI 分析"])

# --- 4. 静态资源服务 ---
# 定位到 backend/data/uploads 目录，使前端可通过 URL 直接访问图片
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 定位到backend/
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads") # backend/data/uploads/
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- 5. 启动入口 ---
if __name__ == "__main__":
    # 0.0.0.0 支持局域网访问，reload 支持热更新
    # 运行文件之后，在浏览器访问 http://localhost:8000/docs 查看自动生成的API文档
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)