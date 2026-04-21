# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# import psycopg2

# app = FastAPI(title="V7.0 智能穿搭推荐引擎")

# # ==========================================
# # 1. 跨域防护盾 
# # ==========================================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ==========================================
# # 2. 静态图片服务器
# # ==========================================
# # ⚠️ 这里我用了你之前发给我的路径，如果图片裂开，请检查是不是 D:\dress_recommender\P4_Dataset\images
# IMG_DIR = r"D:\dress_recommender\images\images"
# app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")

# # ==========================================
# # 3. 定义前端传过来的数据格式
# # ==========================================
# class QuestionnaireRequest(BaseModel):
#     gender: str                 
#     scene: str                  
#     style: list[str]            
#     preferred_colors: list[str] 

# # ==========================================
# # 4. 问卷推荐接口 (生成搭配按钮)
# # ==========================================
# @app.post("/api/recommend_by_survey")
# def recommend_by_survey(req: QuestionnaireRequest):
#     print(f"📡 收到问卷！场景:{req.scene}, 风格:{req.style}, 颜色:{req.preferred_colors}")
    
#     # 临时强行组 CP 测试版，让你立刻在前端看到上下装双拼效果！
#     fake_outfits = [
#         {
#             "type": "combo",
#             "score": 0.98,
#             "top": {"filename": "img_0001.jpg", "category": "上装", "color": "white"},
#             "bottom": {"filename": "img_0002.jpg", "category": "下装", "color": "black"}
#         }
#     ]
    
#     return {
#         "status": "success",
#         "data": {
#             "outfits": fake_outfits
#         }
#     }

# # ==========================================
# # 5. 首页专供：随机盲抽瀑布流
# # ==========================================
# # ==========================================
# # 5. 首页专供：随机盲抽瀑布流 (带真实价格版)
# # ==========================================
# @app.get("/api/random_looks")
# def get_random_looks(limit: int = 12):
#     try:
#         conn = psycopg2.connect(
#             host="localhost", database="postgres", user="postgres", password="123456", port="5432"
#         )
#         cursor = conn.cursor()

#         # 🚀 极其关键：把 price 加进 SELECT 语句里！
#         sql_query = """
#             SELECT filename, item_category, color, brand, price
#             FROM clothing_features 
#             ORDER BY RANDOM() 
#             LIMIT %s;
#         """
#         cursor.execute(sql_query, (limit,))
#         rows = cursor.fetchall()
        
#         random_items = []
#         for row in rows:
#             random_items.append({
#                 "filename": str(row[0]).strip(), # 强行去空格，保证 "img_0001.jpg" 极其纯净
#                 "category": row[1],
#                 "color": row[2],
#                 "brand": row[3],
#                 "price": row[4]                  # 👈 真实价格拿到手了！
#             })
            
#         cursor.close()
#         conn.close()

#         return {"status": "success", "data": random_items}

#     except Exception as e:
#         print("首页抽盲盒失败：", e)
#         return {"status": "error", "message": str(e)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

# import os
# import json
# import torch
# import torch.nn.functional as F
# import clip
# import psycopg2
# import numpy as np
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel

# app = FastAPI(title="V7.0 审美碰撞推荐引擎")

# # ==========================================
# # 0. 核心模型初始化 (全局加载，只载一次)
# # ==========================================
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"🚀 正在加载 CLIP 核心模型至 {device}...")
# clip_model, _ = clip.load("ViT-L/14", device=device)
# clip_model.eval()

# # ==========================================
# # 1. 跨域防护盾 
# # ==========================================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ==========================================
# # 2. 静态图片服务器
# # ==========================================
# IMG_DIR = r"D:\dress_recommender\images\images"
# app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")

# # ==========================================
# # 3. 数据模型
# # ==========================================
# class QuestionnaireRequest(BaseModel):
#     gender: str                 
#     scene: str                  
#     style: list[str]            
#     preferred_colors: list[str]
#     season: str = "" 

