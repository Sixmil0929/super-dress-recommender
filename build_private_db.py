# import os
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import clip
# import pandas as pd
# import psycopg2
# import torchvision.transforms as T
# from PIL import Image

# # ==========================================
# # 1. 核心融合模块：完全体 ATF
# # ==========================================
# class DualPathATF(nn.Module):
#     def __init__(self, clip_dim=768, dino_dim=1024, embed_dim=768, num_heads=8):
#         super().__init__()
#         self.proj_clip = nn.Linear(clip_dim, embed_dim)
#         self.proj_dino = nn.Linear(dino_dim, embed_dim)
#         self.self_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
#         self.norm = nn.LayerNorm(embed_dim)
#         self.gate_net = nn.Sequential(nn.Linear(embed_dim * 2, embed_dim), nn.Sigmoid())
#         self.fusion_norm = nn.LayerNorm(embed_dim)

#     def forward(self, f_clip, f_dino):
#         q_clip = self.proj_clip(f_clip)
#         q_dino = self.proj_dino(f_dino)
#         seq = torch.stack([q_clip, q_dino], dim=1) 
#         attn_out, _ = self.self_attn(query=seq, key=seq, value=seq)
#         seq_out = self.norm(seq + attn_out)
#         fused_clip = seq_out[:, 0, :]
#         fused_dino = seq_out[:, 1, :]
#         g = self.gate_net(torch.cat([fused_clip, fused_dino], dim=-1))
#         fused_features = g * fused_clip + (1 - g) * fused_dino
#         return self.fusion_norm(fused_features)

# # ==========================================
# # 2. 环境与模型初始化
# # ==========================================
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"🚀 正在使用 {device} 启动 V6.1 场景赋能建库引擎...")

# # 👇 【注意修改这里的路径】
# csv_path = r'D:\dress_recommender\P1_Dataset\P1_Dataset.csv'
# img_base_dir = r'D:\dress_recommender\P1_Dataset\images'
# weight_path = r'D:\dress_recommender\weights\atf_epoch_25.pth'

# clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)
# clip_model.eval()

# dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitl14', pretrained=True).to(device)
# dino_model.eval()
# dino_transform = T.Compose([
#     T.Resize((518, 518), interpolation=T.InterpolationMode.BICUBIC),
#     T.ToTensor(),
#     T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
# ])

# atf_model = DualPathATF().to(device)
# atf_model.load_state_dict(torch.load(weight_path, map_location=device))
# atf_model.eval()

# # ==========================================
# # 3. 🎯 V6.1 核心重构：加入独立场景池！
# # ==========================================
# TAG_POOLS = {
#     "style": ["sporty", "formal", "casual", "vintage", "streetwear", "romantic dating", "business casual", "minimalist", "outdoor", "sweet", "sexy"],
#     "color": ["black", "white", "gray", "red", "blue", "green", "yellow", "pink", "brown", "purple", "khaki", "multi-color"],
#     "season": ["spring", "summer", "autumn", "winter"],
#     "category": ["top wear", "bottom wear", "one-piece dress or jumpsuit"],
#     # 🌴 你的神级构想：树状场景池！
#     "scene": ["office workplace", "formal banquet or wedding", "home relaxing", "indoor gym", 
#               "beach vacation", "park camping", "street shopping", "outdoor sports"]
# }

# text_features_dict = {}
# with torch.no_grad():
#     for key, pool in TAG_POOLS.items():
#         # 💡 针对不同的属性，采用不同的考题 (Prompt)
#         if key == "scene":
#             prompts = [f"a clothing outfit perfectly suitable for {t}" for t in pool]
#         elif key == "color":
#             prompts = [f"a clothing item in {t} color" for t in pool]
#         else:
#             prompts = [f"a photo of a {t} clothing item" for t in pool]
            
#         text_inputs = clip.tokenize(prompts).to(device)
#         features = clip_model.encode_text(text_inputs).float()
#         text_features_dict[key] = F.normalize(features, dim=-1)

