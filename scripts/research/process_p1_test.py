import os
import torch
import clip
import pandas as pd
import psycopg2
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image

# ==========================================
# 1. 核心融合模块：ATF (Adaptive Token Features Fusion)
# ==========================================
class SimpleATFBlock(nn.Module):
    def __init__(self, d_clip=768, d_dino=1024, d_head=512):
        super().__init__()
        self.q_c = nn.Linear(d_clip, d_head)
        self.k_d = nn.Linear(d_dino, d_head)
        self.v_d = nn.Linear(d_dino, d_head)
        
        self.mlp = nn.Sequential(
            nn.Linear(d_head, d_head),
            nn.GELU(),
            nn.Linear(d_head, d_clip)
        )
        
    def forward(self, f_c, f_d):
        q = self.q_c(f_c) 
        k = self.k_d(f_d) 
        v = self.v_d(f_d) 
        
        attn_weights = torch.softmax(torch.bmm(q.unsqueeze(1), k.transpose(1, 2)) / (512**0.5), dim=-1)
        attn_out = torch.bmm(attn_weights, v).squeeze(1) 
        
        super_vec = f_c + self.mlp(attn_out)
        return super_vec

# ==========================================
# 2. 环境与模型初始化 (彻底拥抱 DINOv2)
# ==========================================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"正在使用 {device} 设备加载模型...")

# 1. 加载 CLIP (补丁14)
clip_model, _ = clip.load("ViT-L/14", device=device)
clip_model.eval()

# 2. 加载 DINOv2 (补丁14，不用申请权限，直接白嫖！)
dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitl14', pretrained=True).to(device)
dino_model.eval()

atf_module = SimpleATFBlock().to(device)
atf_module.eval()

# 3. 严格对齐分辨率！因为都是 14 的补丁，所以全缩放到 518！
clip_transform = T.Compose([
    T.Resize(224, interpolation=T.InterpolationMode.BICUBIC),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
])
dino_transform = T.Compose([
    T.Resize((518, 518), interpolation=T.InterpolationMode.BICUBIC),
    T.ToTensor(),
    T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
])

# ==========================================
# 3. 扩充后的超级标签池 (Tag Pool)
# ==========================================
tag_pool = [
    # 风格与场景
    "sporty", "formal", "casual", "vintage", "streetwear", 
    "romantic dating", "business casual", "minimalist", "outdoor", "sweet",
    # 材质
    "cotton", "denim", "leather",
    # 基础品类
    "T-shirt", "shirt", "sweater", "hoodie", "jacket", "coat", 
    "jeans", "trousers", "shorts", "dress", "skirt",
    # 季节
    "spring", "summer", "autumn", "winter",
    # 图案
    "striped", "plaid", "floral",
    # 具体颜色
    "black", "white", "gray", "red", "blue", 
    "green", "yellow", "pink", "brown", "purple"
]

# 将标签转化为 CLIP 能懂的文本特征向量格式
text_inputs = torch.cat([clip.tokenize(f"a photo of a {t} clothing") for t in tag_pool]).to(device)

# ==========================================
# 4. 数据库连接与批量处理
# ==========================================
print("正在连接 PostgreSQL 数据库...")
conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
conn.autocommit = True
cursor = conn.cursor()

csv_path = 'D:\\dress_recommender\\P1_Dataset\\P1_Dataset.csv' # 请确保你的CSV文件名是这个，否则需要修改
df = pd.read_csv(csv_path, encoding='gbk')

print(f"开始处理 {len(df)} 张图片，请稍候...")

for index, row in df.iterrows():
    img_name = row['Filename']
    img_path = os.path.join('P1_Dataset', 'images', img_name)
    
    if not os.path.exists(img_path):
        print(f"⚠️ 找不到图片: {img_path}，已跳过。")
        continue

    try:
        raw_img = Image.open(img_path).convert('RGB')
        
        img_clip = clip_transform(raw_img).unsqueeze(0).to(device)
        img_dino = dino_transform(raw_img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            # --- A. CLIP 文字打标签 ---
            image_features = clip_model.encode_image(img_clip)
            text_features = clip_model.encode_text(text_inputs)
            
            # 计算相似度
            image_features_norm = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features_norm = text_features / text_features.norm(dim=-1, keepdim=True)
            similarity = (100.0 * image_features_norm @ text_features_norm.T).softmax(dim=-1)
            
            # 提取得分最高的 5 个标签
            top_indices = similarity[0].topk(5).indices
            clip_tags = ", ".join([tag_pool[i] for i in top_indices])
            
            # --- B. 提取特征并融合生成超级向量 ---
            dino_features = dino_model.forward_features(img_dino)["x_norm_patchtokens"]
            super_vector = atf_module(image_features.float(), dino_features.float())
            super_vector_list = super_vector.squeeze().tolist()
        
        # --- C. 数据入库 ---
        insert_query = """
            INSERT INTO clothing_features 
            (filename, brand, price, gender, has_model, clip_tags, super_vector)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            img_name, row['Brand'], row['Price'], row['Gender'], row['Has_Model'], 
            clip_tags, super_vector_list
        ))
        
        if (index + 1) % 10 == 0:
            print(f"✅ 进度：已成功处理并入库 {index + 1} / {len(df)} 张图片... 最新的标签提取结果为: [{clip_tags}]")

    except Exception as e:
        print(f"❌ 处理 {img_name} 时发生错误: {e}")

cursor.close()
conn.close()
print("🎉 P1_Dataset 全部处理完毕，超级向量与文字标签已完美入库！")