# import os
# import json
# import psycopg2
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# import torch.nn.functional as F
# import clip
# from PIL import Image

# # ==========================================
# # 👗 真·语义级视觉搭配大屏 (基于你的向量检索思想)
# # ==========================================

# plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
# plt.rcParams['axes.unicode_minus'] = False 

# # 严格的品类隔离墙 (防止长裤变裙子的 Bug)
# TOP_TAGS = {"t-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", "tank top", "blouse", "cardigan", "suit blazer"}
# BOTTOM_TAGS = {"jeans", "casual trousers", "cargo pants", "shorts", "hot pants", "pleated skirt", "a-line skirt", "pencil skirt", "midi skirt", "mini skirt"}
# ONE_PIECE_TAGS = {"dress", "bodycon dress", "slip dress", "floral dress", "maxi dress", "jumpsuit"}

# # 极简的“一票否决”防呆图谱 (只用来做负面排除)
# KILL_RULES = {
#     "夏": ["winter", "coat", "sweater", "hoodie", "jacket"],
#     "冬": ["summer", "shorts", "hot pants", "tank top", "slip dress"],
# }

# def get_db_connection():
#     return psycopg2.connect(
#         host="localhost", database="postgres", 
#         user="postgres", password="123456", port="5432"
#     )

# def categorize_item(tags_str):
#     """【绝对防御版】极其严格的品类鉴定，彻底封杀长裤变裙子的Bug"""
#     tags_set = set([t.strip().lower() for t in tags_str.split(',')])
    
#     # 👑 最高优先级：只要它带有明确的裤子或半身裙标签，立刻锁死为下装！
#     if tags_set.intersection(BOTTOM_TAGS): 
#         return "bottom"
        
#     # 👑 第二优先级：只要带有明确的上衣标签，立刻锁死为上装！
#     if tags_set.intersection(TOP_TAGS): 
#         return "top"
        
#     # 👗 只有在系统绝对确认它既不是单件裤子，也不是单件上衣之后，如果它带有 dress，才允许它是连体装！
#     if tags_set.intersection(ONE_PIECE_TAGS): 
#         return "one_piece"
        
#     return "unknown"

# def recommend_and_visualize(user_query, img_base_dir, top_k=3):
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"\n✨ 正在把你的整段话交给 CLIP 大脑: [{user_query}]")
    
#     # ------------------------------------------------
#     # 1. 你的神级操作：提取全句的超级语义向量
#     # ------------------------------------------------
#     clip_model, _ = clip.load("ViT-L/14", device=device)
#     clip_model.eval()
#     with torch.no_grad():
#         text_tokens = clip.tokenize([user_query]).to(device)
#         query_vector = clip_model.encode_text(text_tokens).float()
#         query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

#     # 解析一票否决的死线
#     forbidden_tags = set()
#     for ch_word, ban_list in KILL_RULES.items():
#         if ch_word in user_query:
#             forbidden_tags.update(ban_list)
#     if forbidden_tags:
#         print(f"🛑 触发常识保底：严禁出现 {list(forbidden_tags)}")

#     # ------------------------------------------------
#     # 2. 从数据库提取特征
#     # ------------------------------------------------
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT filename, brand, price, clip_tags, super_vector::text FROM clothing_features;")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     items = []
#     for row in rows:
#         filename, brand, price, tags, vec_str = row
#         vec_list = json.loads(vec_str)
#         tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
#         items.append({
#             "filename": filename, "brand": brand, "price": price, 
#             "tags": tags, "vector": tensor_vec,
#             "category": categorize_item(tags),
#             "tag_set": set([t.strip().lower() for t in tags.split(',')])
#         })

#     # ------------------------------------------------
#     # 3. 第一阶段：全局纯语义大统考 (直接算向量！)
#     # ------------------------------------------------
#     all_vectors = torch.stack([item["vector"] for item in items])
#     # 这一步，CLIP 会自动去理解“海岛”、“鲜艳”到底长什么样！
#     all_sim_scores = torch.matmul(all_vectors, query_vector)

#     tops, bottoms, ops = [], [], []
    
#     # 根据分数派发，并执行一票否决
#     for idx, item in enumerate(items):
#         score = all_sim_scores[idx].item()
        
#         # 🛡️ 致命死刑判定：夏天绝不推大衣
#         if item["tag_set"].intersection(forbidden_tags):
#             score -= 100.0  
            
#         if score > 0: # 只要不是被判死刑的，都按品类装桶
#             item["semantic_score"] = score
#             if item["category"] == "top": tops.append(item)
#             elif item["category"] == "bottom": bottoms.append(item)
#             elif item["category"] == "one_piece": ops.append(item)

#     print(f"📦 语义初筛存活: 上装 {len(tops)} | 下装 {len(bottoms)} | 连体装 {len(ops)}")

#     # ------------------------------------------------
#     # 4. 第二阶段：审美碰撞与搭配
#     # ------------------------------------------------
#     final_outfits = []

#     # 【模式 A：上下装碰撞】
#     if tops and bottoms:
#         # 只取各自语义得分最高的前 30 件去碰撞，避免计算爆炸和劣质干扰
#         tops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         bottoms.sort(key=lambda x: x["semantic_score"], reverse=True)
#         best_tops = tops[:30]
#         best_bottoms = bottoms[:30]
        
#         t_vecs = torch.stack([t["vector"] for t in best_tops])
#         b_vecs = torch.stack([b["vector"] for b in best_bottoms])
        
#         t_scores = torch.tensor([t["semantic_score"] for t in best_tops])
#         b_scores = torch.tensor([b["semantic_score"] for b in best_bottoms])
        
#         raw_harmony = torch.matmul(t_vecs, b_vecs.T)
#         harmony_score = torch.exp(-((raw_harmony - 0.6) ** 2) / (2 * 0.2 ** 2))
        
#         combo_scores = (0.40 * t_scores.unsqueeze(1)) + (0.40 * b_scores.unsqueeze(0)) + (0.20 * harmony_score)
        
#         flat_scores = combo_scores.flatten()
#         top_combo_indices = torch.topk(flat_scores, min(20, len(flat_scores))).indices
        
#         for flat_idx in top_combo_indices:
#             t_idx = flat_idx // len(best_bottoms)
#             b_idx = flat_idx % len(best_bottoms)
#             final_outfits.append({
#                 "type": "combo",
#                 "score": combo_scores[t_idx, b_idx].item(),
#                 "top": best_tops[t_idx],
#                 "bottom": best_bottoms[b_idx]
#             })

#     # 【模式 B：连体装公平补偿】
#     if ops:
#         ops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         best_ops = ops[:20]
        
#         for op_item in best_ops:
#             op_score = (0.80 * op_item["semantic_score"]) + (0.20 * 0.85) # 补偿分
#             final_outfits.append({
#                 "type": "one_piece",
#                 "score": op_score,
#                 "item": op_item
#             })

#     # ------------------------------------------------
#     # 5. 排序发榜与终极可视化
#     # ------------------------------------------------
#     final_outfits.sort(key=lambda x: x["score"], reverse=True)
#     best_outfits = final_outfits[:top_k]
    
#     if not best_outfits:
#         print("💥 计算失败，未能生成有效搭配！")
#         return

#     print(f"\n🎉 智能审美计算完毕！正在为您展示画板...")
    
#     fig, axes = plt.subplots(nrows=len(best_outfits), ncols=2, figsize=(10, 4.5 * len(best_outfits)))
#     fig.suptitle(f"🤖 语义搜索大屏 | 需求: {user_query}", fontsize=14, fontweight='bold', y=0.98)
    
