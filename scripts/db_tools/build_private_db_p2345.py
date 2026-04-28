# import os
# import sys
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import clip
# import pandas as pd
# import psycopg2
# import torchvision.transforms as T
# from PIL import Image

# # ==========================================
# # 1. 核心融合模块：完全体 ATF (Epoch 25 版本)
# # ==========================================
# class DualPathATF(nn.Module):
#     def __init__(self, clip_dim=768, dino_dim=1024, embed_dim=768, num_heads=8):
#         super().__init__()
#         self.proj_clip = nn.Linear(clip_dim, embed_dim)
#         self.proj_dino = nn.Linear(dino_dim, embed_dim)
        
#         self.self_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
#         self.norm = nn.LayerNorm(embed_dim)
        
#         self.gate_net = nn.Sequential(
#             nn.Linear(embed_dim * 2, embed_dim),
#             nn.Sigmoid()
#         )
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
        
#         super_vector = self.fusion_norm(fused_features)
#         return super_vector

# # ==========================================
# # 2. 环境与模型初始化
# # ==========================================
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"🚀 正在使用 {device} 设备唤醒终极系统...")

# # 👇 【在此处修改】改成 P2, P3, P4 等队友的数据路径！
# csv_path = r'D:\dress_recommender\P5_Dataset\P5_Dataset.csv'
# img_base_dir = r'D:\dress_recommender\P5_Dataset\images'
# weight_path = r'D:\dress_recommender\weights\atf_epoch_25.pth'

# print("⏳ 正在加载 CLIP & DINOv2...")
# clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)
# clip_model.eval()

# dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitl14', pretrained=True).to(device)
# dino_model.eval()

# dino_transform = T.Compose([
#     T.Resize((518, 518), interpolation=T.InterpolationMode.BICUBIC),
#     T.ToTensor(),
#     T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
# ])

# print("🧠 正在加载黄金融合矩阵 (Epoch 25)...")
# atf_model = DualPathATF().to(device)
# if not os.path.exists(weight_path):
#     print(f"💥 致命错误：找不到模型权重 {weight_path}")
#     sys.exit()
# atf_model.load_state_dict(torch.load(weight_path, map_location=device))
# atf_model.eval()

# # ==========================================
# # 💎 V2.0 细粒度高阶超级标签池 (Tag Pool)
# # ==========================================
# tag_pool = [
#     # 风格与场景 (保持经典)
#     "sporty", "formal", "casual", "vintage", "streetwear", 
#     "romantic dating", "business casual", "minimalist", "outdoor", "sweet", "sexy",
    
#     # 材质 (增强质感)
#     "cotton", "denim", "leather", "knit", "silk", "chiffon",
    
#     # 👕 上装 (Tops - 极度细化)
#     "T-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", 
#     "tank top", "blouse", "cardigan", "suit blazer",
    
#     # 👖 下装 (Bottoms - 彻底解决短裤和裙子混淆)
#     "jeans", "casual trousers", "cargo pants", "shorts", "hot pants",
#     "pleated skirt", "A-line skirt", "pencil skirt", "midi skirt", "mini skirt",
    
#     # 👗 连体装 (One-Piece - 彻底剥离包臀裙与普通裙装)
#     "dress", "bodycon dress", "slip dress", "floral dress", "maxi dress", "jumpsuit",
    
#     # 季节
#     "spring", "summer", "autumn", "winter",
    
#     # 图案
#     "striped", "plaid", "floral", "solid color",
    
#     # 具体颜色
#     "black", "white", "gray", "red", "blue", 
#     "green", "yellow", "pink", "brown", "purple", "khaki"
# ]

# print("🏷️ 正在预计算 CLIP 文字标签向量...")
# text_prompts = [f"a photo of a {t} clothing item" for t in tag_pool]
# with torch.no_grad():
#     text_inputs = clip.tokenize(text_prompts).to(device)
#     tag_features = clip_model.encode_text(text_inputs).float()
#     tag_features = F.normalize(tag_features, dim=-1)