# # ==========================================
# # 4. 数据库重构 (新增场景表头)
# # ==========================================
# print("🐘 正在连接 PostgreSQL，准备新增场景专属表头...")
# conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
# conn.autocommit = True
# cursor = conn.cursor()

# cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
# cursor.execute("DROP TABLE IF EXISTS clothing_features;")

# cursor.execute("""
#     CREATE TABLE clothing_features (
#         filename TEXT PRIMARY KEY,
#         brand TEXT,
#         price REAL,
#         gender TEXT,
#         has_model TEXT,
#         style TEXT,          
#         color TEXT,          
#         season TEXT,         
#         item_category TEXT,  
#         scene TEXT,          -- 🌟 终极独立表头：穿着场景！
#         super_vector vector(768)
#     );
# """)
# print("✅ 带有 [Scene] 格子的终极数据库表已就绪！")

# # ==========================================
# # 5. 读取 CSV 并进行【5项全能专项考试】
# # ==========================================
# try:
#     df = pd.read_csv(csv_path, encoding='utf-8-sig')
# except UnicodeDecodeError:
#     df = pd.read_csv(csv_path, encoding='gbk')

# rename_map = {c: 'Filename' for c in df.columns if str(c).lower().strip() in ['filename', 'file_name', '图片名']}
# rename_map.update({c: 'Brand' for c in df.columns if str(c).lower().strip() in ['brand', '品牌']})
# rename_map.update({c: 'Price' for c in df.columns if str(c).lower().strip() in ['price', '价格']})
# rename_map.update({c: 'Gender' for c in df.columns if str(c).lower().strip() in ['gender', '性别']})
# rename_map.update({c: 'Has_Model' for c in df.columns if str(c).lower().strip() in ['has_model', '模特']})
# df = df.rename(columns=rename_map)

# if 'Brand' not in df.columns: df['Brand'] = 'Unknown'
# if 'Price' not in df.columns: df['Price'] = 0.0
# if 'Gender' not in df.columns: df['Gender'] = 'Unknown'
# if 'Has_Model' not in df.columns: df['Has_Model'] = 'Unknown'

# print(f"🔥 开始进行 V6.1 场景赋能打标入库，共 {len(df)} 张图片...")

# for index, row in df.iterrows():
#     img_name = str(row['Filename']).strip()
#     img_path = os.path.join(img_base_dir, img_name)
    
#     if not os.path.exists(img_path): continue

#     try:
#         raw_img = Image.open(img_path).convert('RGB')
#         img_clip = clip_preprocess(raw_img).unsqueeze(0).to(device)
#         img_dino = dino_transform(raw_img).unsqueeze(0).to(device)
        
#         with torch.no_grad():
#             raw_f_clip = clip_model.encode_image(img_clip)
#             raw_f_dino = dino_model(img_dino)
#             f_clip = F.normalize(raw_f_clip, dim=-1).float()
#             f_dino = F.normalize(raw_f_dino, dim=-1).float()
            
#             final_tags = {}
            
#             # 1. 风格 (Top 2)
#             sim_style = torch.matmul(f_clip, text_features_dict["style"].T)[0]
#             top_styles = [TAG_POOLS["style"][i] for i in sim_style.topk(2).indices]
#             final_tags["style"] = ", ".join(top_styles)
            
#             # 2. 颜色 (Top 1)
#             sim_color = torch.matmul(f_clip, text_features_dict["color"].T)[0]
#             final_tags["color"] = TAG_POOLS["color"][sim_color.argmax().item()]
            
#             # 3. 季节 (Top 2)
#             sim_season = torch.matmul(f_clip, text_features_dict["season"].T)[0]
#             top_seasons = [TAG_POOLS["season"][i] for i in sim_season.topk(2).indices]
#             final_tags["season"] = ", ".join(top_seasons)
            