#     if len(best_outfits) == 1: axes = np.array([axes])

#     for i, outfit in enumerate(best_outfits):
#         score_text = f"匹配度得分: {outfit['score']:.4f}"
        
#         if outfit["type"] == "combo":
#             t = outfit["top"]
#             b = outfit["bottom"]
            
#             # 画上装
#             ax_top = axes[i, 0]
#             try: ax_top.imshow(Image.open(os.path.join(img_base_dir, t['filename'])).convert('RGB'))
#             except: ax_top.text(0.5, 0.5, '图丢了', ha='center')
#             ax_top.axis('off')
#             ax_top.set_title(f"👑 搭配 {i+1} (上衣) | ¥{t['price']}", color='darkred', fontsize=10)
#             ax_top.text(0.5, -0.1, f"{t['tags']}", transform=ax_top.transAxes, ha='center', fontsize=8, color='blue')
            
#             # 画下装
#             ax_bot = axes[i, 1]
#             try: ax_bot.imshow(Image.open(os.path.join(img_base_dir, b['filename'])).convert('RGB'))
#             except: ax_bot.text(0.5, 0.5, '图丢了', ha='center')
#             ax_bot.axis('off')
#             ax_bot.set_title(f"({score_text})\n搭配 {i+1} (下装) | ¥{b['price']}", color='darkgreen', fontsize=10)
#             ax_bot.text(0.5, -0.1, f"{b['tags']}", transform=ax_bot.transAxes, ha='center', fontsize=8, color='blue')

#         else: # 连体装
#             op = outfit["item"]
            
#             ax_op = axes[i, 0]
#             try: ax_op.imshow(Image.open(os.path.join(img_base_dir, op['filename'])).convert('RGB'))
#             except: ax_op.text(0.5, 0.5, '图丢了', ha='center')
#             ax_op.axis('off')
#             ax_op.set_title(f"👑 连体方案 {i+1}\n{score_text} | ¥{op['price']}", color='purple', fontweight='bold', fontsize=10)
#             ax_op.text(0.5, -0.1, f"自带标签: {op['tags']}", transform=ax_op.transAxes, ha='center', fontsize=8, color='blue')
            
#             ax_blank = axes[i, 1]
#             ax_blank.axis('off')
#             ax_blank.text(0.5, 0.5, "👗 一件搞定，无需搭配", ha='center', va='center', fontsize=12, color='gray')

#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
#     plt.show()

# if __name__ == "__main__":
#     img_dir = r"D:\dress_recommender\images\images" 
    
#     # 💡 见证奇迹：这一次大模型会完全理解“海岛”、“度假”、“鲜艳”！
#     test_query = "夏天去海岛穿的衣服，颜色鲜艳一点" 
    
#     recommend_and_visualize(test_query, img_dir, top_k=4)




# import os
# import json
# import psycopg2
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# import torch.nn.functional as F
# import clip
# from PIL import Image

# # ==========================================
# # 👗 终极工业级双引擎架构 (混合检索 Hybrid Search)
# # ==========================================

# plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
# plt.rcParams['axes.unicode_minus'] = False 

# TOP_TAGS = {"t-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", "tank top", "blouse", "cardigan", "suit blazer"}
# BOTTOM_TAGS = {"jeans", "casual trousers", "cargo pants", "shorts", "hot pants", "pleated skirt", "a-line skirt", "pencil skirt", "midi skirt", "mini skirt"}
# ONE_PIECE_TAGS = {"dress", "bodycon dress", "slip dress", "floral dress", "maxi dress", "jumpsuit"}

# # 🛡️ 混合检索：必须命中的正向硬筛 (只要触发，没这个标签就绝对不要)
# MUST_HAVE_RULES = {
#     "短裤": ["shorts", "hot pants"],
#     "短裙": ["mini skirt", "pleated skirt"],
#     "夏": ["summer", "shorts", "T-shirt", "tank top", "slip dress"],
#     "冬": ["winter", "coat", "sweater", "hoodie"]
# }

# # 🛑 混合检索：一票否决的负向硬筛 (连秋装一起封杀！)
# KILL_RULES = {
#     "夏": ["winter", "autumn", "coat", "sweater", "hoodie", "jacket", "casual trousers", "jeans"], # 强制夏天屏蔽长裤和秋装
#     "冬": ["summer", "shorts", "hot pants", "tank top", "slip dress"],
# }

# def get_db_connection():
#     return psycopg2.connect(
#         host="localhost", database="postgres", user="postgres", password="123456", port="5432"
#     )

# def categorize_item(tags_str):
#     """【终极防智障版】严格按照 CLIP 的置信度顺序判断！谁先出现听谁的！"""
#     # 保持 CLIP 给出的原始顺序（列表，而不是无序集合）
#     tags_list = [t.strip().lower() for t in tags_str.split(',')]
    
#     for tag in tags_list:
#         # 从最自信的标签开始往下顺，命中哪个就是哪个！
#         if tag in ONE_PIECE_TAGS: 
#             return "one_piece"
#         if tag in BOTTOM_TAGS: 
#             return "bottom"
#         if tag in TOP_TAGS: 
#             return "top"
            
#     return "unknown" # 如果全是风格标签（比如 summer, casual），兜底变 unknown

# # 注意这里：我们把“中文硬规则”和“英文审美词”分开了！
# def recommend_and_visualize(rule_query, vibe_query, img_base_dir, top_k=3):
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"\n✨ 正在启动双引擎推荐...")
#     print(f"🔒 逻辑引擎锁定规则: [{rule_query}]")
#     print(f"🎨 审美引擎渲染意境: [{vibe_query}]")
    
#     # ------------------------------------------------
#     # 1. 提取绝对规则
#     # ------------------------------------------------
#     must_have_tags = set()
#     for ch_word, must_list in MUST_HAVE_RULES.items():
#         if ch_word in rule_query:
#             must_have_tags.update(must_list)
            
#     forbidden_tags = set()
#     for ch_word, ban_list in KILL_RULES.items():
#         if ch_word in rule_query:
#             forbidden_tags.update(ban_list)
            
#     if must_have_tags: print(f"🎯 正向强制要求: 必须包含 {list(must_have_tags)[:3]} 等")
#     if forbidden_tags: print(f"🛑 负向一票否决: 严禁出现 {list(forbidden_tags)[:3]} 等")

#     # ------------------------------------------------
#     # 2. 提取 CLIP 高维审美向量
#     # ------------------------------------------------
#     clip_model, _ = clip.load("ViT-L/14", device=device)
#     clip_model.eval()
#     with torch.no_grad():
#         text_tokens = clip.tokenize([vibe_query]).to(device)
#         query_vector = clip_model.encode_text(text_tokens).float()
#         query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

#     # ------------------------------------------------
#     # 3. 第一阶段：带锁的全局提取
#     # ------------------------------------------------
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT filename, brand, price, clip_tags, super_vector::text FROM clothing_features;")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     tops, bottoms, ops = [], [], []
    
#     for row in rows:
#         filename, brand, price, tags, vec_str = row
#         tag_set = set([t.strip().lower() for t in tags.split(',')])
        
#         # ⚔️ 规则层：死刑拦截 (长袖长裤秋装统统滚蛋)
#         if tag_set.intersection(forbidden_tags):
#             continue
            
