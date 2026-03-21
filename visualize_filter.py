# import os
# import psycopg2
# import matplotlib.pyplot as plt
# import numpy as np  # 👈 加上了这个至关重要的灵魂引包！
# from PIL import Image

# # ==========================================
# # 🔍 纯净版：硬筛选可视化探查仪
# # ==========================================

# # 解决 Matplotlib 画图时中文显示变成方块的问题
# plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
# plt.rcParams['axes.unicode_minus'] = False 

# # 🧠 中英文标签知识图谱
# # 🧠 V2.0 中英文高阶知识图谱
# INTENT_MAP = {
#     # 风格
#     "运动": "sporty", "正式": "formal", "休闲": "casual", "复古": "vintage", "街头": "streetwear",
#     "约会": "romantic dating", "通勤": "business casual", "极简": "minimalist", "户外": "outdoor", "甜美": "sweet", "性感": "sexy",
#     # 材质
#     "棉": "cotton", "牛仔": "denim", "皮": "leather", "针织": "knit", "丝绸": "silk", "雪纺": "chiffon",
#     # 上装
#     "t恤": "T-shirt", "短袖": "T-shirt", "衬衫": "shirt", "毛衣": "sweater", "卫衣": "hoodie", "外套": "jacket", "大衣": "coat",
#     "吊带": "tank top", "女衫": "blouse", "开衫": "cardigan", "西装": "suit blazer",
#     # 下装
#     "牛仔裤": "jeans", "长裤": "casual trousers", "工装裤": "cargo pants", "短裤": "shorts", "热裤": "hot pants",
#     "百褶裙": "pleated skirt", "a字裙": "A-line skirt", "包臀半身裙": "pencil skirt", "半身裙": "midi skirt", "短裙": "mini skirt",
#     # 连体装
#     "连衣": "dress", "包臀裙": "bodycon dress", "紧身裙": "bodycon dress", "吊带裙": "slip dress", "碎花裙": "floral dress", "长裙": "maxi dress", "连体裤": "jumpsuit",
#     # 季节
#     "春": "spring", "夏": "summer", "秋": "autumn", "冬": "winter",
# }

# def get_db_connection():
#     return psycopg2.connect(
#         host="localhost", database="postgres", 
#         user="postgres", password="123456", port="5432"
#     )

# def parse_user_intent(user_query):
#     """把大白话翻译成英文硬标签"""
#     required_tags = set()
#     for ch_word, en_tag in INTENT_MAP.items():
#         if ch_word in user_query:
#             required_tags.add(en_tag)
#     return required_tags

# def visualize_hard_filter(user_query, img_base_dir, top_k=10):
#     print(f"\n✨ 收到查询需求: [{user_query}]")
    
#     required_tags = parse_user_intent(user_query)
#     if not required_tags:
#         print("💥 哎呀，没有从你的话里提取到任何预设标签！试着带上季节、风格或品类词吧。")
#         return
        
#     print(f"🎯 提取到的硬性检索标签: {list(required_tags)}")
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT filename, brand, price, clip_tags FROM clothing_features;")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     candidates = []
    
#     for row in rows:
#         filename, brand, price, tags = row
#         item_tags_set = set([t.strip().lower() for t in tags.split(',')])
        
#         # 算一下这件衣服命中了几个你的需求
#         matched_tags = item_tags_set.intersection(required_tags)
#         match_count = len(matched_tags)
        
#         if match_count > 0:
#             candidates.append({
#                 "filename": filename,
#                 "brand": brand,
#                 "price": price,
#                 "tags": tags,
#                 "match_count": match_count,
#             })
            
#     # 按照命中标签的数量从高到低排序
#     candidates.sort(key=lambda x: x["match_count"], reverse=True)
#     results = candidates[:top_k]
    
#     if not results:
#         print("😭 惨了，数据库里没有任何一件衣服能匹配上你的这些标签...")
#         return
        
#     print(f"\n🎉 检索完毕！为你展示命中数量最高的 {len(results)} 件衣服！")

#     # ==========================================
#     # 🎨 启动可视化前端画板
#     # ==========================================
#     cols = 5
#     rows_num = (len(results) + cols - 1) // cols
#     fig, axes = plt.subplots(rows_num, cols, figsize=(18, 4 * rows_num))
    