# # ==========================================
# # 4. MMR 多样性算法
# # ==========================================
# def apply_mmr(items, top_n=15, diversity_weight=0.5):
#     if not items: return []
#     selected_items = []
#     candidates = items.copy()
    
#     best_idx = max(range(len(candidates)), key=lambda i: candidates[i]['semantic_score'])
#     selected_items.append(candidates.pop(best_idx))
    
#     while len(selected_items) < top_n and candidates:
#         best_mmr_score = -float('inf')
#         best_candidate_idx = -1
#         selected_vecs = torch.stack([x['vector'] for x in selected_items])
        
#         for i, cand in enumerate(candidates):
#             cand_vec = cand['vector']
#             sims = torch.matmul(selected_vecs, cand_vec)
#             max_sim = sims.max().item()
#             mmr_score = (1 - diversity_weight) * cand['semantic_score'] - (diversity_weight * max_sim)
#             if mmr_score > best_mmr_score:
#                 best_mmr_score = mmr_score
#                 best_candidate_idx = i
#         selected_items.append(candidates.pop(best_candidate_idx))
#     return selected_items

# # ==========================================
# # 5. 核心：V7.0 结构化推荐算法接口
# # ==========================================
# @app.post("/api/recommend_by_survey")
# async def recommend_by_survey(req: QuestionnaireRequest):
#     print(f"📡 收到问卷！正在进行审美碰撞...")
#     try:
#         # --- A. 语义向量化 ---
#         vibe_words = [req.scene] + req.style + req.preferred_colors
#         vibe_query = f"A high-end fashion outfit for {', '.join(vibe_words)}"
        
#         with torch.no_grad():
#             text_tokens = clip.tokenize([vibe_query]).to(device)
#             query_vector = clip_model.encode_text(text_tokens).float()
#             query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

#         # --- B. 数据库连接 ---
#         conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
#         cursor = conn.cursor()
        
#         # --- C. 硬筛选 + 语义初筛 ---
#         cursor.execute("SELECT filename, brand, price, item_category, super_vector::text FROM clothing_features;")
#         rows = cursor.fetchall()
        
#         tops, bottoms, ops = [], [], []
#         for row in rows:
#             fname, brand, price, cat, vec_str = row
#             vec_list = json.loads(vec_str)
#             tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
#             score = torch.matmul(tensor_vec, query_vector).item()
            
#             item = {"filename": fname, "brand": brand, "price": price, "vector": tensor_vec, "semantic_score": score}
            
#             if cat == "top": tops.append(item)
#             elif cat == "bottom": bottoms.append(item)
#             elif cat == "one_piece": ops.append(item)

#         # --- D. 审美碰撞逻辑 ---
#         final_outfits = []
        
#         if tops and bottoms:
#             best_tops = apply_mmr(tops, top_n=10)
#             best_bottoms = apply_mmr(bottoms, top_n=10)
            
#             for t in best_tops:
#                 for b in best_bottoms:
#                     raw_harmony = torch.matmul(t["vector"], b["vector"]).item()
#                     harmony_score = float(np.exp(-((raw_harmony - 0.6) ** 2) / (2 * 0.2 ** 2)))
#                     total_score = (t["semantic_score"] * 0.4) + (b["semantic_score"] * 0.4) + (harmony_score * 0.2)
                    
#                     final_outfits.append({
#                         "type": "combo",
#                         "score": total_score,
#                         "top": {"filename": t["filename"], "brand": t["brand"], "price": f"¥{int(t['price'])}", "category": "上装"},
#                         "bottom": {"filename": b["filename"], "brand": b["brand"], "price": f"¥{int(b['price'])}", "category": "下装"}
#                     })

#         if ops:
#             best_ops = apply_mmr(ops, top_n=5)
#             for op in best_ops:
#                 final_outfits.append({
#                     "type": "single",
#                     "score": op["semantic_score"],
#                     "item": {"filename": op["filename"], "brand": op["brand"], "price": f"¥{int(op['price'])}", "category": "连衣裙"}
#                 })

