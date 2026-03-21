#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服装图片处理脚本
- 提取CLIP和DINOv2特征
- 融合特征生成超级向量 (HSVS融合)
- 存储到PostgreSQL数据库
"""

import os
import sys
import torch
import numpy as np
import pandas as pd
import clip
from PIL import Image
from torchvision import transforms as T
import psycopg2
from pgvector.psycopg2 import register_vector
import warnings

warnings.filterwarnings('ignore')

# ========== 配置参数 ==========
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DATASET_PATH = "P1_Dataset"
CSV_FILE = os.path.join(DATASET_PATH, "P1_Dataset.csv")
IMAGES_DIR = os.path.join(DATASET_PATH, "images")

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'postgres',
    'database': 'dress_recommender',
    'port': 5432
}

print(f"使用设备: {DEVICE}")

# ========== 模型初始化 ==========
print("\n加载模型...")
clip_model, clip_preprocess = clip.load("ViT-B/32", device=DEVICE)
dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14').to(DEVICE)
dino_model.eval()
print("✓ CLIP和DINOv2模型已加载")

# ========== 图像预处理定义 ==========
# CLIP预处理：缩放到224x224（CLIP标准）
clip_transform = clip_preprocess

# DINOv2预处理：缩放到252x252
dino_transform = T.Compose([
    T.Resize((252, 252), interpolation=T.InterpolationMode.BILINEAR),
    T.ToTensor(),
    T.Normalize(mean=(0.485, 0.456, 0.406), 
                std=(0.229, 0.224, 0.225)),
])

# ========== 特征融合模块 (HSVS) ==========
class HSVSFusion(torch.nn.Module):
    """
    混合语义-视觉综合 (Hybrid Semantic-Visual Synthesis)
    
    融合CLIP的语义特征和DINOv2的结构特征
    基于论文中的ATF (自适应Token特征融合) 逻辑 [cite: 247]
    """
    
    def __init__(self, clip_dim=512, dino_dim=768, output_dim=768):
        super().__init__()
        self.clip_dim = clip_dim
        self.dino_dim = dino_dim
        self.output_dim = output_dim
        
        # CLIP特征投影层：512 -> 768
        self.clip_projection = torch.nn.Linear(clip_dim, output_dim)
        
        # 自适应融合权重 (学习融合比例)
        self.fusion_weight = torch.nn.Linear(output_dim * 2, 2)
        self.softmax = torch.nn.Softmax(dim=-1)
        
        # 特征标准化
        self.norm = torch.nn.LayerNorm(output_dim)
    
    def forward(self, clip_feat, dino_feat):
        """
        融合特征
        
        Args:
            clip_feat: CLIP全局特征 (batch_size, 512)
            dino_feat: DINOv2特征 (batch_size, 768)
        
        Returns:
            fused_feat: 融合后的超级向量 (batch_size, 768)
        """
        # 1. 投影CLIP特征到768维
        clip_projected = self.clip_projection(clip_feat)  # (B, 768)
        
        # 2. 计算自适应融合权重
        combined = torch.cat([clip_projected, dino_feat], dim=-1)  # (B, 1536)
        weights = self.fusion_weight(combined)  # (B, 2)
        weights = self.softmax(weights)  # (B, 2)
        
        # 3. 加权融合
        # weights[:, 0] 用于CLIP特征，weights[:, 1] 用于DINO特征
        fused = (weights[:, 0].unsqueeze(-1) * clip_projected + 
                weights[:, 1].unsqueeze(-1) * dino_feat)  # (B, 768)
        
        # 4. 标准化
        fused = self.norm(fused)
        
        return fused


# 初始化融合模块
hsvs_fusion = HSVSFusion(clip_dim=512, dino_dim=768, output_dim=768)
hsvs_fusion = hsvs_fusion.to(DEVICE)
hsvs_fusion.eval()

print("✓ HSVS融合模块已初始化")

# ========== 特征提取函数 ==========
def extract_features(image_path):
    """
    提取图像的CLIP和DINOv2特征
    
    Args:
        image_path: 图像路径
        
    Returns:
        clip_feat: CLIP特征 (512,)
        dino_feat: DINOv2特征 (768,)
    """
    try:
        # 加载图片
        img = Image.open(image_path).convert('RGB')
        
        # CLIP特征提取
        img_clip = clip_transform(img).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            clip_feat = clip_model.encode_image(img_clip)[0]  # (512,)
        
        # DINOv2特征提取
        img_dino = dino_transform(img).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            dino_output = dino_model.forward_features(img_dino)
            # DINOv2返回全局token特征 (patch_count+1, 768)，我们取CLS token
            dino_feat = dino_output['x_norm_clstoken'][0]  # (768,)
        
        return clip_feat, dino_feat
        
    except Exception as e:
        print(f"❌ 特征提取失败 ({image_path}): {e}")
        return None, None

def fuse_features(clip_feat, dino_feat):
    """
    融合CLIP和DINOv2特征，生成超级向量
    
    Args:
        clip_feat: CLIP特征 (512,)
        dino_feat: DINOv2特征 (768,)
        
    Returns:
        super_vec: 融合后的超级向量 (768,)
    """
    with torch.no_grad():
        # 添加batch维度
        clip_feat = clip_feat.unsqueeze(0)  # (1, 512)
        dino_feat = dino_feat.unsqueeze(0)  # (1, 768)
        
        # 融合
        super_vec = hsvs_fusion(clip_feat, dino_feat)[0]  # (768,)
        
    return super_vec

def detect_style_tags(image_path, num_tags=5):
    """
    使用CLIP检测图像的风格标签
    
    Args:
        image_path: 图像路径
        num_tags: 返回的标签数量
        
    Returns:
        tags: 标签列表
        confidences: 置信度列表
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img_input = clip_transform(img).unsqueeze(0).to(DEVICE)
        
        # 预定义的服装相关标签
        clothing_tags = [
            "casual", "formal", "sporty", "elegant", "trendy",
            "vintage", "minimalist", "colorful", "neutral", "patterned",
            "short sleeves", "long sleeves", "sleeveless", "fitted", "loose",
            "summer", "winter", "spring", "autumn", "all-season"
        ]
        
        with torch.no_grad():
            img_features = clip_model.encode_image(img_input)
            text_features = clip_model.encode_text(clip.tokenize(clothing_tags).to(DEVICE))
            
            # 计算相似度
            img_features = img_features / img_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            similarities = (img_features @ text_features.T)[0]  # (len(tags),)
            
            # 排序并选择top-k
            top_k_indices = torch.argsort(similarities, descending=True)[:num_tags]
            top_tags = [clothing_tags[i] for i in top_k_indices]
            top_confidences = [similarities[i].item() for i in top_k_indices]
        
        return top_tags, top_confidences
        
    except Exception as e:
        print(f"⚠ 标签检测失败 ({image_path}): {e}")
        return [], []