#     if rows_num == 1:
#         axes = np.array(axes).reshape(1, -1) if len(results) == 1 else axes
#     axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]

#     for i, item in enumerate(results):
#         ax = axes[i]
#         img_path = os.path.join(img_base_dir, item['filename'])
        
#         try:
#             img = Image.open(img_path).convert('RGB')
#             ax.imshow(img)
#         except Exception as e:
#             ax.text(0.5, 0.5, '图片加载失败', ha='center', va='center')
            
#         ax.axis('off') 
        
#         # 图片上方：文件名 + 命中数 + 价格
#         title_text = f"{item['filename']}\n命中 {item['match_count']} 个需求\n¥{item['price']}"
#         ax.set_title(title_text, fontsize=10, fontweight='bold')
        
#         # 图片下方：自带的AI标签
#         ax.text(0.5, -0.1, f"自带标签:\n{item['tags']}", 
#                 transform=ax.transAxes, ha='center', va='top', 
#                 fontsize=8, color='blue', wrap=True)

#     for j in range(len(results), len(axes)):
#         axes[j].axis('off')

#     plt.tight_layout()
#     plt.show()

# if __name__ == "__main__":
#     # ⚠️ 请确保这里的文件夹路径包含了你测试的图片！
#     img_dir = r"D:\dress_recommender\images\images"
    
#     # 测试你的极限拷问词
#     test_query = "适合夏天出去玩穿的运动服"
#     # test_query = "参加前男友婚礼穿的包臀裙"
    
#     visualize_hard_filter(test_query, img_dir, top_k=10)
import os
import psycopg2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from collections import defaultdict

# ==========================================
# 🔍 V2.0 硬筛选可视化探查仪 (搭载品类打散算法)
# ==========================================

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
plt.rcParams['axes.unicode_minus'] = False 

# 🧠 V2.0 中英文高阶知识图谱
INTENT_MAP = {
    "运动": "sporty", "正式": "formal", "休闲": "casual", "复古": "vintage", "街头": "streetwear",
    "约会": "romantic dating", "通勤": "business casual", "极简": "minimalist", "户外": "outdoor", "甜美": "sweet", "性感": "sexy",
    "棉": "cotton", "牛仔": "denim", "皮": "leather", "针织": "knit", "丝绸": "silk", "雪纺": "chiffon",
    "t恤": "T-shirt", "短袖": "T-shirt", "衬衫": "shirt", "毛衣": "sweater", "卫衣": "hoodie", "外套": "jacket", "大衣": "coat",
    "吊带": "tank top", "女衫": "blouse", "开衫": "cardigan", "西装": "suit blazer",
    "牛仔裤": "jeans", "裤": "casual trousers", "工装裤": "cargo pants", "短裤": "shorts", "热裤": "hot pants",
    "百褶裙": "pleated skirt", "a字裙": "A-line skirt", "包臀半身裙": "pencil skirt", "半身裙": "midi skirt", "短裙": "mini skirt",
    "连衣": "dress", "包臀裙": "bodycon dress", "紧身裙": "bodycon dress", "吊带裙": "slip dress", "碎花裙": "floral dress", "长裙": "maxi dress", "连体裤": "jumpsuit",
    "春": "spring", "夏": "summer", "秋": "autumn", "冬": "winter",
}

# 👗 绝对品类隔离字典 (用于打散端水)
TOP_TAGS = {"t-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", "tank top", "blouse", "cardigan", "suit blazer"}
BOTTOM_TAGS = {"jeans", "casual trousers", "cargo pants", "shorts", "hot pants", "pleated skirt", "a-line skirt", "pencil skirt", "midi skirt", "mini skirt"}
ONE_PIECE_TAGS = {"dress", "bodycon dress", "slip dress", "floral dress", "maxi dress", "jumpsuit"}

def get_db_connection():
    return psycopg2.connect(
        host="localhost", database="postgres", 
        user="postgres", password="123456", port="5432"
    )

def parse_user_intent(user_query):
    required_tags = set()
    for ch_word, en_tag in INTENT_MAP.items():
        if ch_word in user_query:
            required_tags.add(en_tag)
    return required_tags