# # ==========================================
# # 4. 数据库连接与建表 (无损追加模式)
# # ==========================================
# print("🐘 正在连接 PostgreSQL 数据库...")
# conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
# conn.autocommit = True
# cursor = conn.cursor()

# cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS clothing_features (
#         filename TEXT PRIMARY KEY,
#         brand TEXT,
#         price REAL,
#         gender TEXT,
#         has_model TEXT,
#         clip_tags TEXT,
#         super_vector vector(768)
#     );
# """)
# print("✅ 数据库表 clothing_features 连接成功，准备进行数据的无损追加入库！")

# # ==========================================
# # 5. 读取 CSV 并进行【终极防幽灵字符处理】
# # ==========================================
# # 🛡️ 核心修复：优先使用 utf-8-sig 杀掉 BOM 头，再用 gbk 兜底
# try:
#     df = pd.read_csv(csv_path, encoding='utf-8-sig')
# except UnicodeDecodeError:
#     try:
#         df = pd.read_csv(csv_path, encoding='gbk')
#     except Exception as e:
#         print(f"💥 致命错误：CSV 编码彻底无法识别: {e}")
#         sys.exit()

# # 检查是否因为分隔符不对导致所有列挤成一坨
# if len(df.columns) == 1 and ',' in df.columns[0]:
#     print("⚠️ 警告：检测到分隔符异常，正在尝试强制重新切分表头...")
#     df = pd.read_csv(csv_path, encoding='utf-8-sig', sep=',')

# # 清洗表头大小写与空格
# rename_map = {}
# for c in df.columns:
#     c_lower = str(c).lower().strip()
#     if c_lower in ['filename', 'file_name', 'file name', '图片名']:
#         rename_map[c] = 'Filename'
#     elif c_lower in ['brand', '品牌']:
#         rename_map[c] = 'Brand'
#     elif c_lower in ['price', '价格']:
#         rename_map[c] = 'Price'
#     elif c_lower in ['gender', '性别']:
#         rename_map[c] = 'Gender'
#     elif c_lower in ['has_model', 'hasmodel', '是否有模特', '模特']:
#         rename_map[c] = 'Has_Model'

# df = df.rename(columns=rename_map)

# if 'Filename' not in df.columns:
#     print(f"💥 致命错误：幽灵清理完毕后依然找不到 Filename 列！当前列名: {list(df.columns)}")
#     sys.exit()
# if 'Brand' not in df.columns: df['Brand'] = 'Unknown'
# if 'Price' not in df.columns: df['Price'] = 0.0
# if 'Gender' not in df.columns: df['Gender'] = 'Unknown'
# if 'Has_Model' not in df.columns: df['Has_Model'] = 'Unknown'

# print(f"🔥 引擎全开！幽灵清理完毕，开始将 {len(df)} 张图片追加进总库，请稍候...")

# for index, row in df.iterrows():
#     img_name = str(row['Filename']).strip()
#     img_path = os.path.join(img_base_dir, img_name)
    
#     if not os.path.exists(img_path):
#         print(f"⚠️ 找不到图片: {img_path}，已跳过。")
#         continue

#     try:
#         raw_img = Image.open(img_path).convert('RGB')
        
#         img_clip = clip_preprocess(raw_img).unsqueeze(0).to(device)
#         img_dino = dino_transform(raw_img).unsqueeze(0).to(device)
        
#         with torch.no_grad():
#             raw_f_clip = clip_model.encode_image(img_clip)
#             raw_f_dino = dino_model(img_dino)
            
#             f_clip = F.normalize(raw_f_clip, dim=-1).float()
#             f_dino = F.normalize(raw_f_dino, dim=-1).float()
            