#         # ⚔️ 规则层：正向拦截 (如果设定了必须有短裤/夏天，没命中的直接滚蛋)
#         # 注意：这里我们给一定容忍度，只要命中必须标签中的任意一个即可存活
#         if must_have_tags and not tag_set.intersection(must_have_tags):
#             continue
            
#         vec_list = json.loads(vec_str)
#         tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
        
#         # 算审美分
#         semantic_score = torch.matmul(tensor_vec, query_vector).item()
        
#         item = {
#             "filename": filename, "brand": brand, "price": price, 
#             "tags": tags, "vector": tensor_vec, "semantic_score": semantic_score
#         }
        
#         category = categorize_item(tags)
#         if category == "top": tops.append(item)
#         elif category == "bottom": bottoms.append(item)
#         elif category == "one_piece": ops.append(item)

#     print(f"📦 规则墙过滤后，存活高潜单品: 上装 {len(tops)} | 下装 {len(bottoms)} | 连体装 {len(ops)}")

#     if not tops and not bottoms and not ops:
#         print("💥 完蛋！在极其严格的规则下，你的图库里找不到任何衣服！(去检查是不是图片太少了)")
#         return

#     # ------------------------------------------------
#     # 4. 第二阶段：审美碰撞与搭配
#     # ------------------------------------------------
#     final_outfits = []

#     if tops and bottoms:
#         tops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         bottoms.sort(key=lambda x: x["semantic_score"], reverse=True)
#         best_tops = tops[:20]
#         best_bottoms = bottoms[:20]
        
#         t_vecs = torch.stack([t["vector"] for t in best_tops])
#         b_vecs = torch.stack([b["vector"] for b in best_bottoms])
        
#         t_scores = torch.tensor([t["semantic_score"] for t in best_tops])
#         b_scores = torch.tensor([b["semantic_score"] for b in best_bottoms])
        
#         raw_harmony = torch.matmul(t_vecs, b_vecs.T)
#         # 降低和谐分的权重，打破枢纽效应的霸权
#         harmony_score = torch.exp(-((raw_harmony - 0.6) ** 2) / (2 * 0.2 ** 2))
        
#         combo_scores = (0.45 * t_scores.unsqueeze(1)) + (0.45 * b_scores.unsqueeze(0)) + (0.10 * harmony_score)
        
#         flat_scores = combo_scores.flatten()
#         top_combo_indices = torch.topk(flat_scores, min(20, len(flat_scores))).indices
        
#         for flat_idx in top_combo_indices:
#             t_idx = flat_idx // len(best_bottoms)
#             b_idx = flat_idx % len(best_bottoms)
#             final_outfits.append({
#                 "type": "combo",
#                 "score": combo_scores[t_idx, b_idx].item(),
#                 "top": best_tops[t_idx],
#                 "bottom": best_bottoms[b_idx]
#             })

#     if ops:
#         ops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         for op_item in ops[:10]:
#             op_score = (0.90 * op_item["semantic_score"]) + (0.10 * 0.85)
#             final_outfits.append({
#                 "type": "one_piece", "score": op_score, "item": op_item
#             })

#     # ------------------------------------------------
#     # 5. 可视化大屏
#     # ------------------------------------------------
#     final_outfits.sort(key=lambda x: x["score"], reverse=True)
#     best_outfits = final_outfits[:top_k]
    
#     if not best_outfits: return

#     fig, axes = plt.subplots(nrows=len(best_outfits), ncols=2, figsize=(10, 4.5 * len(best_outfits)))
#     fig.suptitle(f"🤖 双引擎过滤大屏 | 意境: {vibe_query}", fontsize=14, fontweight='bold', y=0.98)
#     if len(best_outfits) == 1: axes = np.array([axes])

#     for i, outfit in enumerate(best_outfits):
#         score_text = f"总评分: {outfit['score']:.4f}"
        
#         if outfit["type"] == "combo":
#             t = outfit["top"]
#             b = outfit["bottom"]
            
#             ax_top = axes[i, 0]
#             try: ax_top.imshow(Image.open(os.path.join(img_base_dir, t['filename'])).convert('RGB'))
#             except: ax_top.text(0.5, 0.5, '图丢了', ha='center')
#             ax_top.axis('off')
#             ax_top.set_title(f"👑 搭配 {i+1} (上衣) | ¥{t['price']}", color='darkred', fontsize=10)
#             ax_top.text(0.5, -0.1, f"{t['tags']}", transform=ax_top.transAxes, ha='center', fontsize=8, color='blue')
            
#             ax_bot = axes[i, 1]
#             try: ax_bot.imshow(Image.open(os.path.join(img_base_dir, b['filename'])).convert('RGB'))
#             except: ax_bot.text(0.5, 0.5, '图丢了', ha='center')
#             ax_bot.axis('off')
#             ax_bot.set_title(f"({score_text})\n搭配 {i+1} (下装) | ¥{b['price']}", color='darkgreen', fontsize=10)
#             ax_bot.text(0.5, -0.1, f"{b['tags']}", transform=ax_bot.transAxes, ha='center', fontsize=8, color='blue')

#         else:
#             op = outfit["item"]
            
#             ax_op = axes[i, 0]
#             try: ax_op.imshow(Image.open(os.path.join(img_base_dir, op['filename'])).convert('RGB'))
#             except: ax_op.text(0.5, 0.5, '图丢了', ha='center')
#             ax_op.axis('off')
#             ax_op.set_title(f"👑 连体方案 {i+1}\n{score_text} | ¥{op['price']}", color='purple', fontweight='bold', fontsize=10)
#             ax_op.text(0.5, -0.1, f"自带标签: {op['tags']}", transform=ax_op.transAxes, ha='center', fontsize=8, color='blue')
            
#             ax_blank = axes[i, 1]
#             ax_blank.axis('off')
#             ax_blank.text(0.5, 0.5, "👗 一件搞定", ha='center', va='center', fontsize=12, color='gray')

#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
#     plt.show()

# if __name__ == "__main__":
#     img_dir = r"D:\dress_recommender\images\images" 
    
#     # 🎯 核心改变：把“死板的硬筛”和“意境的搜索”分开！
#     # 只要 rule_query 里带了“夏”，秋装和长裤必定在海选阶段就被爆头！
#     rule_query = "冬天" 
#     vibe_query = "Simple，neutral-colored outfits for the park in winter" 
    
#     recommend_and_visualize(rule_query, vibe_query, img_dir, top_k=4)


# import os
# import json
# import psycopg2
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# import torch.nn.functional as F
# import clip
# from PIL import Image

# # ==========================================
# # 👗 V3.0 终极推荐大脑 (自动解析 + 柔性提权 + 语义渲染)
# # ==========================================

# plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
# plt.rcParams['axes.unicode_minus'] = False 

# TOP_TAGS = {"t-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", "tank top", "blouse", "cardigan", "suit blazer"}
# BOTTOM_TAGS = {"jeans", "casual trousers", "cargo pants", "shorts", "hot pants", "pleated skirt", "a-line skirt", "pencil skirt", "midi skirt", "mini skirt"}
# ONE_PIECE_TAGS = {"dress", "bodycon dress", "slip dress", "floral dress", "maxi dress", "jumpsuit"}

# # 🛑 绝对底线：反人类穿搭一票否决 (只封杀绝对不合理的)
# KILL_RULES = {
#     "夏": ["winter", "coat", "sweater", "hoodie"], # 夏天不再封杀长裤，只封杀羽绒服/毛衣！
#     "冬": ["summer", "shorts", "hot pants", "tank top", "slip dress"],
# }