#         # --- 🚀 E. 结果择优 (新增频率锁，禁止重复展示) ---
#         final_outfits.sort(key=lambda x: x["score"], reverse=True)
        
#         # 👑 新增：查水表黑名单，记录已经选中的文件名
#         usage_count = {} 
#         results = []
        
#         for outfit in final_outfits:
#             # 逻辑：如果是套装，检查上衣和下衣是否都还没出过场
#             if outfit["type"] == "combo":
#                 t_fname = outfit["top"]["filename"]
#                 b_fname = outfit["bottom"]["filename"]
#                 if t_fname in usage_count or b_fname in usage_count:
#                     continue # 有一个出过场了，这套就不要了
#                 usage_count[t_fname] = 1
#                 usage_count[b_fname] = 1
#             # 如果是单件，检查这件是否出过场
#             else:
#                 item_fname = outfit["item"]["filename"]
#                 if item_fname in usage_count:
#                     continue
#                 usage_count[item_fname] = 1
                
#             results.append(outfit)
            
#             # 凑够 4 套就收工
#             if len(results) >= 4:
#                 break

#         cursor.close()
#         conn.close()
#         return {"status": "success", "data": {"outfits": results}}

#     except Exception as e:
#         print(f"❌ 推荐失败: {e}")
#         return {"status": "error", "message": str(e)}

# # ==========================================
# # 6. 首页专供：随机盲抽瀑布流
# # ==========================================
# @app.get("/api/random_looks")
# def get_random_looks(limit: int = 12):
#     try:
#         conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
#         cursor = conn.cursor()
#         sql_query = "SELECT filename, item_category, color, brand, price FROM clothing_features ORDER BY RANDOM() LIMIT %s;"
#         cursor.execute(sql_query, (limit,))
#         rows = cursor.fetchall()
        
#         random_items = []
#         for row in rows:
#             random_items.append({
#                 "filename": str(row[0]).strip(),
#                 "category": row[1],
#                 "color": row[2],
#                 "brand": row[3],
#                 "price": row[4]
#             })
#         cursor.close()
#         conn.close()
#         return {"status": "success", "data": random_items}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# import os
# import json
# import torch
# import torch.nn.functional as F
# import clip
# import psycopg2
# import numpy as np
# import re
# import random
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel

# app = FastAPI(title="V7.0 审美碰撞+物理隔离+随机盲抽 终极版")

# # ==========================================
# # 0. 核心初始化 (CLIP 模型全局热启动)
# # ==========================================
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"🚀 正在加载 CLIP 核心模型至 {device}...")
# clip_model, _ = clip.load("ViT-L/14", device=device)
# clip_model.eval()

# # 1. 跨域防护与静态资源挂载
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
# IMG_DIR = r"D:\dress_recommender\images\images"
# app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")

# # ==========================================
# # 2. 核心辅助工具
# # ==========================================
# def get_img_num(filename):
#     """从文件名提取数字，用于 401-480 的物理隔离"""
#     match = re.search(r'img_(\d+)', filename)
#     return int(match.group(1)) if match else 0

# def apply_mmr(items, top_n=15, diversity_weight=0.5):
#     """MMR 算法：保证推荐结果的‘多样性’，拒绝长得一模一样的衣服"""
#     if not items: return []
#     selected_items = []
#     candidates = items.copy()
#     best_idx = max(range(len(candidates)), key=lambda i: candidates[i]['semantic_score'])
#     selected_items.append(candidates.pop(best_idx))
#     while len(selected_items) < top_n and candidates:
#         best_mmr_score = -float('inf')
#         best_candidate_idx = -1
#         selected_vecs = torch.stack([x['vector'] for x in selected_items])
#         for i, cand in enumerate(candidates):
#             cand_vec = cand['vector']
#             sims = torch.matmul(selected_vecs, cand_vec)
#             max_sim = sims.max().item()
#             mmr_score = (1 - diversity_weight) * cand['semantic_score'] - (diversity_weight * max_sim)
#             if mmr_score > best_mmr_score:
#                 best_mmr_score = mmr_score
#                 best_candidate_idx = i
#         if best_candidate_idx == -1: break
#         selected_items.append(candidates.pop(best_candidate_idx))
#     return selected_items