#             # 4. 品类 (Top 1 强制)
#             sim_cat = torch.matmul(f_clip, text_features_dict["category"].T)[0]
#             raw_cat = TAG_POOLS["category"][sim_cat.argmax().item()]
#             if "top" in raw_cat: standard_cat = "top"
#             elif "bottom" in raw_cat: standard_cat = "bottom"
#             else: standard_cat = "one_piece"
#             final_tags["category"] = standard_cat
            
#             # 5. 🌴 场景 (Top 2) - 为这件衣服赋予场景灵魂！
#             sim_scene = torch.matmul(f_clip, text_features_dict["scene"].T)[0]
#             top_scenes = [TAG_POOLS["scene"][i] for i in sim_scene.topk(2).indices]
#             final_tags["scene"] = ", ".join(top_scenes)
            
#             super_vector = atf_model(f_clip, f_dino)
#             super_vector = F.normalize(super_vector, dim=-1)
#             super_vector_list = super_vector.squeeze().cpu().tolist()
        
#         insert_query = """
#             INSERT INTO clothing_features 
#             (filename, brand, price, gender, has_model, style, color, season, item_category, scene, super_vector)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (filename) DO UPDATE 
#             SET brand = EXCLUDED.brand, price = EXCLUDED.price, 
#                 style = EXCLUDED.style, color = EXCLUDED.color,
#                 season = EXCLUDED.season, item_category = EXCLUDED.item_category,
#                 scene = EXCLUDED.scene, super_vector = EXCLUDED.super_vector;
#         """
#         try: price = float(row['Price']) if pd.notna(row['Price']) else 0.0
#         except: price = 0.0
            
#         cursor.execute(insert_query, (
#             img_name, str(row['Brand']), price, str(row['Gender']), str(row['Has_Model']), 
#             final_tags["style"], final_tags["color"], final_tags["season"], 
#             final_tags["category"], final_tags["scene"], super_vector_list
#         ))
        
#         if (index + 1) % 10 == 0:
#             print(f"✅ [{index+1}/{len(df)}] | 品类:{final_tags['category']} | 颜色:{final_tags['color']} | 🌴场景:{final_tags['scene']}")

#     except Exception as e:
#         print(f"❌ 处理 {img_name} 时发生错误: {e}")

# cursor.close()
# conn.close()
# print("\n" + "="*50)
# print("🎉 场景赋能全部完成！每件衣服都找到了属于它的归宿！")
# print("="*50)


# import os
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import clip
# import pandas as pd
# import psycopg2
# import torchvision.transforms as T
# from PIL import Image

# # ==========================================
# # 👗 终极一刀切建库脚本 (build_private_db.py)
# # ==========================================

# class DualPathATF(nn.Module):
#     def __init__(self, clip_dim=768, dino_dim=1024, embed_dim=768, num_heads=8):
#         super().__init__()
#         self.proj_clip = nn.Linear(clip_dim, embed_dim)
#         self.proj_dino = nn.Linear(dino_dim, embed_dim)
#         self.self_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
#         self.norm = nn.LayerNorm(embed_dim)
#         self.gate_net = nn.Sequential(nn.Linear(embed_dim * 2, embed_dim), nn.Sigmoid())
#         self.fusion_norm = nn.LayerNorm(embed_dim)

#     def forward(self, f_clip, f_dino):
#         q_clip = self.proj_clip(f_clip)
#         q_dino = self.proj_dino(f_dino)
#         seq = torch.stack([q_clip, q_dino], dim=1) 
#         attn_out, _ = self.self_attn(query=seq, key=seq, value=seq)
#         seq_out = self.norm(seq + attn_out)
#         fused_clip = seq_out[:, 0, :]
#         fused_dino = seq_out[:, 1, :]
#         g = self.gate_net(torch.cat([fused_clip, fused_dino], dim=-1))
#         fused_features = g * fused_clip + (1 - g) * fused_dino
#         return self.fusion_norm(fused_features)

# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"🚀 正在使用 {device} 启动终极免维护建库引擎...")