# # 🚀 柔性提权：场景偏好加分 (打破长裤霸权的神器！)
# BOOST_RULES = {
#     "夏": {"tags": ["shorts", "hot pants", "mini skirt", "tank top", "T-shirt", "slip dress"], "bonus": 0.15},
#     "海岛": {"tags": ["floral dress", "slip dress", "shorts", "tank top"], "bonus": 0.20},
#     "运动": {"tags": ["sporty", "T-shirt", "shorts", "casual trousers"], "bonus": 0.15},
#     "约会": {"tags": ["romantic dating", "sweet", "dress", "blouse"], "bonus": 0.15}
# }

# def get_db_connection():
#     return psycopg2.connect(
#         host="localhost", database="postgres", user="postgres", password="123456", port="5432"
#     )

# def categorize_item(tags_str):
#     tags_list = [t.strip().lower() for t in tags_str.split(',')]
#     for tag in tags_list:
#         if tag in ONE_PIECE_TAGS: return "one_piece"
#         if tag in BOTTOM_TAGS: return "bottom"
#         if tag in TOP_TAGS: return "top"
#     return "unknown"

# def simulate_llm_parser(user_input_cn):
#     """
#     模拟企业级 LLM 网关：把用户的大白话拆解为【逻辑关键词】和【CLIP英文提示词】
#     在真实线上环境，这里会调用一次 GPT-4 / 文心一言 的 API。
#     """
#     print(f"\n🧠 智能网关正在解析用户输入: [{user_input_cn}]")
    
#     # 模拟简单的词汇触发来提取逻辑关键词
#     logic_keywords = []
#     if "夏" in user_input_cn: logic_keywords.append("夏")
#     if "冬" in user_input_cn: logic_keywords.append("冬")
#     if "海岛" in user_input_cn or "海边" in user_input_cn: logic_keywords.append("海岛")
#     if "运动" in user_input_cn: logic_keywords.append("运动")
    
#     # 模拟将中文翻译为地道的英文 Prompt (这里用字典映射模拟)
#     vibe_en = "A beautiful clothing outfit" # 兜底
#     if "夏" in user_input_cn and "海岛" in user_input_cn and "鲜艳" in user_input_cn:
#         vibe_en = "A highly colorful, bright and breezy outfit for a summer island vacation"
#     elif "冬" in user_input_cn and "公园" in user_input_cn:
#         vibe_en = "Simple, neutral-colored warm outfits for walking in the park in winter"
        
#     print(f"   ├─ 抓取逻辑关键词: {logic_keywords}")
#     print(f"   └─ 生成审美 Prompt: {vibe_en}")
    
#     return logic_keywords, vibe_en

# def recommend_and_visualize(user_input_cn, img_base_dir, top_k=3):
#     device = "cuda" if torch.cuda.is_available() else "cpu"
    
#     # 1. 自动解析意图
#     logic_keywords, vibe_query = simulate_llm_parser(user_input_cn)
    
#     forbidden_tags = set()
#     for kw in logic_keywords:
#         if kw in KILL_RULES: forbidden_tags.update(KILL_RULES[kw])

#     # 2. 提取 CLIP 高维审美向量
#     clip_model, _ = clip.load("ViT-L/14", device=device)
#     clip_model.eval()
#     with torch.no_grad():
#         text_tokens = clip.tokenize([vibe_query]).to(device)
#         query_vector = clip_model.encode_text(text_tokens).float()
#         query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

#     # 3. 连库提取与初筛
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT filename, brand, price, clip_tags, super_vector::text FROM clothing_features;")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     tops, bottoms, ops = [], [], []
    
#     for row in rows:
#         filename, brand, price, tags, vec_str = row
#         tag_list = [t.strip().lower() for t in tags.split(',')]
#         tag_set = set(tag_list)
        
#         # ⚔️ 绝对死线拦截 (羽绒服夏天死啦死啦地)
#         if tag_set.intersection(forbidden_tags):
#             continue
            
#         vec_list = json.loads(vec_str)
#         tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
        
#         # 🎨 核心：审美基础分
#         base_semantic_score = torch.matmul(tensor_vec, query_vector).item()
        
#         # 🚀 核心：柔性提权机制 (Contextual Boosting)
#         bonus_score = 0.0
#         for kw in logic_keywords:
#             if kw in BOOST_RULES:
#                 boost_tags = set(BOOST_RULES[kw]["tags"])
#                 # 如果这件衣服带有被提权的标签，加分！
#                 if tag_set.intersection(boost_tags):
#                     bonus_score += BOOST_RULES[kw]["bonus"]
        
#         final_semantic_score = base_semantic_score + bonus_score
        
#         item = {
#             "filename": filename, "brand": brand, "price": price, 
#             "tags": tags, "vector": tensor_vec, "semantic_score": final_semantic_score
#         }
        
#         category = categorize_item(tags)
#         if category == "top": tops.append(item)
#         elif category == "bottom": bottoms.append(item)
#         elif category == "one_piece": ops.append(item)

#     # 4. 审美碰撞
#     final_outfits = []
#     if tops and bottoms:
#         tops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         bottoms.sort(key=lambda x: x["semantic_score"], reverse=True)
#         best_tops = tops[:20]
#         best_bottoms = bottoms[:20]
        
#         t_vecs = torch.stack([t["vector"] for t in best_tops])
#         b_vecs = torch.stack([b["vector"] for b in best_bottoms])
        
#         t_scores = torch.tensor([t["semantic_score"] for t in best_tops])
#         b_scores = torch.tensor([b["semantic_score"] for b in best_bottoms])
        
#         raw_harmony = torch.matmul(t_vecs, b_vecs.T)
#         harmony_score = torch.exp(-((raw_harmony - 0.6) ** 2) / (2 * 0.2 ** 2))
        
#         # 弱化和谐分权重，强调单品的语义和提权分
#         combo_scores = (0.45 * t_scores.unsqueeze(1)) + (0.45 * b_scores.unsqueeze(0)) + (0.10 * harmony_score)
        
#         flat_scores = combo_scores.flatten()
#         top_combo_indices = torch.topk(flat_scores, min(20, len(flat_scores))).indices
        
#         for flat_idx in top_combo_indices:
#             t_idx = flat_idx // len(best_bottoms)
#             b_idx = flat_idx % len(best_bottoms)
#             final_outfits.append({
#                 "type": "combo", "score": combo_scores[t_idx, b_idx].item(),
#                 "top": best_tops[t_idx], "bottom": best_bottoms[b_idx]
#             })

#     if ops:
#         ops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         for op_item in ops[:10]:
#             op_score = (0.90 * op_item["semantic_score"]) + (0.10 * 0.85)
#             final_outfits.append({
#                 "type": "one_piece", "score": op_score, "item": op_item
#             })

#     # 5. 画板展示
#     final_outfits.sort(key=lambda x: x["score"], reverse=True)
#     best_outfits = final_outfits[:top_k]
    
#     if not best_outfits: 
#         print("💥 找不到搭配！")
#         return

#     fig, axes = plt.subplots(nrows=len(best_outfits), ncols=2, figsize=(10, 4.5 * len(best_outfits)))
#     fig.suptitle(f"🤖 智能推荐大屏 | 需求: {user_input_cn}", fontsize=14, fontweight='bold', y=0.98)
#     if len(best_outfits) == 1: axes = np.array([axes])

#     for i, outfit in enumerate(best_outfits):
#         score_text = f"匹配度: {outfit['score']:.4f}"
#         if outfit["type"] == "combo":
#             t = outfit["top"]
#             b = outfit["bottom"]
            