def categorize_item(tags_str):
    """给每件衣服进行品类定性，方便后续发牌"""
    tags_lower = tags_str.lower()
    if any(t in tags_lower for t in ONE_PIECE_TAGS): return "one_piece"
    if any(t in tags_lower for t in BOTTOM_TAGS): return "bottom"
    if any(t in tags_lower for t in TOP_TAGS): return "top"
    return "unknown"

def visualize_hard_filter(user_query, img_base_dir, top_k=10):
    print(f"\n✨ 收到查询需求: [{user_query}]")
    
    required_tags = parse_user_intent(user_query)
    if not required_tags:
        print("💥 哎呀，没有从你的话里提取到任何预设标签！")
        return
        
    print(f"🎯 提取到的硬性检索标签: {list(required_tags)}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, brand, price, clip_tags FROM clothing_features;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    candidates = []
    for row in rows:
        filename, brand, price, tags = row
        item_tags_set = set([t.strip().lower() for t in tags.split(',')])
        
        matched_tags = item_tags_set.intersection(required_tags)
        match_count = len(matched_tags)
        
        if match_count > 0:
            candidates.append({
                "filename": filename,
                "brand": brand,
                "price": price,
                "tags": tags,
                "match_count": match_count,
                "category": categorize_item(tags) # 记录它的品类
            })
            
    if not candidates:
        print("😭 惨了，数据库里没有任何衣服能匹配上...")
        return
        
    # ==========================================
    # ⚖️ 核心黑科技：分数分层 + 品类轮询打散算法
    # ==========================================
    # 1. 先把所有衣服按分数分桶 (比如 3分的放一桶，2分的放一桶)
    score_buckets = defaultdict(list)
    for c in candidates:
        score_buckets[c['match_count']].append(c)
        
    results = []
    
    # 2. 从最高分的桶开始，执行“轮流发牌”
    for score in sorted(score_buckets.keys(), reverse=True):
        bucket = score_buckets[score]
        
        # 将同分的衣服再按品类分成三堆
        tops = [c for c in bucket if c['category'] == 'top']
        bottoms = [c for c in bucket if c['category'] == 'bottom']
        ops = [c for c in bucket if c['category'] == 'one_piece']
        
        # 只要这层分数桶里还有衣服，并且没拿满 top_k，就轮流各拿一件！
        while (tops or bottoms or ops) and len(results) < top_k:
            if tops and len(results) < top_k: results.append(tops.pop(0))
            if bottoms and len(results) < top_k: results.append(bottoms.pop(0))
            if ops and len(results) < top_k: results.append(ops.pop(0))
            
        if len(results) >= top_k:
            break

    print(f"\n🎉 检索并打散完毕！完美端水，为你展示最均匀的 {len(results)} 件衣服！")

    # ==========================================
    # 🎨 启动可视化前端画板
    # ==========================================
    cols = 5
    rows_num = (len(results) + cols - 1) // cols
    fig, axes = plt.subplots(rows_num, cols, figsize=(18, 4 * rows_num))
    
    if rows_num == 1:
        axes = np.array(axes).reshape(1, -1) if len(results) == 1 else axes
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    for i, item in enumerate(results):
        ax = axes[i]
        img_path = os.path.join(img_base_dir, item['filename'])
        
        try:
            img = Image.open(img_path).convert('RGB')
            ax.imshow(img)
        except Exception as e:
            ax.text(0.5, 0.5, '图片加载失败', ha='center', va='center')
            
        ax.axis('off') 
        
        title_text = f"[{item['category'].upper()}]\n{item['filename']}\n命中 {item['match_count']} 个需求"
        ax.set_title(title_text, fontsize=10, fontweight='bold', color='darkred')
        
        ax.text(0.5, -0.1, f"自带标签:\n{item['tags']}", 
                transform=ax.transAxes, ha='center', va='top', 
                fontsize=8, color='blue', wrap=True)

    for j in range(len(results), len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # ⚠️ 请确保你的图片路径正确
    img_dir = r"D:\dress_recommender\images\images" 
    
    # 见证奇迹的时刻：这次搜“夏天运动服”，看看是不是一半衣服一半裤子！
    test_query = "夏天海岛碎花裙"
    
    visualize_hard_filter(test_query, img_dir, top_k=10)