# # 👇 确保这里的路径是你的真实路径
# csv_path = r'D:\dress_recommender\P4_Dataset\P4_Dataset.csv'
# img_base_dir = r'D:\dress_recommender\P4_Dataset\images'
# weight_path = r'D:\dress_recommender\weights\atf_epoch_25.pth'

# clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)
# clip_model.eval()

# dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitl14', pretrained=True).to(device)
# dino_model.eval()
# dino_transform = T.Compose([
#     T.Resize((518, 518), interpolation=T.InterpolationMode.BICUBIC),
#     T.ToTensor(),
#     T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
# ])

# atf_model = DualPathATF().to(device)
# atf_model.load_state_dict(torch.load(weight_path, map_location=device))
# atf_model.eval()

# # ==========================================
# # 👑 史上最全的终极实体词典 (一次性写死，永不修改)
# # ==========================================
# TOP_ITEMS = [
#     "T-shirt", "shirt", "blouse", "sweater", "hoodie", "sweatshirt", 
#     "jacket", "coat", "trench coat", "puffer jacket", "suit blazer", 
#     "vest", "tank top", "camisole", "crop top", "cardigan", "polo shirt"
# ]

# BOTTOM_ITEMS = [
#     "jeans", "casual trousers", "cargo pants", "sweatpants", "leggings", 
#     "wide-leg pants", "suit pants", "shorts", "hot pants", 
#     "skirt", "mini skirt", "midi skirt", "pleated skirt", "pencil skirt", "A-line skirt"
# ]

# ONE_PIECE_ITEMS = [
#     "dress", "jumpsuit", "romper", "evening gown", "maxi dress", 
#     "slip dress", "bodycon dress", "floral dress", "cheongsam", "overalls"
# ]

# TAG_POOLS = {
#     "style": ["sporty", "formal", "casual", "vintage", "streetwear", "romantic dating", "business casual", "minimalist", "outdoor", "sweet", "sexy"],
#     "color": ["black", "white", "gray", "red", "blue", "green", "yellow", "pink", "brown", "purple", "khaki", "multi-color"],
#     "season": ["spring", "summer", "autumn", "winter"],
#     "scene": ["office workplace", "formal banquet or wedding", "home relaxing", "indoor gym", "beach vacation", "park camping", "street shopping", "outdoor sports"],
#     "category": TOP_ITEMS + BOTTOM_ITEMS + ONE_PIECE_ITEMS
# }

# text_features_dict = {}
# with torch.no_grad():
#     for key, pool in TAG_POOLS.items():
#         if key == "scene":
#             prompts = [f"a clothing outfit perfectly suitable for {t}" for t in pool]
#         elif key == "color":
#             prompts = [f"a clothing item in {t} color" for t in pool]
#         else:
#             prompts = [f"a photo of a {t} clothing item" for t in pool]
            
#         text_inputs = clip.tokenize(prompts).to(device)
#         features = clip_model.encode_text(text_inputs).float()
#         text_features_dict[key] = F.normalize(features, dim=-1)

# # ==========================================
# # 数据库连接 (静默更新模式)
# # ==========================================
# print("🐘 正在连接 PostgreSQL...")
# conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
# conn.autocommit = True
# cursor = conn.cursor()

# cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
# # 表结构已经建好了，我们注释掉炸表代码，直接用 ON CONFLICT DO UPDATE 刷新数据
# # cursor.execute("DROP TABLE IF EXISTS clothing_features;")
# # cursor.execute("""
# #     CREATE TABLE clothing_features (
# #         filename TEXT PRIMARY KEY,
# #         brand TEXT, price REAL, gender TEXT, has_model TEXT,
# #         style TEXT, color TEXT, season TEXT, item_category TEXT, scene TEXT,
# #         super_vector vector(768)
# #     );
# # """)

# # ==========================================
# # 开始处理并暴力纠正分类
# # ==========================================
# try: df = pd.read_csv(csv_path, encoding='utf-8-sig')
# except: df = pd.read_csv(csv_path, encoding='gbk')

