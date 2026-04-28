# Dress Select 智能穿搭推荐系统

项目现状已经统一为一套可运行链路：

- 前端：`frontend/`
- 后端：`api_server.py`
- 数据库：Docker + PostgreSQL + `init.sql`
- 图片资源：根目录 `images/`


## 当前目录结构

```text
.
├── README.md
├── 操作流程.md                # 给队友看的启动/初始化说明
├── api_server.py                # 当前唯一后端入口
├── docker_compose.yml           # PostgreSQL 容器配置
├── init.sql                     # 数据库初始化文件
├── images/                      # 服装图片资源（不提交到 Git）
├── frontend/                    # Vue + Vite 前端
├── backend/                     # 旧后端模块与用户路由代码
├── ai/                          # 体型分析相关代码与资料
├── docs/                        # 当前文档
│   ├── 脚本索引.md
│   └── archive/                 # 历史说明文档归档
├── scripts/                     # 研发脚本归类
│   ├── db_tools/                # 建库、修库、数据处理脚本
│   ├── debug/                   # 数据库查询、调试、检查脚本
│   └── research/                # 训练、评估、可视化、实验脚本
```

## 哪些文件是现在真的在用

### 运行主链路

- `api_server.py`
- `docker_compose.yml`
- `init.sql`
- `frontend/`
- `images/`

### 仍会被当前后端引用的旧模块

- `backend/app/api/user_routes.py`
- `backend/app/schemas/user_model.py`
- `backend/app/utils/user_handler.py`

说明：

- 当前后端统一由 `api_server.py` 启动
- 用户注册、登录、资料更新接口仍通过 `backend/app` 下的模块被 `api_server.py` 引入
- `backend/app/main.py` 已废弃并移除，不要再按旧方式启动

### AI 目录当前内容

`ai/` 目录主要保留体型分析相关代码：

- `Access_token.py`
  - 获取百度相关服务 token
- `Body_ratio.py`
  - 基于人体关键点做身材比例分析
- `Body_Analysis.py`
  - 综合分析入口，传入图片后输出分析结果

这部分目前不是网站主流程的运行依赖，但作为已有研究成果保留在仓库中。

### 研发资产

以下内容不参与日常启动，但保留给后续研究、排障或复现使用：

- `scripts/db_tools/`
- `scripts/debug/`
- `scripts/research/`
- `docs/archive/`
- `backend/probleme-solutions/`
- `frontend/problems/`

如果需要进一步了解这些脚本分别做什么，请看：

- [docs/脚本索引.md](/Users/a1/Desktop/GitHub项目/super-dress-recommender/docs/脚本索引.md)

## 当前数据库表

当前项目围绕 PostgreSQL 工作，核心表包括：

- `clothing_features`
  - 服装主数据表，存图片名、品牌、价格、性别、风格、颜色、季节、场景、向量等
- `users`
  - 用户表，当前手机号登录和资料信息都落在这里
- `user_item_behavior`
  - 用户行为明细表，记录停留时长、点赞、收藏、转发
- `item_engagement_stats`
  - 衣服全局统计表，记录总点赞数、总收藏数、总转发数、总浏览次数、总停留时长

## 如何运行

详细初始化和日常启动步骤请看：

- [操作流程.md](/Users/a1/Desktop/GitHub项目/super-dress-recommender/操作流程.md)

这里只保留最短版，方便快速建立全局印象：

1. 打开 Docker Desktop，确认 `Engine running`
2. 在项目根目录启动数据库

```bash
docker compose -f docker_compose.yml down -v
docker compose -f docker_compose.yml up -d
docker cp init.sql dress_select_db:/tmp/init.sql
docker exec -it dress_select_db psql -U postgres -d postgres -f /tmp/init.sql
```

3. 启动后端

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python api_server.py
```

Mac：

```bash
source .venv/bin/activate
python3 api_server.py
```

4. 启动前端

```bash
cd frontend
npm install
npm run dev
```
