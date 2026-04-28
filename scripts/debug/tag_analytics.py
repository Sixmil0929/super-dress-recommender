import psycopg2
import pandas as pd
from collections import Counter

# ==========================================
# 终极数据分析：480张图库的家底盘点仪
# ==========================================
def analyze_tags():
    print("🚀 正在启动全库标签扫描引擎...")

    # 1. 连接你的大象数据库 (密码配置和之前一样)
    try:
        conn = psycopg2.connect(
            host="localhost", 
            database="postgres", 
            user="postgres", 
            password="123456", 
            port="5432"
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"💥 数据库连接失败，请检查 Docker 是否开启: {e}")
        return

    # 2. 从数据库一口气把 480 条数据的 clip_tags 揪出来
    print("🐘 正在从 PostgreSQL 提取全量标签数据...")
    cursor.execute("SELECT clip_tags FROM clothing_features;")
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    total_images = len(rows)
    print(f"✅ 成功读取！当前总图库容量: {total_images} 件服装。\n")
    
    if total_images == 0:
        print("⚠️ 数据库是空的，快去检查一下！")
        return

    # 3. 剥茧抽丝：把字符串切开，扔进计数器
    all_tags = []
    for row in rows:
        # row[0] 长这样: "casual, cotton, T-shirt, summer..."
        tags_string = row[0]
        if tags_string:
            # 用逗号和空格切开，变成列表
            individual_tags = [t.strip() for t in tags_string.split(',')]
            all_tags.extend(individual_tags)
            
    # 4. 祭出计数大杀器
    tag_counts = Counter(all_tags)
    
    # 你设定的那套原始完美标签池（用来查漏补缺）
    tag_pool = [
        "sporty", "formal", "casual", "vintage", "streetwear", 
        "romantic dating", "business casual", "minimalist", "outdoor", "sweet",
        "cotton", "denim", "leather",
        "T-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", 
        "jeans", "trousers", "shorts", "dress", "skirt",
        "spring", "summer", "autumn", "winter",
        "striped", "plaid", "floral",
        "black", "white", "gray", "red", "blue", 
        "green", "yellow", "pink", "brown", "purple"
    ]
    
    # 5. 打印华丽的成绩单
    print("="*50)
    print("🏆 【全库标签火力分布排行榜】")
    print("="*50)
    
    for tag, count in tag_counts.most_common():
        percentage = (count / total_images) * 100
        # 排版对齐：标签名占 15 个字符位置
        print(f" 🏷️ {tag: <15} | 库存: {count: >3} 件 | 渗透率: {percentage:>5.1f}%")
        
    print("\n" + "="*50)
    print("🚨 【零库存 / 盲区警报】")
    print("="*50)
    
    # 找出在原始池子里，但在数据库里一次都没出现过的标签
    empty_tags = [tag for tag in tag_pool if tag not in tag_counts]
    
    if empty_tags:
        print("⚠️ 警告！以下标签在 480 张图里【完全没有命中】，如果用户搜了会直接扑空：")
        for tag in empty_tags:
            print(f"  ❌ {tag}")
        print("\n👉 建议：如果在意这些分类，可以让团队去网上再针对性地扒几张对应风格的图追加进去！")
    else:
        print("🎉 太无敌了！你设定的所有标签分类，在图库里都有衣服对应！没有任何盲区！")

if __name__ == "__main__":
    analyze_tags()