# rename_map = {c: 'Filename' for c in df.columns if str(c).lower().strip() in ['filename', 'file_name', '图片名']}
# rename_map.update({c: 'Brand' for c in df.columns if str(c).lower().strip() in ['brand', '品牌']})
# rename_map.update({c: 'Price' for c in df.columns if str(c).lower().strip() in ['price', '价格']})
# rename_map.update({c: 'Gender' for c in df.columns if str(c).lower().strip() in ['gender', '性别']})
# rename_map.update({c: 'Has_Model' for c in df.columns if str(c).lower().strip() in ['has_model', '模特']})
# df = df.rename(columns=rename_map)

# if 'Brand' not in df.columns: df['Brand'] = 'Unknown'
# if 'Price' not in df.columns: df['Price'] = 0.0
# if 'Gender' not in df.columns: df['Gender'] = 'Unknown'
# if 'Has_Model' not in df.columns: df['Has_Model'] = 'Unknown'

# print(f"🔥 开始进行终极洗库，共 {len(df)} 张图片...")

# for index, row in df.iterrows():
#     img_name = str(row['Filename']).strip()
#     img_path = os.path.join(img_base_dir, img_name)
    
#     if not os.path.exists(img_path): continue

#     try:
#         raw_img = Image.open(img_path).convert('RGB')
#         img_clip = clip_preprocess(raw_img).unsqueeze(0).to(device)
#         img_dino = dino_transform(raw_img).unsqueeze(0).to(device)
        
#         with torch.no_grad():
#             f_clip = F.normalize(clip_model.encode_image(img_clip), dim=-1).float()
#             f_dino = F.normalize(dino_model(img_dino), dim=-1).float()
#             final_tags = {}
            
#             # 1. 风格 (Top 2)
#             sim_style = torch.matmul(f_clip, text_features_dict["style"].T)[0]
#             final_tags["style"] = ", ".join([TAG_POOLS["style"][i] for i in sim_style.topk(2).indices])
            
#             # 2. 颜色 (Top 1)
#             sim_color = torch.matmul(f_clip, text_features_dict["color"].T)[0]
#             final_tags["color"] = TAG_POOLS["color"][sim_color.argmax().item()]
            
#             # 3. 季节 (Top 2)
#             sim_season = torch.matmul(f_clip, text_features_dict["season"].T)[0]
#             final_tags["season"] = ", ".join([TAG_POOLS["season"][i] for i in sim_season.topk(2).indices])
            
#             # 4. 场景 (Top 2)
#             sim_scene = torch.matmul(f_clip, text_features_dict["scene"].T)[0]
#             final_tags["scene"] = ", ".join([TAG_POOLS["scene"][i] for i in sim_scene.topk(2).indices])
            
#            # ==========================================
#             # 5. 👑 终极小队平均分隔离 (彻底抹杀偶然高分错判)
#             # ==========================================
#             sim_cat = torch.matmul(f_clip, text_features_dict["category"].T)[0]
            
#             # 拿到三个大数组在 TAG_POOLS["category"] 里的具体位置(索引)
#             top_idx = [TAG_POOLS["category"].index(i) for i in TOP_ITEMS]
#             bot_idx = [TAG_POOLS["category"].index(i) for i in BOTTOM_ITEMS]
#             op_idx = [TAG_POOLS["category"].index(i) for i in ONE_PIECE_ITEMS]
            
#             # 取出每个小队的所有得分
#             scores_top = sim_cat[top_idx]
#             scores_bot = sim_cat[bot_idx]
#             scores_op = sim_cat[op_idx]
            
#             # 算法核心：取每个小队的前 3 名得分，算平均分！(防止冷门词拖后腿，也防止单一词作弊)
#             avg_top = scores_top.topk(min(3, len(scores_top))).values.mean().item()
#             avg_bot = scores_bot.topk(min(3, len(scores_bot))).values.mean().item()
#             avg_op = scores_op.topk(min(3, len(scores_op))).values.mean().item()
            
