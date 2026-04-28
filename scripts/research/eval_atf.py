import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import clip
from torchvision import transforms as T
from PIL import Image
import pandas as pd
from tqdm import tqdm 

# ==========================================
# 1. 核心网络：必须和训练时的完全体一模一样！
# ==========================================
class DualPathATF(nn.Module):
    def __init__(self, clip_dim=768, dino_dim=1024, embed_dim=768, num_heads=8):
        super().__init__()
        self.proj_clip = nn.Linear(clip_dim, embed_dim)
        self.proj_dino = nn.Linear(dino_dim, embed_dim)
        
        self.self_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
        self.norm = nn.LayerNorm(embed_dim)
        
        self.gate_net = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.Sigmoid()
        )
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
        
        super_vector = self.fusion_norm(fused_features)
        return super_vector

# ==========================================
# 2. 评估数据集：验证集读取 (抽取测试数据)
# ==========================================
class EvalFashionDataset(Dataset):
    def __init__(self, data_dir, ann_file, clip_transform, dino_transform):
        self.data_dir = data_dir
        self.clip_transform = clip_transform
        self.dino_transform = dino_transform
        
        print(f"📂 正在读取评估数据: {ann_file} ...")
        self.df = pd.read_feather(ann_file).dropna(subset=['path', 'caption'])
        # 🌟 核心操作：截取最后 1000 条未见过的数据作为测试集！绝不作弊！
        self.df = self.df.tail(1000).reset_index(drop=True) 
        print(f"✅ 成功划定 {len(self.df)} 条测试数据！")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = os.path.normpath(os.path.join(self.data_dir, str(row['path']).strip()))
        text = str(row['caption']).strip()
        
        image = Image.open(img_path).convert("RGB")
        img_clip = self.clip_transform(image)
        img_dino = self.dino_transform(image)
        text_token = clip.tokenize([text], truncate=True)[0]
        
        return img_clip, img_dino, text_token

# ==========================================
# 3. 终极体检中心：全图库相似度匹配与 Recall 计算
# ==========================================
def evaluate():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 启动 {device} 阅卷引擎...")

    # ================= 路径配置区 =================
    # 👇 请修改为你的实际路径，记得指向你辛辛苦苦跑出来的 atf_epoch_30.pth！
    data_dir = r"D:\dress_recommender\DeepFashion_Data\selected_images" 
    ann_file = r"D:\dress_recommender\DeepFashion_Data\labels_front.feather" 
    weight_path = r"D:\dress_recommender\weights\atf_epoch_30.pth" 
    # ==============================================

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
    
    if not os.path.exists(weight_path):
        print(f"\n💥 找不到权重文件 {weight_path}！请检查路径！")
        return
        
    # 注入灵魂：加载你跑出来的黄金权重
    atf_model.load_state_dict(torch.load(weight_path, map_location=device))
    atf_model.eval()
    print(f"✨ 成功加载黄金权重: {weight_path}")

    dataset = EvalFashionDataset(data_dir, ann_file, clip_preprocess, dino_transform)
    # 评估时不需要计算梯度，batch_size 可以开大一点
    dataloader = DataLoader(dataset, batch_size=64, shuffle=False, num_workers=4)

    all_super_vectors = []
    all_text_features = []

    print("🔍 正在疯狂提取全局图文特征...")
    with torch.no_grad():
        for img_clip, img_dino, text_tokens in tqdm(dataloader):
            img_clip, img_dino, text_tokens = img_clip.to(device), img_dino.to(device), text_tokens.to(device)
            
            raw_f_clip = clip_model.encode_image(img_clip)
            raw_f_dino = dino_model(img_dino)
            text_features = clip_model.encode_text(text_tokens).float()
            
            f_clip = torch.nn.functional.normalize(raw_f_clip, dim=-1).float()
            f_dino = torch.nn.functional.normalize(raw_f_dino, dim=-1).float()
            
            super_vectors = atf_model(f_clip, f_dino)
            
            all_super_vectors.append(super_vectors)
            all_text_features.append(text_features)
            
    all_super_vectors = torch.cat(all_super_vectors, dim=0)
    all_text_features = torch.cat(all_text_features, dim=0)

    # 强制 L2 归一化以计算正确的余弦相似度
    all_super_vectors = nn.functional.normalize(all_super_vectors, dim=-1)
    all_text_features = nn.functional.normalize(all_text_features, dim=-1)

    print("🧮 正在计算 1000 x 1000 的超大相似度矩阵...")
    # 核心测试：用文本去大海捞针找图片！
    sim_matrix = torch.matmul(all_text_features, all_super_vectors.T)

    # 统计 Recall@1, 5, 10
    num_samples = sim_matrix.shape[0]
    ranks = torch.argsort(sim_matrix, dim=-1, descending=True)
    
    # 对角线就是它本来对应的正确图片
    targets = torch.arange(num_samples).to(device).view(-1, 1)
    matches = (ranks == targets)

    r1 = matches[:, :1].sum().item() / num_samples * 100
    r5 = matches[:, :5].sum().item() / num_samples * 100
    r10 = matches[:, :10].sum().item() / num_samples * 100

    print("\n" + "="*45)
    print("🏆 炼丹终极成绩单 (Text-to-Image Retrieval)")
    print("="*45)
    print(f"🥇 Recall@1 : {r1:.2f}% (一发入魂的概率)")
    print(f"🥈 Recall@5 : {r5:.2f}% (前五名命中的概率)")
    print(f"🥉 Recall@10: {r10:.2f}% (前十名命中的概率)")
    print("="*45)

if __name__ == "__main__":
    evaluate()