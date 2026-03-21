#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库查询和相似度搜索工具
支持基于向量的相似服装搜索
"""

import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
from tabulate import tabulate  # type: ignore
import sys
import torch
import clip
from PIL import Image
from torchvision import transforms as T

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'postgres',
    'database': 'dress_recommender',
    'port': 5432
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def connect_db():
    """连接到数据库"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        register_vector(conn)
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def get_table_info():
    """获取表的基本信息"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 查询表统计
        cursor.execute("""
            SELECT 
                entity_kind,
                COUNT(*) as record_count,
                SUM(heap_blks_read) FILTER (WHERE entity_kind = 'table') as size_blocks
            FROM (
                SELECT 'table' as entity_kind, heap_blks_read FROM pg_statio_user_tables
                UNION ALL
                SELECT 'index', heap_blks_read FROM pg_statio_user_indexes
            ) AS t
            GROUP BY entity_kind
        """)
        
        # 直接查询记录数
        cursor.execute("SELECT COUNT(*) FROM clothing_inventory")
        count = cursor.fetchone()[0]
        
        print(f"\n📊 表信息:")
        print(f"  clothing_inventory: {count} 条记录")
        
        # 查询品牌统计
        cursor.execute("""
            SELECT brand, COUNT(*) as count 
            FROM clothing_inventory 
            GROUP BY brand 
            ORDER BY count DESC
        """)
        brands = cursor.fetchall()
        
        print(f"\n🏷️  品牌分布:")
        for brand, cnt in brands[:10]:
            print(f"  {brand}: {cnt} 件")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        cursor.close()
        conn.close()

def similarity_search(filename=None, image_path=None, top_k=5):
    """
    相似度搜索
    
    Args:
        filename: 数据库中已有的文件名（用于从数据库获取向量）
        image_path: 新图片路径（用于临时特征提取）
        top_k: 返回的相似结果数量
    """
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        if filename:
            # 从数据库获取向量
            cursor.execute("""
                SELECT super_vector, filename, brand, price, style_tags
                FROM clothing_inventory
                WHERE filename = %s
            """, (filename,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ 文件不存在: {filename}")
                return
            
            query_vector = result[0]
            query_name = result[1]
            
        elif image_path:
            # 临时特征提取
            print(f"提取图像特征: {image_path}")
            clip_model, clip_preprocess = clip.load("ViT-B/32", device=DEVICE)
            dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14').to(DEVICE)
            dino_model.eval()
            
            img = Image.open(image_path).convert('RGB')
            
            # CLIP特征
            img_clip = clip_preprocess(img).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                clip_feat = clip_model.encode_image(img_clip)[0]
            
            # DINOv2特征
            dino_transform = T.Compose([
                T.Resize((252, 252)),
                T.ToTensor(),
                T.Normalize(mean=(0.485, 0.456, 0.406), 
                           std=(0.229, 0.224, 0.225)),
            ])
            img_dino = dino_transform(img).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                dino_feat = dino_model.forward_features(img_dino)['x_norm_clstoken'][0]
            
            # 简单融合（平均）
            query_vector = torch.cat([clip_feat, dino_feat]).cpu().numpy()
            query_name = image_path
        else:
            print("❌ 需要指定filename或image_path")
            return
        
        # 相似度搜索
        cursor.execute(f"""
            SELECT 
                filename, 
                brand, 
                price, 
                gender,
                style_tags,
                1 - (super_vector <=> %s::vector) as similarity
            FROM clothing_inventory
            WHERE filename != %s
            ORDER BY super_vector <=> %s::vector
            LIMIT %s
        """, (query_vector, query_name if filename else '', query_vector, top_k))
        
        results = cursor.fetchall()
        
        print(f"\n🔍 相似度搜索结果 (查询: {query_name})")
        print("=" * 100)
        
        if results:
            table_data = []
            for row in results:
                filename_r, brand, price, gender, tags, similarity = row
                table_data.append([
                    filename_r,
                    brand,
                    f"¥{price}",
                    gender,
                    ", ".join(tags) if tags else "-",
                    f"{similarity:.4f}"
                ])
            
            headers = ["文件名", "品牌", "价格", "性别", "标签", "相似度"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("未找到相似结果")
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
    finally:
        cursor.close()
        conn.close()

def search_by_brand(brand, limit=10):
    """按品牌搜索"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT filename, brand, price, gender, style_tags
            FROM clothing_inventory
            WHERE brand LIKE %s
            LIMIT %s
        """, (f"%{brand}%", limit))
        
        results = cursor.fetchall()
        
        print(f"\n🏷️  品牌搜索结果: {brand}")
        print("=" * 100)
        
        if results:
            table_data = []
            for row in results:
                filename, brand_result, price, gender, tags = row
                table_data.append([
                    filename,
                    brand_result,
                    f"¥{price}" if price else "-",
                    gender,
                    ", ".join(tags) if tags else "-"
                ])
            
            headers = ["文件名", "品牌", "价格", "性别", "标签"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print(f"未找到品牌: {brand}")
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
    finally:
        cursor.close()
        conn.close()

def search_by_price_range(min_price, max_price, limit=10):
    """按价格范围搜索"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT filename, brand, price, gender, style_tags
            FROM clothing_inventory
            WHERE price BETWEEN %s AND %s
            ORDER BY price ASC
            LIMIT %s
        """, (min_price, max_price, limit))
        
        results = cursor.fetchall()
        
        print(f"\n💰 价格搜索结果: ¥{min_price} - ¥{max_price}")
        print("=" * 100)
        
        if results:
            table_data = []
            for row in results:
                filename, brand, price, gender, tags = row
                table_data.append([
                    filename,
                    brand,
                    f"¥{price}" if price else "-",
                    gender,
                    ", ".join(tags) if tags else "-"
                ])
            
            headers = ["文件名", "品牌", "价格", "性别", "标签"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print(f"价格范围内没有结果")
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 100)
    print("服装数据库查询工具")
    print("=" * 100)
    
    # 显示表信息
    get_table_info()
    
    # 示例搜索
    print("\n" + "=" * 100)
    print("示例查询:")
    print("=" * 100)
    
    # 相似度搜索示例（需要数据库中有数据）
    # similarity_search(filename="img_0001.jpg", top_k=5)
    
    # 品牌搜索示例
    # search_by_brand("MUJI", limit=5)
    
    # 价格范围搜索示例
    # search_by_price_range(400, 600, limit=5)
    
    print("\n💡 使用示例:")
    print("""
    # 相似度搜索
    python query_database.py
    从代码中调用:
    > similarity_search(filename="img_0001.jpg", top_k=5)
    
    # 品牌搜索
    > search_by_brand("MUJI")
    
    # 价格范围搜索
    > search_by_price_range(300, 500)
    """)