#             # 团队总分大比拼！
#             if avg_bot > avg_top and avg_bot > avg_op:
#                 final_tags["category"] = "bottom"
#             elif avg_top > avg_bot and avg_top > avg_op:
#                 final_tags["category"] = "top"
#             else:
#                 final_tags["category"] = "one_piece"
            
#             # 生成超级向量
#             super_vector_list = F.normalize(atf_model(f_clip, f_dino), dim=-1).squeeze().cpu().tolist()
        
#         # 插入或静默更新数据库
#         insert_query = """
#             INSERT INTO clothing_features 
#             (filename, brand, price, gender, has_model, style, color, season, item_category, scene, super_vector)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (filename) DO UPDATE 
#             SET brand = EXCLUDED.brand, price = EXCLUDED.price, 
#                 style = EXCLUDED.style, color = EXCLUDED.color,
#                 season = EXCLUDED.season, item_category = EXCLUDED.item_category,
#                 scene = EXCLUDED.scene, super_vector = EXCLUDED.super_vector;
#         """
#         try: price = float(row['Price']) if pd.notna(row['Price']) else 0.0
#         except: price = 0.0
            
#         cursor.execute(insert_query, (
#             img_name, str(row['Brand']), price, str(row['Gender']), str(row['Has_Model']), 
#             final_tags["style"], final_tags["color"], final_tags["season"], 
#             final_tags["category"], final_tags["scene"], super_vector_list
#         ))
        
#         if (index + 1) % 10 == 0:
#             print(f"✅ [{index+1}/{len(df)}] | 品类:{final_tags['category']} | 颜色:{final_tags['color']} | 🌴场景:{final_tags['scene']}")

#     except Exception as e:
#         print(f"❌ 处理 {img_name} 报错: {e}")

# cursor.close()
# conn.close()
# print("\n🎉 洗库彻底结束！")


import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import clip
import pandas as pd
import psycopg2
import torchvision.transforms as T
from PIL import Image

class DualPathATF(nn.Module):
    def __init__(self, clip_dim=768, dino_dim=1024, embed_dim=768, num_heads=8):
        super().__init__()
        self.proj_clip = nn.Linear(clip_dim, embed_dim)
        self.proj_dino = nn.Linear(dino_dim, embed_dim)
        self.self_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
        self.norm = nn.LayerNorm(embed_dim)
        self.gate_net = nn.Sequential(nn.Linear(embed_dim * 2, embed_dim), nn.Sigmoid())
        self.fusion_norm = nn.LayerNorm(embed_dim)

    def forward(self, f_clip, f_dino):
        q_clip = self.proj_clip(f_clip)
        q_dino = self.proj_dino(f_dino)
        seq = torch.stack([q_clip, q_dino], dim=1) 
        attn_out, _ = self.self_attn(query=seq, key=seq, value=seq)
        seq_out = self.norm(seq + attn_out)
        fused_clip = seq_out[:, 0, :]
        fused_dino = seq_out[:, 1, :]
        g = self.gate_net(torch.cat([fused_clip, fused_dino], dim=-1))
        fused_features = g * fused_clip + (1 - g) * fused_dino
        return self.fusion_norm(fused_features)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 正在使用 {device} 启动终极免维护建库引擎...")

csv_path = r'D:\dress_recommender\P5_Dataset\P5_Dataset.csv'
img_base_dir = r'D:\dress_recommender\P5_Dataset\images'
weight_path = r'D:\dress_recommender\weights\atf_epoch_25.pth'

clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)
clip_model.eval()

dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitl14', pretrained=True).to(device)
dino_model.eval()
dino_transform = T.Compose([
    T.Resize((518, 518), interpolation=T.InterpolationMode.BICUBIC),
    T.ToTensor(),
    T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
])

atf_model = DualPathATF().to(device)
atf_model.load_state_dict(torch.load(weight_path, map_location=device))
atf_model.eval()

TOP_ITEMS = [
    "T-shirt", "shirt", "blouse", "sweater", "hoodie", "sweatshirt", 
    "jacket", "coat", "trench coat", "puffer jacket", "suit blazer", 
    "vest", "tank top", "camisole", "crop top", "cardigan", "polo shirt"
]