#             ax_top = axes[i, 0]
#             try: ax_top.imshow(Image.open(os.path.join(img_base_dir, t['filename'])).convert('RGB'))
#             except: ax_top.text(0.5, 0.5, '图丢了', ha='center')
#             ax_top.axis('off')
#             ax_top.set_title(f"👑 搭配 {i+1} (上衣) | ¥{t['price']}", color='darkred', fontsize=10)
#             ax_top.text(0.5, -0.1, f"{t['tags']}", transform=ax_top.transAxes, ha='center', fontsize=8, color='blue')
            
#             ax_bot = axes[i, 1]
#             try: ax_bot.imshow(Image.open(os.path.join(img_base_dir, b['filename'])).convert('RGB'))
#             except: ax_bot.text(0.5, 0.5, '图丢了', ha='center')
#             ax_bot.axis('off')
#             ax_bot.set_title(f"({score_text})\n搭配 {i+1} (下装) | ¥{b['price']}", color='darkgreen', fontsize=10)
#             ax_bot.text(0.5, -0.1, f"{b['tags']}", transform=ax_bot.transAxes, ha='center', fontsize=8, color='blue')

#         else:
#             op = outfit["item"]
            
#             ax_op = axes[i, 0]
#             try: ax_op.imshow(Image.open(os.path.join(img_base_dir, op['filename'])).convert('RGB'))
#             except: ax_op.text(0.5, 0.5, '图丢了', ha='center')
#             ax_op.axis('off')
#             ax_op.set_title(f"👑 连体方案 {i+1}\n{score_text} | ¥{op['price']}", color='purple', fontweight='bold', fontsize=10)
#             ax_op.text(0.5, -0.1, f"自带标签: {op['tags']}", transform=ax_op.transAxes, ha='center', fontsize=8, color='blue')
            
#             ax_blank = axes[i, 1]
#             ax_blank.axis('off')
#             ax_blank.text(0.5, 0.5, "👗 一件搞定", ha='center', va='center', fontsize=12, color='gray')

#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
#     plt.show()

# if __name__ == "__main__":
#     img_dir = r"D:\dress_recommender\images\images" 
    
#     # 🎯 终极All-in-One输入！你只需要输入这一句话！
#     user_input = "参加婚礼穿啥，庄重一点" 
    
#     recommend_and_visualize(user_input, img_dir, top_k=4)



# import os
# import json
# import psycopg2
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# import torch.nn.functional as F
# import clip
# from PIL import Image

# # ==========================================
# # 👗 V5.0 商业级 UI 绝对硬控推荐大脑 (修复品类漂移)
# # ==========================================

# plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
# plt.rcParams['axes.unicode_minus'] = False 

# TOP_TAGS = {"t-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", "tank top", "blouse", "cardigan", "suit blazer"}
# BOTTOM_TAGS = {"jeans", "casual trousers", "cargo pants", "shorts", "hot pants", "pleated skirt", "a-line skirt", "pencil skirt", "midi skirt", "mini skirt"}
# ONE_PIECE_TAGS = {"dress", "bodycon dress", "slip dress", "floral dress", "maxi dress", "jumpsuit"}

# # 🧠 前端 UI 中文选项 -> 后端数据库英文标签
# UI_TAG_MAP = {
#     "运动": "sporty", "正式": "formal", "休闲": "casual", "复古": "vintage", "街头": "streetwear",
#     "约会": "romantic dating", "通勤": "business casual", "极简": "minimalist", "户外": "outdoor", "甜美": "sweet", "性感": "sexy",
#     "棉": "cotton", "牛仔": "denim", "皮": "leather", "针织": "knit", "丝绸": "silk", "雪纺": "chiffon",
#     "t恤": "T-shirt", "衬衫": "shirt", "毛衣": "sweater", "卫衣": "hoodie", "外套": "jacket", "大衣": "coat",
#     "吊带": "tank top", "西装": "suit blazer",
#     "牛仔裤": "jeans", "长裤": "casual trousers", "工装裤": "cargo pants", "短裤": "shorts",
#     "百褶裙": "pleated skirt", "包臀裙": "pencil skirt", "半身裙": "midi skirt",
#     "连衣裙": "dress", "吊带裙": "slip dress", "碎花裙": "floral dress", "连体裤": "jumpsuit",
#     "春": "spring", "夏": "summer", "秋": "autumn", "冬": "winter",
#     "黑色": "black", "白色": "white", "红色": "red", "蓝色": "blue", 
#     "鲜艳": "highly colorful and bright" # 这是一个氛围词
# }

# def get_db_connection():
#     return psycopg2.connect(
#         host="localhost", database="postgres", user="postgres", password="123456", port="5432"
#     )

# def categorize_item(tags_str):
#     """极其严格的品类判断，按置信度顺序"""
#     tags_list = [t.strip().lower() for t in tags_str.split(',')]
#     for tag in tags_list:
#         if tag in ONE_PIECE_TAGS: return "one_piece"
#         if tag in BOTTOM_TAGS: return "bottom"
#         if tag in TOP_TAGS: return "top"
#     return "unknown"

# def recommend_from_ui_tags(selected_ch_options, img_base_dir, top_k=3):
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"\n📱 接收到前端极其明确的圣旨: {selected_ch_options}")
    
#     # ==========================================
#     # 1. 核心大改：把软氛围和硬指标彻底分开！
#     # ==========================================
#     hard_keywords = []  # 绝对不能妥协的词（如 dress, floral, summer）
#     vibe_phrases = []   # 渲染意境的词（如 colorful）
    
#     for opt in selected_ch_options:
#         en_tag = UI_TAG_MAP.get(opt, "")
#         if not en_tag: continue
            
#         # 只要是描述感觉的词，丢给氛围组
#         if opt in ["鲜艳", "复古", "极简", "高级"]:
#             vibe_phrases.append(en_tag)
#         else:
#             # 比如 "floral dress" 会被拆成 ["floral", "dress"]
#             # 衣服必须同时带有这俩词才能活下来！
#             hard_keywords.extend(en_tag.split())
            
#     # 生成 CLIP 提示词（把硬指标和氛围词拼起来，让大模型画面感更强）
#     vibe_query = f"A highly aesthetic fashion outfit featuring: {' '.join(vibe_phrases)} {' '.join(hard_keywords)}"
#     print(f"🎯 绝对硬核过滤词 (少一个都不行): {hard_keywords}")
#     print(f"🎨 CLIP 审美渲染器已启动: [{vibe_query}]")

#     clip_model, _ = clip.load("ViT-L/14", device=device)
#     clip_model.eval()
#     with torch.no_grad():
#         text_tokens = clip.tokenize([vibe_query]).to(device)
#         query_vector = clip_model.encode_text(text_tokens).float()
#         query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT filename, brand, price, clip_tags, super_vector::text FROM clothing_features;")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     tops, bottoms, ops = [], [], []
    
#     # ==========================================
#     # 2. 绝对硬杀机制：天王老子来了也得守规矩！
#     # ==========================================
#     for row in rows:
#         filename, brand, price, tags, vec_str = row
#         tags_lower = tags.lower()
        
#         # 🛡️ 一票否决：如果你勾了"碎花裙"(floral dress)
#         # 那么这件衣服的标签里如果找不到"floral"或者"dress"，直接踢掉！
#         failed_hard_filter = False
#         for kw in hard_keywords:
#             if kw not in tags_lower:
#                 failed_hard_filter = True
#                 break
                