# class QuestionnaireRequest(BaseModel):
#     gender: str
#     scene: str
#     style: list[str]
#     preferred_colors: list[str]
#     season: str 

# # ==========================================
# # 3. 核心 API：推荐页面 (物理隔离 + AI 审美)
# # ==========================================
# @app.post("/api/recommend_by_survey")
# async def recommend_v7_fusion(req: QuestionnaireRequest):
#     print(f"📡 接收任务：{req.gender} | {req.season} | {req.scene}")
#     try:
#         # A. 语义向量化
#         vibe_words = [req.scene] + req.style + req.preferred_colors
#         vibe_query = f"A high-end fashion outfit for {', '.join(vibe_words)}"
#         with torch.no_grad():
#             text_tokens = clip.tokenize([vibe_query]).to(device)
#             query_vector = clip_model.encode_text(text_tokens).float()
#             query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

#         # B. 数据库检索
#         conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
#         cursor = conn.cursor()
#         cursor.execute("SELECT filename, brand, price, item_category, super_vector::text FROM clothing_features WHERE season ILIKE %s", (f"%{req.season}%",))
#         rows = cursor.fetchall()
        
#         tops, bottoms, ops = [], [], []
#         for row in rows:
#             fname, brand, price, cat, vec_str = row
#             img_num = get_img_num(fname)
#             is_in_female_zone = (401 <= img_num <= 480)

#             # 🛡️ 物理红线：如果是男生，直接抹除禁区和所有裙装
#             if req.gender == "male":
#                 if is_in_female_zone: continue
#                 if cat == "one_piece" or "裙" in fname or "skirt" in fname: continue
            
#             # C. 智能评分 (AI 审美)
#             vec_list = json.loads(vec_str)
#             tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
#             base_score = torch.matmul(tensor_vec, query_vector).item()
            
#             # 🌟 提权逻辑：如果是女生，给禁区衣服加 Buff
#             if req.gender == "female" and is_in_female_zone:
#                 base_score += 0.35 
            
#             item = {"filename": fname, "brand": brand, "price": price, "vector": tensor_vec, "semantic_score": base_score}
#             if cat == "top": tops.append(item)
#             elif cat == "bottom": bottoms.append(item)
#             elif cat == "one_piece": ops.append(item)

#         # D. MMR 多样性初筛
#         diverse_tops = apply_mmr(tops, top_n=15)
#         diverse_bottoms = apply_mmr(bottoms, top_n=15)

#         # E. 审美碰撞 (Harmony Score)
#         all_combos = []
#         for t in diverse_tops:
#             for b in diverse_bottoms:
#                 harmony = torch.matmul(t["vector"], b["vector"]).item()
#                 harmony_score = float(np.exp(-((harmony - 0.6) ** 2) / (2 * 0.2 ** 2)))
#                 total_score = (t["semantic_score"] * 0.45) + (b["semantic_score"] * 0.45) + (harmony_score * 0.1)
#                 all_combos.append({"type": "combo", "score": total_score, "top": t, "bottom": b})

#         all_combos.sort(key=lambda x: x["score"], reverse=True)
#         usage_count, final_results = {}, []

#         # F. 组合筛选 (带频率锁)
#         for combo in all_combos:
#             t_name, b_name = combo["top"]["filename"], combo["bottom"]["filename"]
#             if usage_count.get(t_name, 0) >= 1 or usage_count.get(b_name, 0) >= 1: continue
#             usage_count[t_name] = 1; usage_count[b_name] = 1
#             final_results.append({
#                 "type": "combo", "score": combo["score"],
#                 "top": {"filename": t_name, "brand": combo["top"]["brand"], "price": f"¥{int(combo['top']['price'])}"},
#                 "bottom": {"filename": b_name, "brand": combo["bottom"]["brand"], "price": f"¥{int(combo['bottom']['price'])}"}
#             })
#             if len(final_results) >= 4: break

