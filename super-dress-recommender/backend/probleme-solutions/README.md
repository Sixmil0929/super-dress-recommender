# 👕 智能服装推荐系统 - 后端开发指南 v2.0

> **文档维护人**：刘明钊
> **适用对象**：后端开发、AI工程师、前端开发

本文档旨在说明后端项目的最新模块化架构，以及后续开发、协作和测试的标准流程。

---

## 1. 📂 项目目录结构（核心）

我们采用了 **FastAPI 分层架构**。请大家严格遵守以下目录规范，不要随意在根目录新建 Python 文件。

```text
backend/                <-- 【重要】PyCharm请将此目录标记为 "Sources Root"
│
├── main.py             # 🚀 程序入口（启动文件，负责路由汇总）
├── requirements.txt    # 项目依赖包列表
│
├── ai_module/          # 🤖 【AI队友工作区】
│   ├── __init__.py
│   ├── Body_Analysis.py    # 你的核心分析代码放这里
│   ├── Body_ratio.py       # 你的计算逻辑放这里
│   └── Access_token.py     # 你的鉴权代码放这里
│
├── api/                # 🌐 【接口层】处理前端请求
│   ├── __init__.py
│   ├── user_routes.py      # 用户相关接口 (已完成)
│   └── analysis_routes.py  # (待新建) AI分析相关接口将写在这里
│
├── models/             # 📦 【数据模型层】定义数据格式 (Pydantic)
│   ├── __init__.py
│   └── user.py             # 定义 UserProfile 等数据结构
│
├── utils/              # 🔧 【工具层】通用功能
│   ├── __init__.py
│   └── json_handler.py     # 负责读写 JSON 数据库
│
└── data/               # 💾 【数据层】
    └── users.json          # 本地存储的用户数据
```

---

## 2. 🤝 后端与 AI 协作指南

### 📌 给 AI/后端 队友 的操作说明：

你的代码集成工作主要包含两个部分：**放置代码** 和 **编写接口**。

#### 第一步：迁移 AI 代码
请将你写好的 `Body_Analysis.py`, `Body_ratio.py`, `Access_token.py` 直接复制到 **`backend/ai_module/`** 文件夹下。
*   **注意**：确保这些代码里没有 `print()` 阻塞流程，最好是函数返回 `dict` 格式的数据。

#### 第二步：开发新的 API 接口
不要直接修改 `main.py`！请在 `backend/api/` 目录下新建一个文件，例如 `analysis_routes.py`。

**参考代码写法：**

```python
# backend/api/analysis_routes.py

from fastapi import APIRouter, UploadFile, File
# 导入你的AI模块
from ai_module import Body_Analysis 

router = APIRouter()

@router.post("/analyze")
async def analyze_photo(file: UploadFile = File(...)):
    # 1. 保存前端上传的图片到本地
    file_content = await file.read()
    # ... (写保存图片的逻辑) ...
    
    # 2. 调用你的 AI 函数
    result = Body_Analysis.process_image(image_path)
    
    # 3. 返回结果给前端
    return {"status": "success", "data": result}
```

#### 第三步：注册路由
写好新文件后，告诉我（刘明钊），或者你自己去 `main.py` 里加上一行注册代码：

```python
# main.py
from api import analysis_routes
app.include_router(analysis_routes.router, prefix="/api/analysis", tags=["AI分析"])
```

---

## 3. 🧪 如何进行独立测试（不依赖前端）

在前端页面没写好，或者前端报错无法判断是哪边问题时，请使用 **Swagger UI** 进行后端自测。

### 步骤 1：启动服务
在终端（Terminal）中运行：
```bash
python main.py
```
*如果看到 `Application startup complete` 代表启动成功。*

### 步骤 2：打开测试页面
在浏览器访问：👉 **http://127.0.0.1:8000/docs**

### 步骤 3：发送测试请求
1.  找到你要测的接口（例如绿色条目 `POST /api/user/profile`）。
2.  点击右上角的 **Try it out** 按钮。
3.  在 **Request body** 中输入测试的 JSON 数据。
4.  点击蓝色的 **Execute** 按钮。

### 步骤 4：查看结果
*   **Code 200**：表示成功，查看 Response body 里的数据是否正确。
*   **Code 422**：表示数据格式错误（比如年龄填了字符串），请检查输入。
*   **Code 500**：表示后端代码报错，请看终端里的具体报错信息。

---

## 4. ⚙️ 开发环境注意事项 (PyCharm 用户必看)

为了避免 PyCharm 代码爆红（提示找不到模块），请务必执行以下操作：

1.  在 PyCharm 左侧项目栏，右键点击 **`backend`** 文件夹。
2.  选择 **Mark Directory as** (将目录标记为) -> **Sources Root** (源代码根目录)。
3.  此时文件夹图标变蓝，所有导入报错将消失。

---

## 5. 📝 当前数据存储格式

`data/users.json` 自动维护以下格式，手动修改数据时请保持格式一致：

```json
[
  {
    "user_id": "user_001",
    "gender": "female",
    "age": 22,
    "height": 165.0,
    "weight": 50.0,
    "style_preferences": ["简约", "韩系"],
    "created_at": "2023-11-26 12:00:00",
    "analysis_records": [] 
  }
]
```