#         if failed_hard_filter:
#             continue # 滚蛋，连算分的资格都没有！
            
#         # 如果能活到这里，说明它 100% 是一件拥有夏天的碎花裙！
#         vec_list = json.loads(vec_str)
#         tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
        
#         semantic_score = torch.matmul(tensor_vec, query_vector).item()
        
#         item = {
#             "filename": filename, "brand": brand, "price": price, 
#             "tags": tags, "vector": tensor_vec, "semantic_score": semantic_score
#         }
        
#         category = categorize_item(tags)
#         if category == "top": tops.append(item)
#         elif category == "bottom": bottoms.append(item)
#         elif category == "one_piece": ops.append(item)

#     if not tops and not bottoms and not ops:
#         print("💥 完蛋！在您的绝对硬要求下，库里根本没有同时满足这些标签的衣服！(比如你又要短裤又要裙子，或者库里根本没有碎花裙)")
#         return

#     # 3. 审美碰撞
#     final_outfits = []
    
#     # 因为用户选了"碎花裙"(包含 dress)，上面的硬筛会导致 tops 和 bottoms 必定为空！
#     # 搭配逻辑会自动失效，极其优雅地只执行 One-Piece 逻辑！
#     if tops and bottoms:
#         tops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         bottoms.sort(key=lambda x: x["semantic_score"], reverse=True)
#         best_tops, best_bottoms = tops[:20], bottoms[:20]
        
#         t_vecs = torch.stack([t["vector"] for t in best_tops])
#         b_vecs = torch.stack([b["vector"] for b in best_bottoms])
#         t_scores = torch.tensor([t["semantic_score"] for t in best_tops])
#         b_scores = torch.tensor([b["semantic_score"] for b in best_bottoms])
        
#         raw_harmony = torch.matmul(t_vecs, b_vecs.T)
#         harmony_score = torch.exp(-((raw_harmony - 0.6) ** 2) / (2 * 0.2 ** 2))
#         combo_scores = (0.45 * t_scores.unsqueeze(1)) + (0.45 * b_scores.unsqueeze(0)) + (0.10 * harmony_score)
        
#         flat_scores = combo_scores.flatten()
#         top_combo_indices = torch.topk(flat_scores, min(20, len(flat_scores))).indices
        
#         for flat_idx in top_combo_indices:
#             t_idx = flat_idx // len(best_bottoms)
#             b_idx = flat_idx % len(best_bottoms)
#             final_outfits.append({
#                 "type": "combo", "score": combo_scores[t_idx, b_idx].item(),
#                 "top": best_tops[t_idx], "bottom": best_bottoms[b_idx]
#             })

#     if ops:
#         ops.sort(key=lambda x: x["semantic_score"], reverse=True)
#         for op_item in ops[:10]:
#             # 连体服直接展示，不需要补偿分了，因为它是靠硬实力杀进来的
#             final_outfits.append({
#                 "type": "one_piece", "score": op_item["semantic_score"], "item": op_item
#             })

#     # 4. 可视化大屏
#     final_outfits.sort(key=lambda x: x["score"], reverse=True)
#     best_outfits = final_outfits[:top_k]

#     fig, axes = plt.subplots(nrows=len(best_outfits), ncols=2, figsize=(10, 4.5 * len(best_outfits)))
#     fig.suptitle(f"🤖 绝对硬控精排引擎 | 筛选项: {' | '.join(selected_ch_options)}", fontsize=14, fontweight='bold', y=0.98)
#     if len(best_outfits) == 1: axes = np.array([axes])

#     for i, outfit in enumerate(best_outfits):
#         score_text = f"匹配度: {outfit['score']:.4f}"
#         if outfit["type"] == "combo":
#             t, b = outfit["top"], outfit["bottom"]
            
#             ax_top = axes[i, 0]
#             try: ax_top.imshow(Image.open(os.path.join(img_base_dir, t['filename'])).convert('RGB'))
#             except: ax_top.text(0.5, 0.5, '图丢了', ha='center')
#             ax_top.axis('off')
#             ax_top.set_title(f"👑 搭配 {i+1} (上衣) | ¥{t['price']}", color='darkred', fontsize=10)
#             ax_top.text(0.5, -0.1, f"{t['tags']}", transform=ax_top.transAxes, ha='center', fontsize=8, color='blue')
            
#             ax_bot = axes[i, 1]
#             try: ax_bot.imshow(Image.open(os.path.join(img_base_dir, b['filename'])).convert('RGB'))
#             except: ax_bot.text(0.5, 0.5, '图丢了', ha='center')
#             ax_bot.axis('off')
#             ax_bot.set_title(f"({score_text})\n搭配 {i+1} (下装) | ¥{b['price']}", color='darkgreen', fontsize=10)
#             ax_bot.text(0.5, -0.1, f"{b['tags']}", transform=ax_bot.transAxes, ha='center', fontsize=8, color='blue')

#         else:
#             op = outfit["item"]
#             ax_op = axes[i, 0]
#             try: ax_op.imshow(Image.open(os.path.join(img_base_dir, op['filename'])).convert('RGB'))
#             except: ax_op.text(0.5, 0.5, '图丢了', ha='center')
#             ax_op.axis('off')
#             ax_op.set_title(f"👑 连体方案 {i+1}\n{score_text} | ¥{op['price']}", color='purple', fontweight='bold', fontsize=10)
#             ax_op.text(0.5, -0.1, f"自带标签: {op['tags']}", transform=ax_op.transAxes, ha='center', fontsize=8, color='blue')
            
#             ax_blank = axes[i, 1]
#             ax_blank.axis('off')
#             ax_blank.text(0.5, 0.5, "👗 碎花裙一件搞定\n绝不会出现半袖短裤", ha='center', va='center', fontsize=12, color='darkred', fontweight='bold')

#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
#     plt.show()

# if __name__ == "__main__":
#     img_dir = r"D:\dress_recommender\images\images" 
    
#     frontend_selected_options = ["夏", "鲜艳", "裙子"]
    
#     recommend_from_ui_tags(frontend_selected_options, img_dir, top_k=4)


import os
import json
import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
import clip
from PIL import Image

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
plt.rcParams['axes.unicode_minus'] = False 

def apply_mmr(items, top_n=20, diversity_weight=0.6):
    """
    👑 MMR (最大边际相关性) 核心算法：打压出头鸟，扶持多样性！
    diversity_weight: 多样性权重，越高越排斥相似的衣服 (0.0 到 1.0)
    """
    if not items: return []
    
    selected_items = []
    candidates = items.copy()
    
    best_idx = max(range(len(candidates)), key=lambda i: candidates[i]['semantic_score'])
    selected_items.append(candidates.pop(best_idx))
    
    while len(selected_items) < top_n and candidates:
        best_mmr_score = -float('inf')
        best_candidate_idx = -1
        
        selected_vecs = torch.stack([x['vector'] for x in selected_items])
        
        for i, cand in enumerate(candidates):
            cand_vec = cand['vector']
            
            # 算一下这件候选衣服，跟【已经上榜】的衣服有多像
            # 如果它跟榜单上的某件衣服极度相似，max_sim 就会非常高
            sims = torch.matmul(selected_vecs, cand_vec)
            max_sim = sims.max().item()
            
            # ⚖️ MMR 核心公式：原始得分 - (多样性权重 * 内部相似度)
            # 你的原始得分再高，如果跟榜单上的衣服撞款了，也要被疯狂扣分
            mmr_score = (1 - diversity_weight) * cand['semantic_score'] - (diversity_weight * max_sim)
            
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_candidate_idx = i
                
        # 把经过反垄断审查后得分最高的刺客，选入榜单
        selected_items.append(candidates.pop(best_candidate_idx))
        
    return selected_items