#             sim_matrix = torch.matmul(f_clip, tag_features.T)
#             top_indices = sim_matrix[0].topk(6).indices
#             clip_tags = ", ".join([tag_pool[i.item()] for i in top_indices])
            
#             super_vector = atf_model(f_clip, f_dino)
#             super_vector = F.normalize(super_vector, dim=-1)
#             super_vector_list = super_vector.squeeze().cpu().tolist()
        
#         insert_query = """
#             INSERT INTO clothing_features 
#             (filename, brand, price, gender, has_model, clip_tags, super_vector)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (filename) DO UPDATE 
#             SET brand = EXCLUDED.brand, price = EXCLUDED.price, 
#                 gender = EXCLUDED.gender, has_model = EXCLUDED.has_model,
#                 clip_tags = EXCLUDED.clip_tags, super_vector = EXCLUDED.super_vector;
#         """
#         try:
#             price = float(row['Price']) if pd.notna(row['Price']) else 0.0
#         except ValueError:
#             price = 0.0
            
#         cursor.execute(insert_query, (
#             img_name, str(row['Brand']), price, str(row['Gender']), str(row['Has_Model']), 
#             clip_tags, super_vector_list
#         ))
        
#         if (index + 1) % 10 == 0:
#             print(f"✅ 进度：追加成功 [{index + 1}/{len(df)}] | 最新提取标签: [{clip_tags}]")

#     except Exception as e:
#         print(f"❌ 处理 {img_name} 时发生错误: {e}")

# cursor.close()
# conn.close()
# print("\n" + "="*50)
# print("🎉 新批次数据已完美合并入总库！快去换下一批吧！")
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
# csv_path = r'D:\dress_recommender\P5_Dataset\P5_Dataset.csv'
# img_base_dir = r'D:\dress_recommender\P5_Dataset\images'
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

# # cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
# # cursor.execute("DROP TABLE IF EXISTS clothing_features;")

# # cursor.execute("""
# #     CREATE TABLE clothing_features (
# #         filename TEXT PRIMARY KEY,
# #         brand TEXT,
# #         price REAL,
# #         gender TEXT,
# #         has_model TEXT,
# #         style TEXT,          
# #         color TEXT,          
# #         season TEXT,         
# #         item_category TEXT,  
# #         scene TEXT,          -- 🌟 终极独立表头：穿着场景！
# #         super_vector vector(768)
# #     );
# # """)
# # print("✅ 带有 [Scene] 格子的终极数据库表已就绪！")

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


import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import clip
import pandas as pd
import psycopg2
import torchvision.transforms as T
from PIL import Image

# ==========================================
# 1. 核心融合模块：完全体 ATF
# ==========================================
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

# ==========================================
# 2. 环境与模型初始化
# ==========================================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 正在使用 {device} 启动 V6.1 场景赋能建库引擎...")

# 👇 【注意修改这里的路径】
csv_path = r'D:\dress_recommender\P1_Dataset\P1_Dataset.csv'
img_base_dir = r'D:\dress_recommender\P1_Dataset\images'
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

# ==========================================
# 3. 🎯 V6.1 核心重构：加入独立场景池！
# ==========================================
TAG_POOLS = {
    "style": ["sporty", "formal", "casual", "vintage", "streetwear", "romantic dating", "business casual", "minimalist", "outdoor", "sweet", "sexy"],
    "color": ["black", "white", "gray", "red", "blue", "green", "yellow", "pink", "brown", "purple", "khaki", "multi-color"],
    "season": ["spring", "summer", "autumn", "winter"],
    "category": ["top wear", "bottom wear", "one-piece dress or jumpsuit"],
    # 🌴 你的神级构想：树状场景池！
    "scene": ["office workplace", "formal banquet or wedding", "home relaxing", "indoor gym", 
              "beach vacation", "park camping", "street shopping", "outdoor sports"]
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
# 4. 数据库重构 (新增场景表头)
# ==========================================
print("🐘 正在连接 PostgreSQL，准备新增场景专属表头...")
conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
conn.autocommit = True
cursor = conn.cursor()

# cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
# cursor.execute("DROP TABLE IF EXISTS clothing_features;")
# ... (建表代码保持注释状态) ...

# ==========================================
# 5. 读取 CSV 并进行【5项全能专项考试】
# ==========================================
try:
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding='gbk')

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