# ========== 数据库操作 ==========
def insert_clothing_record(cursor, row, clip_vec, dino_vec, super_vec, style_tags):
    """
    插入服装记录到数据库
    """
    sql = """
    INSERT INTO clothing_inventory 
    (filename, brand, price, gender, has_model, clip_vector, dino_vector, super_vector, style_tags)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (filename) DO UPDATE SET
        clip_vector = EXCLUDED.clip_vector,
        dino_vector = EXCLUDED.dino_vector,
        super_vector = EXCLUDED.super_vector,
        style_tags = EXCLUDED.style_tags,
        updated_at = CURRENT_TIMESTAMP
    """
    
    params = (
        row['Filename'],
        row['Brand'],
        float(row['Price']) if pd.notna(row['Price']) else None,
        row['Gender'],
        bool(row['Has_Model']),
        clip_vec.cpu().numpy(),
        dino_vec.cpu().numpy(),
        super_vec.cpu().numpy(),
        style_tags
    )
    
    cursor.execute(sql, params)

def process_dataset():
    """
    处理整个数据集并存储到数据库
    """
    # 读取CSV
    df = pd.read_csv(CSV_FILE)
    print(f"\n读取CSV: {CSV_FILE}")
    print(f"✓ 待处理图片数: {len(df)}")
    
    # 连接数据库
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        register_vector(conn)  # 为pgvector注册类型
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    # 处理每一行
    successful = 0
    failed = 0
    
    print("\n开始处理图片...")
    print("=" * 80)
    
    for index, row in df.iterrows():
        try:
            filename = row['Filename']
            image_path = os.path.join(IMAGES_DIR, filename)
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"[{index+1}/{len(df)}] ⚠ 文件不存在: {filename}")
                failed += 1
                continue
            
            # 提取特征
            clip_feat, dino_feat = extract_features(image_path)
            if clip_feat is None or dino_feat is None:
                failed += 1
                continue
            
            # 融合特征
            super_vec = fuse_features(clip_feat, dino_feat)
            
            # 检测风格标签
            style_tags, confidences = detect_style_tags(image_path, num_tags=5)
            
            # 存储到数据库
            insert_clothing_record(cursor, row, clip_feat, dino_feat, super_vec, style_tags)
            
            print(f"[{index+1}/{len(df)}] ✓ {filename}")
            print(f"       品牌: {row['Brand']}, 价格: {row['Price']}, 性别: {row['Gender']}")
            print(f"       标签: {', '.join(style_tags)}")
            print(f"       超级向量: {super_vec.shape}")
            
            successful += 1
            
        except Exception as e:
            print(f"[{index+1}/{len(df)}] ❌ 处理失败: {e}")
            failed += 1
            continue
    
    # 提交事务
    try:
        conn.commit()
        cursor.close()
        conn.close()
        print("=" * 80)
        print(f"\n✓ 处理完成!")
        print(f"  成功: {successful}")
        print(f"  失败: {failed}")
        return True
    except Exception as e:
        print(f"❌ 数据库提交失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("服装图片处理和特征融合")
    print("=" * 80)
    
    success = process_dataset()
    
    if success:
        print("\n✓ 所有数据已成功导入数据库")
        print("  你现在可以使用以下查询:")
        print("    SELECT * FROM clothing_inventory;")
        print("    SELECT * FROM clothing_inventory WHERE brand = '...';")
    else:
        print("\n❌ 数据导入过程中出现错误")
        sys.exit(1)