BOTTOM_ITEMS = [
    "jeans", "casual trousers", "cargo pants", "sweatpants", "leggings", 
    "wide-leg pants", "suit pants", "shorts", "hot pants", 
    "skirt", "mini skirt", "midi skirt", "pleated skirt", "pencil skirt", "A-line skirt"
]

ONE_PIECE_ITEMS = [
    "dress", "jumpsuit", "romper", "evening gown", "maxi dress", 
    "slip dress", "bodycon dress", "floral dress", "cheongsam", "overalls"
]

TAG_POOLS = {
    "style": ["sporty", "formal", "casual", "vintage", "streetwear", "romantic dating", "business casual", "minimalist", "outdoor", "sweet", "sexy"],
    "color": ["black", "white", "gray", "red", "blue", "green", "yellow", "pink", "brown", "purple", "khaki", "multi-color"],
    "season": ["spring", "summer", "autumn", "winter"],
    "scene": ["office workplace", "formal banquet or wedding", "home relaxing", "indoor gym", "beach vacation", "park camping", "street shopping", "outdoor sports"],
    "category": TOP_ITEMS + BOTTOM_ITEMS + ONE_PIECE_ITEMS
}

text_features_dict = {}
with torch.no_grad():
    for key, pool in TAG_POOLS.items():
        if key == "scene":
            prompts = [f"a clothing outfit perfectly suitable for {t}" for t in pool]
        elif key == "color":
            prompts = [f"a clothing item in {t} color" for t in pool]
        else:
            prompts = [f"a photo of a {t} clothing item" for t in pool]
            
        text_inputs = clip.tokenize(prompts).to(device)
        features = clip_model.encode_text(text_inputs).float()
        text_features_dict[key] = F.normalize(features, dim=-1)

# ==========================================
# 数据库连接 (静默更新模式)
# ==========================================
print("🐘 正在连接 PostgreSQL...")
conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
conn.autocommit = True
cursor = conn.cursor()

cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
try: df = pd.read_csv(csv_path, encoding='utf-8-sig')
except: df = pd.read_csv(csv_path, encoding='gbk')

rename_map = {c: 'Filename' for c in df.columns if str(c).lower().strip() in ['filename', 'file_name', '图片名']}
rename_map.update({c: 'Brand' for c in df.columns if str(c).lower().strip() in ['brand', '品牌']})
rename_map.update({c: 'Price' for c in df.columns if str(c).lower().strip() in ['price', '价格']})
rename_map.update({c: 'Gender' for c in df.columns if str(c).lower().strip() in ['gender', '性别']})
rename_map.update({c: 'Has_Model' for c in df.columns if str(c).lower().strip() in ['has_model', '模特']})
df = df.rename(columns=rename_map)

if 'Brand' not in df.columns: df['Brand'] = 'Unknown'
if 'Price' not in df.columns: df['Price'] = 0.0
if 'Gender' not in df.columns: df['Gender'] = 'Unknown'
if 'Has_Model' not in df.columns: df['Has_Model'] = 'Unknown'

print(f"🔥 开始进行终极洗库，共 {len(df)} 张图片...")