print(f"🔥 开始进行 V6.1 场景赋能打标入库，共 {len(df)} 张图片...")

for index, row in df.iterrows():
    img_name = str(row['Filename']).strip()
    img_path = os.path.join(img_base_dir, img_name)
    
    if not os.path.exists(img_path): continue

    try:
        raw_img = Image.open(img_path).convert('RGB')
        img_clip = clip_preprocess(raw_img).unsqueeze(0).to(device)
        img_dino = dino_transform(raw_img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            raw_f_clip = clip_model.encode_image(img_clip)
            raw_f_dino = dino_model(img_dino)
            f_clip = F.normalize(raw_f_clip, dim=-1).float()
            f_dino = F.normalize(raw_f_dino, dim=-1).float()
            
            final_tags = {}
            
            # 1. 风格 (Top 2)
            sim_style = torch.matmul(f_clip, text_features_dict["style"].T)[0]
            top_styles = [TAG_POOLS["style"][i] for i in sim_style.topk(2).indices]
            final_tags["style"] = ", ".join(top_styles)
            
            # 2. 颜色 (Top 1)
            sim_color = torch.matmul(f_clip, text_features_dict["color"].T)[0]
            final_tags["color"] = TAG_POOLS["color"][sim_color.argmax().item()]
            
            # ==========================================
            # 🚀 3. 季节 (智能排斥逻辑重构) 
            # ==========================================
            sim_season = torch.matmul(f_clip, text_features_dict["season"].T)[0]
            # 获取按照概率从高到低排序的所有季节索引
            sorted_indices = sim_season.argsort(descending=True)
            
            # 绝对信任第一名
            first_season = TAG_POOLS["season"][sorted_indices[0]]
            valid_seasons = [first_season]
            
            # 往后找第二名，遇到互斥直接跳过
            for idx in sorted_indices[1:]:
                next_season = TAG_POOLS["season"][idx]
                
                # 🚫 核心互斥锁：夏不容冬，冬不容夏
                if first_season == "summer" and next_season == "winter":
                    continue
                if first_season == "winter" and next_season == "summer":
                    continue
                
                valid_seasons.append(next_season)
                # 只要凑齐两个合法的季节，立刻停止
                if len(valid_seasons) == 2:
                    break
                    
            final_tags["season"] = ", ".join(valid_seasons)
            # ==========================================
            
            # 4. 品类 (Top 1 强制)
            sim_cat = torch.matmul(f_clip, text_features_dict["category"].T)[0]
            raw_cat = TAG_POOLS["category"][sim_cat.argmax().item()]
            if "top" in raw_cat: standard_cat = "top"
            elif "bottom" in raw_cat: standard_cat = "bottom"
            else: standard_cat = "one_piece"
            final_tags["category"] = standard_cat
            
            # 5. 🌴 场景 (Top 2)
            sim_scene = torch.matmul(f_clip, text_features_dict["scene"].T)[0]
            top_scenes = [TAG_POOLS["scene"][i] for i in sim_scene.topk(2).indices]
            final_tags["scene"] = ", ".join(top_scenes)
            
            super_vector = atf_model(f_clip, f_dino)
            super_vector = F.normalize(super_vector, dim=-1)
            super_vector_list = super_vector.squeeze().cpu().tolist()
        
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
        print(f"❌ 处理 {img_name} 时发生错误: {e}")

cursor.close()
conn.close()
print("\n" + "="*50)
print("🎉 场景赋能全部完成！互斥锁已生效！")
print("="*50)