#         # 补齐连衣裙
#         if len(final_results) < 4 and ops:
#             best_ops = apply_mmr(ops, top_n=5)
#             for op in best_ops:
#                 if usage_count.get(op["filename"], 0) < 1:
#                     final_results.append({
#                         "type": "single", "score": op["semantic_score"],
#                         "item": {"filename": op["filename"], "brand": op["brand"], "price": f"¥{int(op['price'])}", "category": "推荐"}
#                     })
#                 if len(final_results) >= 4: break

#         cursor.close(); conn.close()
#         return {"status": "success", "data": {"outfits": final_results}}
#     except Exception as e:
#         print(f"💥 崩溃了: {e}")
#         return {"status": "error", "message": str(e)}

# # ==========================================
# # 4. 核心 API：首页瀑布流 (随机盲抽)
# # ==========================================
# @app.get("/api/random_looks")
# def get_random_looks(limit: int = 12):
#     print("🎲 正在为首页抽盲盒...")
#     try:
#         conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
#         cursor = conn.cursor()
        
#         # 🚀 真实价格、真实品牌、真实品类，全部带上！
#         sql_query = """
#             SELECT filename, item_category, color, brand, price 
#             FROM clothing_features 
#             ORDER BY RANDOM() 
#             LIMIT %s;
#         """
#         cursor.execute(sql_query, (limit,))
#         rows = cursor.fetchall()
        
#         random_items = []
#         for row in rows:
#             random_items.append({
#                 "filename": str(row[0]).strip(),
#                 "category": row[1],
#                 "color": row[2],
#                 "brand": row[3],
#                 "price": f"¥{int(row[4])}" if row[4] else "¥199"
#             })
            
#         cursor.close()
#         conn.close()
#         return {"status": "success", "data": random_items}

#     except Exception as e:
#         print("❌ 首页随机盲抽失败：", e)
#         return {"status": "error", "message": str(e)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


import os
import json
import os
import sys
import torch
import psycopg2
import numpy as np
import re
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_APP_DIR = os.path.join(BASE_DIR, "super-dress-recommender", "backend", "app")
if BACKEND_APP_DIR not in sys.path:
    sys.path.append(BACKEND_APP_DIR)

from api import user_routes

app = FastAPI(title="V8.0 漏斗架构：SQL硬召回 + 审美排序")

# ==========================================
# 1. 跨域防护与静态资源
# ==========================================
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
IMG_DIR = os.path.join(BASE_DIR, "images")
app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")
app.include_router(user_routes.router, prefix="/api/user", tags=["用户管理"])

# ==========================================
# 2. 核心辅助工具
# ==========================================
def get_img_num(filename):
    match = re.search(r'img_(\d+)', filename)
    return int(match.group(1)) if match else 0

def apply_mmr(items, top_n=15, diversity_weight=0.5):
    """MMR 算法：在满足硬标签的衣服里，挑选出风格最不一样的"""
    if not items: return []
    selected_items = []
    candidates = items.copy()
    
    # 既然大家分数都一样(都满足SQL)，第一名随便挑个基础分最高的
    best_idx = max(range(len(candidates)), key=lambda i: candidates[i]['base_score'])
    selected_items.append(candidates.pop(best_idx))
    
    while len(selected_items) < top_n and candidates:
        best_mmr_score = -float('inf')
        best_candidate_idx = -1
        selected_vecs = torch.stack([x['vector'] for x in selected_items])
        
        for i, cand in enumerate(candidates):
            cand_vec = cand['vector']
            sims = torch.matmul(selected_vecs, cand_vec)
            max_sim = sims.max().item()
            # 基础分 - 相似度惩罚 (越独特越容易被选中)
            mmr_score = (1 - diversity_weight) * cand['base_score'] - (diversity_weight * max_sim)
            
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_candidate_idx = i
                
        if best_candidate_idx == -1: break
        selected_items.append(candidates.pop(best_candidate_idx))
        
    return selected_items

