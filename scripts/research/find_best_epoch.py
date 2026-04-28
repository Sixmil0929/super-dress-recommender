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
# 1. 核心网络：不可撼动的基石
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
        # 截取最后 1000 条未见过的数据作为公平考场！
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
# 3. 极速阅卷引擎：遍历 30 个 Epoch
# ==========================================
def find_best_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 启动 {device} 极速自动化选优引擎...")

    # ================= 路径配置区 =================
    data_dir = r"D:\dress_recommender\DeepFashion_Data\selected_images" 
    ann_file = r"D:\dress_recommender\DeepFashion_Data\labels_front.feather" 
    weights_dir = r"D:\dress_recommender\weights" 
    # ==============================================

    print("⏳ 正在唤醒基座模型 CLIP & DINOv2...")
    clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)
    clip_model.eval()
    
    dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitl14', pretrained=True).to(device)
    dino_model.eval()

    dino_transform = T.Compose([
        T.Resize((518, 518), interpolation=T.InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
    ])

    dataset = EvalFashionDataset(data_dir, ann_file, clip_preprocess, dino_transform)
    dataloader = DataLoader(dataset, batch_size=64, shuffle=False, num_workers=4)

    # 🌟 绝杀优化：提前把基座特征全提出来，只需要做一次！
    all_f_clip = []
    all_f_dino = []
    all_text_features = []

    print("🔍 [阶段一] 正在一次性提取测试集的全局基座特征 (只需提一次)...")
    with torch.no_grad():
        for img_clip, img_dino, text_tokens in tqdm(dataloader):
            img_clip, img_dino, text_tokens = img_clip.to(device), img_dino.to(device), text_tokens.to(device)
            
            raw_f_clip = clip_model.encode_image(img_clip)
            raw_f_dino = dino_model(img_dino)
            text_features = clip_model.encode_text(text_tokens).float()
            
            f_clip = torch.nn.functional.normalize(raw_f_clip, dim=-1).float()
            f_dino = torch.nn.functional.normalize(raw_f_dino, dim=-1).float()
            text_features = torch.nn.functional.normalize(text_features, dim=-1)
            
            all_f_clip.append(f_clip)
            all_f_dino.append(f_dino)
            all_text_features.append(text_features)
            
    all_f_clip = torch.cat(all_f_clip, dim=0)
    all_f_dino = torch.cat(all_f_dino, dim=0)
    all_text_features = torch.cat(all_text_features, dim=0)
    
    # 清理不再需要的基座大模型以腾出显存
    del clip_model
    del dino_model
    torch.cuda.empty_cache()

    print("\n⚔️ [阶段二] 开始让 30 个 Epoch 的模型排队考试...")
    atf_model = DualPathATF().to(device)
    
    best_epoch = -1
    best_r1 = -1.0
    best_r5 = -1.0
    best_r10 = -1.0
    
    results_log = []

    # 遍历 1 到 30 个 Epoch 的权重
    for epoch in range(1, 31):
        weight_path = os.path.join(weights_dir, f"atf_epoch_{epoch}.pth")
        
        if not os.path.exists(weight_path):
            continue
            
        atf_model.load_state_dict(torch.load(weight_path, map_location=device))
        atf_model.eval()
        
        with torch.no_grad():
            # 直接用预提取好的特征输入给 ATF
            super_vectors = atf_model(all_f_clip, all_f_dino)
            super_vectors = nn.functional.normalize(super_vectors, dim=-1)
            
            # 计算相似度矩阵
            sim_matrix = torch.matmul(all_text_features, super_vectors.T)
            
            num_samples = sim_matrix.shape[0]
            ranks = torch.argsort(sim_matrix, dim=-1, descending=True)
            targets = torch.arange(num_samples).to(device).view(-1, 1)
            matches = (ranks == targets)

            r1 = matches[:, :1].sum().item() / num_samples * 100
            r5 = matches[:, :5].sum().item() / num_samples * 100
            r10 = matches[:, :10].sum().item() / num_samples * 100
            
            results_log.append((epoch, r1, r5, r10))
            print(f"   ▫️ Epoch {epoch:02d} | R@1: {r1:.2f}% | R@5: {r5:.2f}% | R@10: {r10:.2f}%")
            
            # 记录历史最高分 (以 Recall@1 为主指标)
            if r1 > best_r1:
                best_r1 = r1
                best_r5 = r5
                best_r10 = r10
                best_epoch = epoch

    print("\n" + "="*50)
    print(f"👑 最终选拔结果：真正的王中王是 【Epoch {best_epoch}】！")
    print("="*50)
    print(f"🥇 其 Recall@1 成绩: {best_r1:.2f}%")
    print(f"🥈 其 Recall@5 成绩: {best_r5:.2f}%")
    print(f"🥉 其 Recall@10成绩: {best_r10:.2f}%")
    print(f"👉 请在后续的建库代码中，使用 atf_epoch_{best_epoch}.pth 作为最终的黄金权重！")
    print("="*50)

if __name__ == "__main__":
    find_best_model()