for index, row in df.iterrows():
    img_name = str(row['Filename']).strip()
    img_path = os.path.join(img_base_dir, img_name)
    
    if not os.path.exists(img_path): continue

    try:
        raw_img = Image.open(img_path).convert('RGB')
        img_clip = clip_preprocess(raw_img).unsqueeze(0).to(device)
        img_dino = dino_transform(raw_img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            f_clip = F.normalize(clip_model.encode_image(img_clip), dim=-1).float()
            f_dino = F.normalize(dino_model(img_dino), dim=-1).float()
            final_tags = {}
            
            # 1. 风格 (Top 2)
            sim_style = torch.matmul(f_clip, text_features_dict["style"].T)[0]
            final_tags["style"] = ", ".join([TAG_POOLS["style"][i] for i in sim_style.topk(2).indices])
            
            # 2. 颜色 (Top 1)
            sim_color = torch.matmul(f_clip, text_features_dict["color"].T)[0]
            final_tags["color"] = TAG_POOLS["color"][sim_color.argmax().item()]
            
            sim_season = torch.matmul(f_clip, text_features_dict["season"].T)[0]
            sorted_indices = sim_season.argsort(descending=True)
            first_season = TAG_POOLS["season"][sorted_indices[0]]
            valid_seasons = [first_season]
            
            for idx in sorted_indices[1:]:
                next_season = TAG_POOLS["season"][idx]
                if (first_season == "summer" and next_season == "winter") or \
                   (first_season == "winter" and next_season == "summer"):
                    continue
                valid_seasons.append(next_season)
                if len(valid_seasons) == 2:
                    break
                    
            final_tags["season"] = ", ".join(valid_seasons)
            
            # 4. 场景 (Top 2)
            sim_scene = torch.matmul(f_clip, text_features_dict["scene"].T)[0]
            final_tags["scene"] = ", ".join([TAG_POOLS["scene"][i] for i in sim_scene.topk(2).indices])
            
            sim_cat = torch.matmul(f_clip, text_features_dict["category"].T)[0]
            
            # 拿到三个大数组在 TAG_POOLS["category"] 里的具体位置(索引)
            top_idx = [TAG_POOLS["category"].index(i) for i in TOP_ITEMS]
            bot_idx = [TAG_POOLS["category"].index(i) for i in BOTTOM_ITEMS]
            op_idx = [TAG_POOLS["category"].index(i) for i in ONE_PIECE_ITEMS]
            
            # 取出每个小队的所有得分
            scores_top = sim_cat[top_idx]
            scores_bot = sim_cat[bot_idx]
            scores_op = sim_cat[op_idx]
            
            # 算法核心：取每个小队的前 3 名得分，算平均分！(防止冷门词拖后腿，也防止单一词作弊)
            avg_top = scores_top.topk(min(3, len(scores_top))).values.mean().item()
            avg_bot = scores_bot.topk(min(3, len(scores_bot))).values.mean().item()
            avg_op = scores_op.topk(min(3, len(scores_op))).values.mean().item()
            
            # 团队总分大比拼！
            if avg_bot > avg_top and avg_bot > avg_op:
                final_tags["category"] = "bottom"
            elif avg_top > avg_bot and avg_top > avg_op:
                final_tags["category"] = "top"
            else:
                final_tags["category"] = "one_piece"
            
            # 生成超级向量
            super_vector_list = F.normalize(atf_model(f_clip, f_dino), dim=-1).squeeze().cpu().tolist()
        
        # 插入或静默更新数据库
        insert_query = """
            INSERT INTO clothing_features 
            (filename, brand, price, gender, has_model, style, color, season, item_category, scene, super_vector)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (filename) DO UPDATE 
            SET brand = EXCLUDED.brand, price = EXCLUDED.price, 
                style = EXCLUDED.style, color = EXCLUDED.color,
                season = EXCLUDED.season, item_category = EXCLUDED.item_category,
                scene = EXCLUDED.scene, super_vector = EXCLUDED.super_vector;
        """
        try: price = float(row['Price']) if pd.notna(row['Price']) else 0.0
        except: price = 0.0
            
        cursor.execute(insert_query, (
            img_name, str(row['Brand']), price, str(row['Gender']), str(row['Has_Model']), 
            final_tags["style"], final_tags["color"], final_tags["season"], 
            final_tags["category"], final_tags["scene"], super_vector_list
        ))
        
        if (index + 1) % 10 == 0:
            print(f"✅ [{index+1}/{len(df)}] | 季节:{final_tags['season']} | 品类:{final_tags['category']} | 🌴场景:{final_tags['scene']}")

    except Exception as e:
        print(f"❌ 处理 {img_name} 报错: {e}")

cursor.close()
conn.close()
print("\n🎉 洗库彻底结束！")