class QuestionnaireRequest(BaseModel):
    gender: Optional[str] = ""
    season: Optional[str] = ""
    scene: Optional[str] = ""
    style: Optional[List[str]] = []
    preferred_colors: Optional[List[str]] = []

# ==========================================
# 3. 核心 API：漏斗架构推荐
# ==========================================
@app.post("/api/recommend_by_survey")
async def recommend_v8_funnel(req: QuestionnaireRequest):
    print(f"📡 接收任务：{req.gender} | {req.season} | {req.scene} | {req.style} | {req.preferred_colors}")
    try:
        conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
        cursor = conn.cursor()
        conditions = []
        params = []

        if req.gender:
            g = req.gender.lower()
            if g == "male":
                # 男生：只看纯男装和中性款
                conditions.append("LOWER(gender) IN ('male', 'unisex')")
            elif g == "female":
                # 女生：只看纯女装和中性款
                conditions.append("LOWER(gender) IN ('female', 'unisex')")

        # 1. 季节 (必命中)
        if req.season:
            conditions.append("season ILIKE %s")
            params.append(f"%{req.season}%")

        # 2. 场景 (必命中)
        if req.scene:
            conditions.append("scene ILIKE %s")
            params.append(f"%{req.scene}%")
            
        # 3. 风格 (遍历前端传来的所有风格)
        if req.style and len(req.style) > 0:
            for s in req.style:
                conditions.append("style ILIKE %s")
                params.append(f"%{s}%")
            
        # 4. 颜色 (遍历所有颜色)
        if req.preferred_colors and len(req.preferred_colors) > 0:
            for c in req.preferred_colors:
                conditions.append("color ILIKE %s")
                params.append(f"%{c}%")

        # 组合 SQL
        sql_query = f"""
            SELECT filename, brand, price, item_category, super_vector::text 
            FROM clothing_features 
        """
        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)
        print(f"🔍 终极严苛 SQL: {sql_query}")
        cursor.execute(sql_query, params)
        rows = cursor.fetchall()
        print(f"📦 筛选结果: 只有 {len(rows)} 件衣服经受住了所有标签的考验！")
        tops, bottoms, ops = [], [], []
        for row in rows:
            fname, brand, price, cat, vec_str = row
            img_num = get_img_num(fname)
            is_in_female_zone = (401 <= img_num <= 480)

            if req.gender == "male":
                if is_in_female_zone: continue
                if cat == "one_piece" or "裙" in fname or "skirt" in fname: continue
            
            # 基础分设定：所有能通过 SQL 筛选的衣服，说明都非常符合用户需求，底分给 1.0
            base_score = 1.0
            if req.gender == "female" and is_in_female_zone:
                base_score += 0.5 
            
            vec_list = json.loads(vec_str)
            tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
            item = {"filename": fname, "brand": brand, "price": price, "vector": tensor_vec, "base_score": base_score}
            
            if cat == "top": tops.append(item)
            elif cat == "bottom": bottoms.append(item)
            elif cat == "one_piece": ops.append(item)

        # 如果连 4 套都凑不齐，说明数据库标签太少了！这就是你要测试的痛点。
        if not tops and not ops:
            print("⚠️ 警告：当前标签组合在数据库中找不到任何衣服！")
        random.shuffle(tops)
        random.shuffle(bottoms)
        
        diverse_tops = tops[:15]
        diverse_bottoms = bottoms[:15]

        all_combos = []
        for t in diverse_tops:
            for b in diverse_bottoms:
                random_score = random.random() 
                
                all_combos.append({
                    "type": "combo", 
                    "score": random_score,
                    "top": t, 
                    "bottom": b
                })

        all_combos.sort(key=lambda x: x["score"], reverse=True)
        
        usage_count, final_results = {}, []

        for combo in all_combos:
            t_name, b_name = combo["top"]["filename"], combo["bottom"]["filename"]
            if usage_count.get(t_name, 0) >= 1 or usage_count.get(b_name, 0) >= 1: continue
            usage_count[t_name] = 1; usage_count[b_name] = 1
            
            final_results.append({
                "type": "combo", 
                "score": combo["score"], # 这里传给前端的只是个随机数，无所谓了
                "top": {"filename": t_name, "brand": combo["top"]["brand"], "price": f"¥{int(combo['top']['price'])}"},
                "bottom": {"filename": b_name, "brand": combo["bottom"]["brand"], "price": f"¥{int(combo['bottom']['price'])}"}
            })
            if len(final_results) >= 4: break

        if len(final_results) < 4 and ops:
            best_ops = apply_mmr(ops, top_n=15) 
            random.shuffle(best_ops) 
            
            for op in best_ops:
                if usage_count.get(op["filename"], 0) < 1:
                    usage_count[op["filename"]] = 1
                    final_results.append({
                        "type": "single", "score": op["base_score"],
                        "item": {"filename": op["filename"], "brand": op["brand"], "price": f"¥{int(op['price'])}", "category": "严格标签匹配"}
                    })
                if len(final_results) >= 4: break

        if len(final_results) < 4 and ops:
            best_ops = apply_mmr(ops, top_n=15) 
            random.shuffle(best_ops)
            
            for op in best_ops:
                if usage_count.get(op["filename"], 0) < 1:
                    usage_count[op["filename"]] = 1
                    final_results.append({
                        "type": "single", "score": op["base_score"],
                        "item": {"filename": op["filename"], "brand": op["brand"], "price": f"¥{int(op['price'])}", "category": "严格标签匹配"}
                    })
                if len(final_results) >= 4: break

        cursor.close(); conn.close()
        return {"status": "success", "data": {"outfits": final_results}}

    except Exception as e:
        print(f"💥 崩溃了: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/random_looks")