def get_db_connection():
    return psycopg2.connect(
        host="localhost", database="postgres", user="postgres", password="123456", port="5432"
    )

def recommend_from_structured_db(ui_options, img_base_dir, top_k=3):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n📱 接收到前端 UI 选项: {ui_options}")
    
    req_season = None
    req_category = None
    req_color = None       # 🎨 新增：颜色物理硬控锁！
    boost_scene = None
    boost_style = None
    vibe_words = []
    
    for opt in ui_options:
        opt_lower = opt.lower()
        
        # 🛑 [表头 1: Season 季节] 绝对硬指标
        if opt_lower in ["春", "春季", "春天", "早春", "初春"]: req_season = "spring"
        elif opt_lower in ["夏", "夏季", "夏天", "炎热", "清凉", "酷暑"]: req_season = "summer"
        elif opt_lower in ["秋", "秋季", "秋天", "初秋", "深秋"]: req_season = "autumn"
        elif opt_lower in ["冬", "冬季", "冬天", "寒冷", "保暖", "过冬"]: req_season = "winter"
        
        # 🛑 [表头 2: Category 品类] 绝对硬指标
        if opt_lower in ["碎花裙", "连衣裙", "包臀裙", "吊带裙", "长裙", "短裙", "连体裤", "礼服", "旗袍", "裙子"]: req_category = "one_piece"
        elif opt_lower in ["t恤", "短袖", "衬衫", "毛衣", "卫衣", "外套", "大衣", "吊带", "背心", "西装", "夹克", "羽绒服", "上衣"]: req_category = "top"
        elif opt_lower in ["牛仔裤", "长裤", "短裤", "工装裤", "热裤", "百褶裙", "半身裙", "a字裙", "阔腿裤", "运动裤", "瑜伽裤", "下装"]: req_category = "bottom"
        
        # 🛑 [表头 3: Color 颜色] 绝对硬指标 
        if opt_lower in ["黑", "黑色", "暗黑", "纯黑"]: req_color = "black"
        elif opt_lower in ["白", "白色", "纯白", "米白", "象牙白", "奶白"]: req_color = "white"
        elif opt_lower in ["灰", "灰色", "浅灰", "深灰", "高级灰"]: req_color = "gray"
        elif opt_lower in ["红", "红色", "酒红", "大红", "玫瑰红", "暗红"]: req_color = "red"
        elif opt_lower in ["蓝", "蓝色", "浅蓝", "深蓝", "天蓝", "藏青", "克莱因蓝", "水蓝"]: req_color = "blue"
        elif opt_lower in ["绿", "绿色", "墨绿", "浅绿", "军绿", "薄荷绿", "草绿", "牛油果绿"]: req_color = "green"
        elif opt_lower in ["黄", "黄色", "亮黄", "姜黄", "鹅黄", "明黄", "柠檬黄"]: req_color = "yellow"
        elif opt_lower in ["粉", "粉色", "芭比粉", "少女粉", "蜜桃粉", "脏粉", "樱花粉"]: req_color = "pink"
        elif opt_lower in ["棕", "棕色", "咖色", "咖啡色", "焦糖色", "巧克力色", "大地色"]: req_color = "brown"
        elif opt_lower in ["紫", "紫色", "香芋紫", "薰衣草紫", "暗紫", "葡萄紫"]: req_color = "purple"
        elif opt_lower in ["卡其", "卡其色", "杏色", "裸色", "燕麦色", "奶茶色", "驼色"]: req_color = "khaki"
        elif opt_lower in ["拼色", "彩色", "撞色", "花色", "多色", "五颜六色", "花哨"]: req_color = "multi-color"
        
        # 🚀 [表头 4: Scene 场景] 软加分提权
        if opt_lower in ["办公室", "通勤", "上班", "职场", "面试"]: boost_scene = "office workplace"
        elif opt_lower in ["婚礼", "晚宴", "聚会", "年会", "派对"]: boost_scene = "formal banquet or wedding"
        elif opt_lower in ["居家", "休息", "睡觉", "宅家", "睡衣"]: boost_scene = "home relaxing"
        elif opt_lower in ["健身房", "室内运动", "瑜伽", "普拉提"]: boost_scene = "indoor gym"
        elif opt_lower in ["海岛", "沙滩", "海边", "度假", "旅游"]: boost_scene = "beach vacation"
        elif opt_lower in ["公园", "露营", "野餐", "踏青", "郊游", "音乐节"]: boost_scene = "park camping"
        elif opt_lower in ["逛街", "街头", "购物", "探店", "约会"]: boost_scene = "street shopping"
        elif opt_lower in ["户外运动", "爬山", "徒步", "跑步", "滑雪", "骑行"]: boost_scene = "outdoor sports"
        
        # 🚀 [表头 5: Style 风格] 软加分提权
        if opt_lower in ["运动", "活力", "休闲运动", "运动风"]: boost_style = "sporty"
        elif opt_lower in ["正式", "庄重", "商务", "得体"]: boost_style = "formal"
        elif opt_lower in ["休闲", "日常", "随性", "慵懒", "百搭"]: boost_style = "casual"
        elif opt_lower in ["复古", "港风", "古着", "经典"]: boost_style = "vintage"
        elif opt_lower in ["潮牌", "嘻哈", "酷飒", "机车"]: boost_style = "streetwear"
        elif opt_lower in ["约会", "浪漫", "温柔", "纯欲"]: boost_style = "romantic dating"
        elif opt_lower in ["极简", "高级感", "性冷淡风", "老钱风", "clean fit"]: boost_style = "minimalist"
        elif opt_lower in ["甜美", "可爱", "仙气", "少女", "公主"]: boost_style = "sweet"
        elif opt_lower in ["性感", "辣妹", "紧身", "夜店", "y2k"]: boost_style = "sexy"
        
        # 🎨 [CLIP 高维渲染词]
        vibe_mapping = {
            "鲜艳": "highly colorful and bright", "暗黑": "dark, black, and gothic",
            "黑白": "classic black and white", "素雅": "simple, elegant and plain colored",
            "碎花": "floral pattern", "条纹": "striped pattern", "格子": "plaid pattern",
            "豹纹": "leopard print", "纯棉": "comfortable pure cotton", "丝绸": "smooth silk",
            "高级感": "high-end luxury aesthetic", "老钱风": "old money aesthetic", "辣妹": "sexy Y2K fashion"
        }
        if opt_lower in vibe_mapping:
            vibe_words.append(vibe_mapping[opt_lower])

    if boost_scene and boost_scene not in vibe_words: vibe_words.append(boost_scene)
    if boost_style and boost_style not in vibe_words: vibe_words.append(boost_style)
    if not vibe_words: vibe_words.append("a beautifully matched clothing outfit")

    vibe_query = f"A highly aesthetic fashion look featuring: {' '.join(vibe_words)}"
    
    print(f"🎯 物理锁定 -> 季节: {req_season} | 强制品类: {req_category} | 绝对颜色: {req_color}")
    print(f"🚀 提权锁定 -> 场景: {boost_scene} | 风格: {boost_style}")
    print(f"🎨 审美渲染 -> [{vibe_query}]")

    clip_model, _ = clip.load("ViT-L/14", device=device)
    clip_model.eval()
    with torch.no_grad():
        text_tokens = clip.tokenize([vibe_query]).to(device)
        query_vector = clip_model.encode_text(text_tokens).float()
        query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, brand, price, style, color, season, item_category, scene, super_vector::text FROM clothing_features;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    tops, bottoms, ops = [], [], []
    
    for row in rows:
        filename, brand, price, style, color, season, category, scene, vec_str = row
        
        # 🛡️ 100% 物理死线拦截 (季节)
        if req_season and req_season not in season: continue
            
        # 🛡️ 100% 物理死线拦截 (品类)
        if req_category == "one_piece" and category != "one_piece": continue

        if req_color and req_color not in color: continue

        vec_list = json.loads(vec_str)
        tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
        
        # 🎨 计算审美基础分
        semantic_score = torch.matmul(tensor_vec, query_vector).item()
        
        # 🚀 场景与风格提权
        bonus = 0.0
        if boost_scene and boost_scene in scene: bonus += 0.25
        if boost_style and boost_style in style: bonus += 0.20
        
        if not req_color and color in ["black", "white", "gray"]:
            bonus -= 0.08 
            
        final_score = semantic_score + bonus
        
        item = {
            "filename": filename, "brand": brand, "price": price, 
            "vector": tensor_vec, "semantic_score": final_score,
            "display_tags": f"品类:{category} | 季节:{season}\n场景:{scene} | 风格:{style}"
        }
        
        if category == "top": tops.append(item)
        elif category == "bottom": bottoms.append(item)
        elif category == "one_piece": ops.append(item)

    if not tops and not bottoms and not ops:
        print("💥 完蛋！图库里没有同时满足这些硬指标的衣服！")
        return

    final_outfits = []
    
    if req_category != "one_piece" and tops and bottoms:
        # 接入 MMR：选出 15 件高分且极其“和而不同”的单品，拒绝海王！
        best_tops = apply_mmr(tops, top_n=15, diversity_weight=0.5)
        best_bottoms = apply_mmr(bottoms, top_n=15, diversity_weight=0.5)
        
        t_vecs = torch.stack([t["vector"] for t in best_tops])
        b_vecs = torch.stack([b["vector"] for b in best_bottoms])
        t_scores = torch.tensor([t["semantic_score"] for t in best_tops])
        b_scores = torch.tensor([b["semantic_score"] for b in best_bottoms])
        
        raw_harmony = torch.matmul(t_vecs, b_vecs.T)
        harmony_score = torch.exp(-((raw_harmony - 0.6) ** 2) / (2 * 0.2 ** 2))
        combo_scores = (0.45 * t_scores.unsqueeze(1)) + (0.45 * b_scores.unsqueeze(0)) + (0.10 * harmony_score)
        
        # 放大备选池到 100，给去重留足空间
        flat_scores = combo_scores.flatten()
        top_combo_indices = torch.topk(flat_scores, min(100, len(flat_scores))).indices
        
        # 👑 频率控制锁：记录每件衣服的出场次数
        top_usage_count = {}
        bottom_usage_count = {}
        
        for flat_idx in top_combo_indices:
            t_idx = flat_idx // len(best_bottoms)
            b_idx = flat_idx % len(best_bottoms)
            
            candidate_top = best_tops[t_idx]
            candidate_bottom = best_bottoms[b_idx]
            
            top_fname = candidate_top['filename']
            bot_fname = candidate_bottom['filename']
            
            if top_usage_count.get(top_fname, 0) >= 2 or bottom_usage_count.get(bot_fname, 0) >= 2:
                continue
                
            # 记录在案，出场次数 +1
            top_usage_count[top_fname] = top_usage_count.get(top_fname, 0) + 1
            bottom_usage_count[bot_fname] = bottom_usage_count.get(bot_fname, 0) + 1
            
            final_outfits.append({
                "type": "combo", "score": combo_scores[t_idx, b_idx].item(),
                "top": candidate_top, "bottom": candidate_bottom
            })
            
            # 留足 10 套备选，满足前端 top_k 展示需求后直接收工
            if len(final_outfits) >= 10:
                break

    if ops:
        best_ops = apply_mmr(ops, top_n=10, diversity_weight=0.6)
        for op_item in best_ops:
            final_outfits.append({
                "type": "one_piece", "score": op_item["semantic_score"], "item": op_item
            })
    final_outfits.sort(key=lambda x: x["score"], reverse=True)
    best_outfits = final_outfits[:top_k]

    fig, axes = plt.subplots(nrows=len(best_outfits), ncols=2, figsize=(11, 4.8 * len(best_outfits)))
    fig.suptitle(f"🤖 V7.0 结构化推荐大屏 | UI 选项: {' | '.join(ui_options)}", fontsize=15, fontweight='bold', y=0.98)
    if len(best_outfits) == 1: axes = np.array([axes])

    for i, outfit in enumerate(best_outfits):
        score_text = f"匹配度: {outfit['score']:.4f}"
        if outfit["type"] == "combo":
            t, b = outfit["top"], outfit["bottom"]
            
            ax_top = axes[i, 0]
            try: ax_top.imshow(Image.open(os.path.join(img_base_dir, t['filename'])).convert('RGB'))
            except: ax_top.text(0.5, 0.5, '图丢了', ha='center')
            ax_top.axis('off')
            ax_top.set_title(f"👑 搭配 {i+1} (上衣) | ¥{t['price']}", color='darkred', fontsize=11, fontweight='bold')
            ax_top.text(0.5, -0.1, t['display_tags'], transform=ax_top.transAxes, ha='center', fontsize=9, color='blue', linespacing=1.5)
            
            ax_bot = axes[i, 1]
            try: ax_bot.imshow(Image.open(os.path.join(img_base_dir, b['filename'])).convert('RGB'))
            except: ax_bot.text(0.5, 0.5, '图丢了', ha='center')
            ax_bot.axis('off')
            ax_bot.set_title(f"({score_text})\n搭配 {i+1} (下装) | ¥{b['price']}", color='darkgreen', fontsize=11, fontweight='bold')
            ax_bot.text(0.5, -0.1, b['display_tags'], transform=ax_bot.transAxes, ha='center', fontsize=9, color='blue', linespacing=1.5)

        else:
            op = outfit["item"]
            ax_op = axes[i, 0]
            try: ax_op.imshow(Image.open(os.path.join(img_base_dir, op['filename'])).convert('RGB'))
            except: ax_op.text(0.5, 0.5, '图丢了', ha='center')
            ax_op.axis('off')
            ax_op.set_title(f"👑 连体方案 {i+1}\n{score_text} | ¥{op['price']}", color='purple', fontweight='bold', fontsize=11)
            ax_op.text(0.5, -0.1, op['display_tags'], transform=ax_op.transAxes, ha='center', fontsize=9, color='blue', linespacing=1.5)
            
            ax_blank = axes[i, 1]
            ax_blank.axis('off')
            ax_blank.text(0.5, 0.5, "👗 完美单品\n无需搭配", ha='center', va='center', fontsize=13, color='gray')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    img_dir = r"D:\dress_recommender\images\images" 
    
    ui_options_1 = ["夏", "海岛", "鲜艳", "碎花裙"]
    ui_options_2 = ["正式", "婚礼"]
    ui_options_3 = ["春","约会","公园"]
    ui_options_4 = ["春","运动","公园"]
    ui_options_5 = ["夏", "日常", "休闲"]
    ui_options_6 = ["夏", "运动", "户外运动","粉色"]
    recommend_from_structured_db(ui_options_1, img_dir, top_k=4)