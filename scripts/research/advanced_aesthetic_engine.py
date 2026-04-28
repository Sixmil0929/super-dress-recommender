import torch
import torch.nn.functional as F
import psycopg2
import clip
import math

def get_db_connection():
    return psycopg2.connect(
        host="localhost", database="postgres", 
        user="postgres", password="123456", port="5432"
    )

def load_clothing_data():
    """从数据库抽取全量服装档案"""
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
        
        category = "unknown"
        tags_lower = tags.lower()
        if any(t in tags_lower for t in ['t-shirt', 'shirt', 'sweater', 'hoodie', 'jacket', 'coat']):
            category = "top"
        elif any(t in tags_lower for t in ['jeans', 'trousers', 'shorts', 'skirt']):
            category = "bottom"
            
        items.append({
            "filename": filename,
            "brand": brand,
            "price": price,
            "tags": tags,
            "category": category,
            "vector": tensor_vec
        })
    return items

def check_aesthetic_clash(top_tags, bottom_tags):
    """
    符号逻辑层：美学冲突检测 (Rule-based Penalty)
    返回惩罚系数：1.0 表示完美，0.2 表示灾难搭配
    """
    top_t = set([t.strip() for t in top_tags.split(',')])
    bottom_t = set([t.strip() for t in bottom_tags.split(',')])
    
    # 冲突规则 1：图案大打出手 (格子配碎花，条纹配格子)
    patterns = {'striped', 'plaid', 'floral'}
    top_patterns = top_t.intersection(patterns)
    bottom_patterns = bottom_t.intersection(patterns)
    if top_patterns and bottom_patterns and top_patterns != bottom_patterns:
        return 0.2  # 灾难级惩罚
        
    # 冲突规则 2：季节极度错乱
    if ('winter' in top_t and 'summer' in bottom_t) or ('summer' in top_t and 'winter' in bottom_t):
        # 除非是时尚达人喜欢羽绒服配短裤，否则普通推荐予以适当降权
        return 0.5 
        
    return 1.0 # 安全通过

def advanced_recommend(user_query, items, top_k=3):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n✨ 正在为您生成搭配，需求: [{user_query}]")
    
    clip_model, _ = clip.load("ViT-L/14", device=device)
    clip_model.eval()
    
    with torch.no_grad():
        text_tokens = clip.tokenize([user_query]).to(device)
        query_vector = clip_model.encode_text(text_tokens).float()
        query_vector = F.normalize(query_vector, dim=-1).squeeze(0).cpu()

    tops = [item for item in items if item["category"] == "top"]
    bottoms = [item for item in items if item["category"] == "bottom"]
    
    if not tops or not bottoms:
        print("💥 图库中上下装数据不全，无法进行美学碰撞！")
        return

    top_vectors = torch.stack([t["vector"] for t in tops])
    bottom_vectors = torch.stack([b["vector"] for b in bottoms])
    
    # --- 阶段一：语义牵引 ---
    top_query_sim = torch.matmul(top_vectors, query_vector)
    bottom_query_sim = torch.matmul(bottom_vectors, query_vector)
    
    # --- 阶段二：计算原始互补余弦距离 ---
    raw_harmony_matrix = torch.matmul(top_vectors, bottom_vectors.T)
    
    # 🌌 核心：高斯流形美学转换 (Gaussian Aesthetic Transformation)
    # 假设最佳视觉对比度发生在相似度 0.6 左右，容差 0.2
    mu = 0.60  
    sigma = 0.20
    # 套用高斯能量公式，让中等相似度的搭配获得最高和谐分！
    gaussian_harmony = torch.exp(-((raw_harmony_matrix - mu) ** 2) / (2 * sigma ** 2))
    
    # --- 阶段三：张量融合加权 ---
    w_query = 0.35
    w_harmony = 0.30
    
    # 初步总分矩阵
    base_score_matrix = (w_query * top_query_sim.unsqueeze(1)) + \
                        (w_query * bottom_query_sim.unsqueeze(0)) + \
                        (w_harmony * gaussian_harmony)
                        
    # 取出前 50 个高潜组合，进入符号逻辑层做最终洗礼
    flat_scores = base_score_matrix.flatten()
    top_50_indices = torch.topk(flat_scores, min(50, len(flat_scores))).indices
    
    final_candidates = []
    
    for flat_idx in top_50_indices:
        top_idx = flat_idx // len(bottoms)
        bottom_idx = flat_idx % len(bottoms)
        
        best_top = tops[top_idx]
        best_bottom = bottoms[bottom_idx]
        base_score = base_score_matrix[top_idx, bottom_idx].item()
        
        # ⚔️ 阶段四：引入符号学规则惩罚 (知识图谱洗礼)
        penalty_factor = check_aesthetic_clash(best_top['tags'], best_bottom['tags'])
        final_score = base_score * penalty_factor
        
        final_candidates.append({
            "top": best_top,
            "bottom": best_bottom,
            "score": final_score
        })
        
    # 根据惩罚后的最终得分重新排序，取出真正的 Top K
    final_candidates.sort(key=lambda x: x["score"], reverse=True)
    best_matches = final_candidates[:top_k]
    
    print("\n" + "★"*60)
    print(f"👗 机器美学最高分搭配榜单 (Top {top_k})")
    print("★"*60)
    
    for rank, match in enumerate(best_matches):
        best_top = match["top"]
        best_bottom = match["bottom"]
        total_price = best_top['price'] + best_bottom['price']
        
        print(f"👑 【搭配方案 {rank + 1}】 | 综合美学评分: {match['score']:.4f} | 组合总价: ¥{total_price}")
        print(f"   👕 互补上装: {best_top['filename']} (品牌: {best_top['brand']}, ¥{best_top['price']})")
        print(f"      ├─ 特征基因: {best_top['tags']}")
        print(f"   👖 互补下装: {best_bottom['filename']} (品牌: {best_bottom['brand']}, ¥{best_bottom['price']})")
        print(f"      └─ 特征基因: {best_bottom['tags']}")
        print("-" * 60)

if __name__ == "__main__":
    print("🗄️ 正在连线数据库，抽取 480 件服装特征档案...")
    db_items = load_clothing_data()
    print(f"✅ 成功唤醒 {len(db_items)} 件服装数据！")
    
    # 💡 在这里输入你的搭配需求！
    test_query = "适合夏天外出运动的时候穿的衣服"
    advanced_recommend(test_query, db_items, top_k=3)