def get_random_looks(limit: int = 12):
    try:
        conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
        cursor = conn.cursor()
        
        sql_query = "SELECT filename, item_category, color, brand, price, season, style FROM clothing_features ORDER BY RANDOM() LIMIT %s;"
        cursor.execute(sql_query, (limit,))
        rows = cursor.fetchall()
        
        random_items = [{
            "filename": str(row[0]).strip(), 
            "category": row[1], 
            "color": row[2], 
            "brand": row[3], 
            "price": f"¥{int(row[4])}" if row[4] else "¥199",
            "season": row[5] or "",  # 新增季节
            "style": row[6] or ""    # 新增风格
        } for row in rows]
        
        cursor.close(); conn.close()
        return {"status": "success", "data": random_items}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/debug_all_tags")
def get_all_tags():
    print("🚨 正在全量拉取数据库所有标签...")
    try:
        conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
        cursor = conn.cursor()
        
        # 直接 SELECT * 拿到所有列！
        cursor.execute("SELECT * FROM clothing_features ORDER BY filename;")
        
        # 动态获取你数据库表里所有的列名 (无论你建表时写了多少个标签，全能抓到)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            # 把列名和每一行的数据打包成字典
            item_dict = dict(zip(columns, row))
            if 'super_vector' in item_dict:
                del item_dict['super_vector']
            if 'vector' in item_dict:
                del item_dict['vector']
                
            # 处理一下可能出现的 None 值
            for key, value in item_dict.items():
                if value is None:
                    item_dict[key] = "无"
                    
            data.append(item_dict)
            
        cursor.close()
        conn.close()
        print(f"✅ 成功提取 {len(data)} 件服装的所有标签！")
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"💥 查水表崩溃: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
