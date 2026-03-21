import torch
import torch.nn.functional as F
import psycopg2
import clip

# 中英文标签知识图谱 (用于解析用户意图)
# 中英文高阶知识图谱
INTENT_MAP = {
    # 风格
    "运动": "sporty", "正式": "formal", "休闲": "casual", "复古": "vintage", "街头": "streetwear",
    "约会": "romantic dating", "通勤": "business casual", "极简": "minimalist", "户外": "outdoor", "甜美": "sweet", "性感": "sexy",
    # 材质
    "棉": "cotton", "牛仔": "denim", "皮": "leather", "针织": "knit", "丝绸": "silk", "雪纺": "chiffon",
    # 上装
    "t恤": "T-shirt", "短袖": "T-shirt", "衬衫": "shirt", "毛衣": "sweater", "卫衣": "hoodie", "外套": "jacket", "大衣": "coat",
    "吊带": "tank top", "女衫": "blouse", "开衫": "cardigan", "西装": "suit blazer",
    # 下装
    "牛仔裤": "jeans", "长裤": "casual trousers", "工装裤": "cargo pants", "短裤": "shorts", "热裤": "hot pants",
    "百褶裙": "pleated skirt", "a字裙": "A-line skirt", "包臀半身裙": "pencil skirt", "半身裙": "midi skirt", "短裙": "mini skirt",
    # 连体装
    "连衣": "dress", "包臀裙": "bodycon dress", "紧身裙": "bodycon dress", "吊带裙": "slip dress", "碎花裙": "floral dress", "长裙": "maxi dress", "连体裤": "jumpsuit",
    # 季节
    "春": "spring", "夏": "summer", "秋": "autumn", "冬": "winter",
}

# 🛑 强制冲突黑名单 (知识图谱)
CONFLICT_RULES = {
    "summer": ["winter", "coat", "sweater", "hoodie"],
    "winter": ["summer", "shorts"],
    "sporty": ["formal", "leather", "romantic dating"],
    "formal": ["sporty", "hoodie", "shorts"]
}

def get_db_connection():
    return psycopg2.connect(
        host="localhost", database="postgres", 
        user="postgres", password="123456", port="5432"
    )

def parse_user_intent(user_query):
    """提取用户的文字硬性要求，转化为英文标签组"""
    required_tags = set()
    for ch_word, en_tag in INTENT_MAP.items():
        if ch_word in user_query:
            required_tags.add(en_tag)
            
    forbidden_tags = set()
    for req_tag in required_tags:
        if req_tag in CONFLICT_RULES:
            forbidden_tags.update(CONFLICT_RULES[req_tag])
            
    return required_tags, forbidden_tags

def check_hard_filters(item_tags, required_tags, forbidden_tags):
    """
    第一轮硬筛机制：
    1. 遇到禁忌标签（如夏天要冬装），直接判死刑 (-999分)
    2. 命中核心需求（如明确要短裤），给予巨额加分 (+1.5分)
    """
    item_t = set([t.strip().lower() for t in item_tags.split(',')])
    
    if item_t.intersection(forbidden_tags):
        return -999.0 
        
    # 命中加分
    bonus = 0.0
    matches = item_t.intersection(required_tags)
    if matches:
        bonus += len(matches) * 0.8  
        
    return bonus

def load_clothing_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, brand, price, clip_tags, super_vector::text FROM clothing_features;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    items = []
    for row in rows:
        filename, brand, price, tags, vec_str = row
        vec_list = eval(vec_str)
        tensor_vec = torch.tensor(vec_list, dtype=torch.float32)
        
        tags_lower = tags.lower()
        
        # 👗 绝对品类隔离逻辑：包臀裙/连衣裙等属于连体装，严禁和上下装混淆
        category = "unknown"
        if 'dress' in tags_lower:
            category = "one_piece"
        elif any(t in tags_lower for t in ['jeans', 'trousers', 'shorts', 'skirt']):
            category = "bottom"
        elif any(t in tags_lower for t in ['t-shirt', 'shirt', 'sweater', 'hoodie', 'jacket', 'coat']):
            category = "top"
        else:
            category = "top" # 兜底
            
        items.append({
            "filename": filename,
            "brand": brand,
            "price": price,
            "tags": tags,
            "category": category,
            "vector": tensor_vec
        })
    return items

def advanced_recommend(user_query, items, top_k=3):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 1. 意图捕获与硬筛提取
    required_tags, forbidden_tags = parse_user_intent(user_query)
    print(f"\n用户需求: [{user_query}]")
    print(f"引擎已锁定硬筛意图: 必须优先 {list(required_tags)}")
    if forbidden_tags:
        print(f"引擎已启用强制封杀: 严禁出现 {list(forbidden_tags)}")

    # 2. 生成用户搜索向量
    clip_model, _ = clip.load("ViT-L/14", device=device)
    clip_model.eval()
    with torch.no_grad():
        text_tokens = clip.tokenize([user_query]).to(device)
        query_vector = clip_model.encode_text(text_tokens).float()
        query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

    tops = [i for i in items if i["category"] == "top"]
    bottoms = [i for i in items if i["category"] == "bottom"]
    one_pieces = [i for i in items if i["category"] == "one_piece"]
    
    final_candidates = []

    if tops and bottoms:
        top_vectors = torch.stack([t["vector"] for t in tops])
        bottom_vectors = torch.stack([b["vector"] for b in bottoms])
        
        # 语义对齐
        top_query_sim = torch.matmul(top_vectors, query_vector)
        bottom_query_sim = torch.matmul(bottom_vectors, query_vector)
        
        # 审美流形碰撞 (高斯互补)
        raw_harmony = torch.matmul(top_vectors, bottom_vectors.T)
        gaussian_harmony = torch.exp(-((raw_harmony - 0.6) ** 2) / (2 * 0.2 ** 2))
        
        # 基础分
        base_score_matrix = (0.4 * top_query_sim.unsqueeze(1)) + \
                            (0.4 * bottom_query_sim.unsqueeze(0)) + \
                            (0.2 * gaussian_harmony)
                            
        # 取前 50 名进入硬筛池
        flat_scores = base_score_matrix.flatten()
        top_50_indices = torch.topk(flat_scores, min(50, len(flat_scores))).indices
        
        for flat_idx in top_50_indices:
            top_idx = flat_idx // len(bottoms)
            bottom_idx = flat_idx % len(bottoms)
            t_item = tops[top_idx]
            b_item = bottoms[bottom_idx]
            
            # 第一轮硬筛
            t_bonus = check_hard_filters(t_item['tags'], required_tags, forbidden_tags)
            b_bonus = check_hard_filters(b_item['tags'], required_tags, forbidden_tags)
            
            # 视觉冲突惩罚 (如格子配碎花)
            penalty = 1.0
            t_set = set([t.strip() for t in t_item['tags'].split(',')])
            b_set = set([t.strip() for t in b_item['tags'].split(',')])
            patterns = {'striped', 'plaid', 'floral'}
            t_pat = t_set.intersection(patterns)
            b_pat = b_set.intersection(patterns)
            if t_pat and b_pat and t_pat != b_pat:
                penalty = 0.5 
                
            final_score = (base_score_matrix[top_idx, bottom_idx].item() + t_bonus + b_bonus) * penalty
            
            if final_score > 0: 
                final_candidates.append({
                    "type": "combo",
                    "top": t_item,
                    "bottom": b_item,
                    "score": final_score
                })

    if one_pieces:
        op_vectors = torch.stack([op["vector"] for op in one_pieces])
        op_query_sim = torch.matmul(op_vectors, query_vector)
        
        # 因为它只有一件，为了和“两件套”的分数处于同一量级，将其特征重要性放大
        for idx, op_item in enumerate(one_pieces):
            base_score = op_query_sim[idx].item() * 0.8 + 0.2 # 补偿缺失的 harmony 分数
            
            # 硬筛洗礼
            bonus = check_hard_filters(op_item['tags'], required_tags, forbidden_tags)
            final_score = base_score + (bonus * 2.0) # 连体服一次性吃满两件衣服的权重
            
            if final_score > 0:
                final_candidates.append({
                    "type": "one_piece",
                    "item": op_item,
                    "score": final_score
                })

    final_candidates.sort(key=lambda x: x["score"], reverse=True)
    best_matches = final_candidates[:top_k]
    
    print("\n" + "★"*65)
    print(f"👗 机器美学最高分榜单 (带硬过滤) - Top {top_k}")
    print("★"*65)
    
    for rank, match in enumerate(best_matches):
        print(f"👑 【最佳方案 {rank + 1}】 | 综合评分: {match['score']:.4f}")
        
        if match["type"] == "combo":
            t = match["top"]
            b = match["bottom"]
            print(f"   👕 互补上装: {t['filename']} (¥{t['price']}) - 标签: {t['tags']}")
            print(f"   👖 互补下装: {b['filename']} (¥{b['price']}) - 标签: {b['tags']}")
            print(f"   💰 组合总价: ¥{t['price'] + b['price']}")
            
        elif match["type"] == "one_piece":
            op = match["item"]
            print(f"   👗 绝美连体服/裙: {op['filename']} (¥{op['price']})")
            print(f"      ├─ 品牌: {op['brand']}")
            print(f"      └─ 标签: {op['tags']}")
            print(f"   💰 一件搞定，总价: ¥{op['price']}")
            
        print("-" * 65)

if __name__ == "__main__":
    db_items = load_clothing_data()
    
    # 你可以修改这里的词语来测试！
    # 测试例1: "适合夏天出去玩穿的运动服，要短裤"
    # 测试例2: "参加前男友婚礼穿的包臀裙"
    test_query = "适合夏天出去玩穿的运动服，要短裤"
    
    advanced_recommend(test_query, db_items, top_k=3)