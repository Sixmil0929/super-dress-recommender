
# import os
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from torch.utils.data import Dataset, DataLoader
# import clip
# from torchvision import transforms as T
# from PIL import Image
# import pandas as pd
# from tqdm import tqdm 

# # ✨ 魔法结界和它的配套防具
# from torch.amp import autocast, GradScaler 

# # ==========================================
# # 1. 核心网络：序列化自注意力特征融合 (Self-Attention ATF)
# # ==========================================
# class DualPathATF(nn.Module):
#     def __init__(self, clip_dim=768, dino_dim=1024, embed_dim=768, num_heads=8):
#         super().__init__()
#         # 1. 统一维度映射
#         self.proj_clip = nn.Linear(clip_dim, embed_dim)
#         self.proj_dino = nn.Linear(dino_dim, embed_dim)
        
#         # 2. 🌟 真正的灵魂交互：自注意力机制
#         self.self_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
#         self.norm = nn.LayerNorm(embed_dim)
        
#         # 3. 门控压缩层
#         self.fusion_ffn = nn.Sequential(
#             nn.Linear(embed_dim * 2, embed_dim),
#             nn.GELU(),
#             nn.Linear(embed_dim, embed_dim)
#         )

#     def forward(self, f_clip, f_dino):
#         # 映射到相同的 768 维空间
#         q_clip = self.proj_clip(f_clip)
#         q_dino = self.proj_dino(f_dino)
        
#         # 🌟 神级操作：把它们叠成一个长度为 2 的序列！shape: (Batch, 2, 768)
#         seq = torch.stack([q_clip, q_dino], dim=1) 
        
#         # 让 CLIP 和 DINO 在自注意力中互相审视对方！
#         attn_out, _ = self.self_attn(query=seq, key=seq, value=seq)
#         seq_out = self.norm(seq + attn_out)
        
#         # 拆解出吸取了对方精华的新 token
#         fused_clip = seq_out[:, 0, :]
#         fused_dino = seq_out[:, 1, :]
        
#         # 拼接并压缩成最终的超级向量
#         super_vector = self.fusion_ffn(torch.cat([fused_clip, fused_dino], dim=-1))
        
#         return super_vector
#         # ==========================================
#         # 模块三：终极融合器 (选项 B 测试场)
#         # ==========================================
#         if self.use_gated_fusion:
#             # 高级门控融合 (Gated Fusion)
#             # 生成 (0, 1) 之间的权重阀门
#             self.gate_net = nn.Sequential(
#                 nn.Linear(embed_dim * 2, embed_dim),
#                 nn.Sigmoid()
#             )
#             # 融合后微调
#             self.fusion_norm = nn.LayerNorm(embed_dim)
#         else:
#             # 经典的 Concat + MLP 融合
#             self.fusion_ffn = nn.Sequential(
#                 nn.Linear(embed_dim * 2, embed_dim),
#                 nn.GELU(),
#                 nn.Linear(embed_dim, embed_dim)
#             )

#     def forward(self, f_clip, f_dino):
#         # 1. 投影到共享空间
#         q_clip = self.proj_clip(f_clip)
#         kv_dino = self.proj_dino(f_dino)
        
#         q_dino = kv_dino
#         kv_clip = q_clip
        
#         # 2. 双向交互
#         out_A, _ = self.cross_attn_A(query=q_clip, key=kv_dino, value=kv_dino)
#         out_A = self.norm1(q_clip + out_A) # 带有DINO细节的CLIP
        
#         out_B, _ = self.cross_attn_B(query=q_dino, key=kv_clip, value=kv_clip)
#         out_B = self.norm2(q_dino + out_B) # 带有CLIP语义的DINO
        
#         # 3. 终极融合
#         if self.use_gated_fusion:
#             # 计算门控权重 g
#             g = self.gate_net(torch.cat([out_A, out_B], dim=-1))
#             # 动态加权融合 (g*A + (1-g)*B)
#             fused_features = g * out_A + (1 - g) * out_B
#             final_super_vector = self.fusion_norm(fused_features)
#         else:
#             # 原始粗暴拼接法
#             fused_features = torch.cat([out_A, out_B], dim=-1)
#             final_super_vector = self.fusion_ffn(fused_features)
        
#         return final_super_vector
# # ==========================================
# # 2. 数据读取器：解析 DeepFashion (光速 feather 版)
# # ==========================================
# class DeepFashionDataset(Dataset):
#     def __init__(self, data_dir, ann_file, clip_transform, dino_transform):
#         self.data_dir = data_dir
#         self.clip_transform = clip_transform
#         self.dino_transform = dino_transform
        
#         print(f"📂 正在使用光速引擎读取羽毛文件: {ann_file} ...")
#         self.df = pd.read_feather(ann_file)
#         self.df = self.df.dropna(subset=['path', 'caption'])
#         self.df = self.df.head(320)
#         print(f"✅ 成功加载了 {len(self.df)} 条有效图文数据！")

#     def __len__(self):
#         return len(self.df)

#     def __getitem__(self, idx):
#         row = self.df.iloc[idx]
        
#         img_rel_path = str(row['path']).strip()
#         img_path = os.path.join(self.data_dir, img_rel_path)
#         text = str(row['caption']).strip()
        
#         try:
#             image = Image.open(img_path).convert("RGB")
#             img_clip = self.clip_transform(image)
#             img_dino = self.dino_transform(image)
#         except Exception as e:
#             image = Image.new('RGB', (224, 224), (0, 0, 0))
#             img_clip = self.clip_transform(image)
#             img_dino = self.dino_transform(image)
            
#         text_token = clip.tokenize([text], truncate=True)[0]
        
#         return img_clip, img_dino, text_token

# # ==========================================
# # 3. 损失函数：InfoNCE 图文对比学习
# # ==========================================
# class ContrastiveLoss(nn.Module):
#     def __init__(self, temperature=0.2):
#         super().__init__()
#         self.temperature = temperature
#         self.cross_entropy = nn.CrossEntropyLoss()

#     def forward(self, super_vectors, text_features):
#         super_vectors = nn.functional.normalize(super_vectors, dim=-1)
#         text_features = nn.functional.normalize(text_features, dim=-1)
        
#         logits = torch.matmul(super_vectors, text_features.T) / self.temperature
#         labels = torch.arange(logits.shape[0]).to(logits.device)
        
#         loss_i2t = self.cross_entropy(logits, labels)
#         loss_t2i = self.cross_entropy(logits.T, labels)
        
#         return (loss_i2t + loss_t2i) / 2

# # ==========================================
# # 4. 主训练循环 (让显卡优雅地狂飙！)
# # ==========================================
# def train():
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"🚀 正在使用 {device} 准备训练大模型融合矩阵...")

#     # ================= 路径配置区 =================
#     data_dir = r"D:\dress_recommender\DeepFashion_Data" 
#     ann_file = r"D:\dress_recommender\DeepFashion_Data\labels_front.feather" 
#     save_dir = r"D:\dress_recommender\weights" 
#     os.makedirs(save_dir, exist_ok=True)
#     # ==============================================

#     clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)
#     clip_model.eval()
    
#     dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitl14', pretrained=True).to(device)
#     dino_model.eval()

#     dino_transform = T.Compose([
#         T.Resize((518, 518), interpolation=T.InterpolationMode.BICUBIC),
#         T.ToTensor(),
#         T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
#     ])

#     # 终极形态：CLIP进768，DINO进1024，在768的隐空间里完美融合出768维的超级向量！
#     atf_model = DualPathATF(clip_dim=768, dino_dim=1024, embed_dim=768).to(device)
#     atf_model.train()
#     # 💥 极速测试专属猛药：随机初始化的网络，必须给足火力！
#     optimizer = optim.AdamW(atf_model.parameters(), lr=1e-3, weight_decay=1e-4)
#     criterion = ContrastiveLoss()

#     # 🛡️ 召唤梯度缩放器（配合 AMP 使用的最强防具）
#     scaler = GradScaler('cuda')

#     dataset = DeepFashionDataset(data_dir, ann_file, clip_preprocess, dino_transform)
#     dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4, pin_memory=True)

#     num_epochs = 50
#     print("🔥 开始优雅地炼丹！")
    
#     for epoch in range(num_epochs):
#         atf_model.train()
#         total_loss = 0
        
#         pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{num_epochs}")
        
#         for batch_idx, (img_clip, img_dino, text_tokens) in enumerate(pbar):
#             img_clip = img_clip.to(device)
#             img_dino = img_dino.to(device)
#             text_tokens = text_tokens.to(device)
            
#             # 提取基座特征
#             with torch.no_grad():
#                 raw_f_clip = clip_model.encode_image(img_clip)
#                 raw_f_dino = dino_model(img_dino)
#                 text_features = clip_model.encode_text(text_tokens)
                
#                 # 🛡️ 终极补丁：归一化巨兽，强行统一量级！(绝对不能漏掉这步)
#                 f_clip = torch.nn.functional.normalize(raw_f_clip, dim=-1).unsqueeze(1)
#                 f_dino = torch.nn.functional.normalize(raw_f_dino, dim=-1).unsqueeze(1)
            
#             optimizer.zero_grad()
            
#             # ✨ 魔法结界启动：自动处理所有精度冲突
#             with autocast(device_type="cuda"):
#                 super_vectors = atf_model(f_clip, f_dino).squeeze(1)
#                 loss = criterion(super_vectors, text_features)
#                 if batch_idx % 5 == 0:
#                     # 算一下当前 Batch 里，第一件衣服和它自己文本的相似度
#                     sim_matrix = torch.matmul(nn.functional.normalize(super_vectors, dim=-1), 
#                                               nn.functional.normalize(text_features, dim=-1).T)
                    
#                     # 正确答案的分数（对角线） vs 错误答案的平均分数
#                     correct_score = sim_matrix[0, 0].item() # 自己找自己的分数
#                     wrong_score = sim_matrix[0, 1].item()   # 自己找别人文本的分数
                    
#                     # 用 tqdm 打印出来，不打乱进度条
#                     tqdm.write(f"🔍 [直观监控] 正确匹配得分: {correct_score:.3f} | 错误匹配得分: {wrong_score:.3f}")
            
#             # 🛡️ 使用缩放器进行反向传播和参数更新
#             scaler.scale(loss).backward()
#             scaler.step(optimizer)
#             scaler.update()
            
#             total_loss += loss.item()
#             pbar.set_postfix({"Loss": f"{loss.item():.4f}"})
            
#         avg_loss = total_loss / len(dataloader)
#         print(f"🌟 Epoch {epoch+1} 完成! 平均 Loss: {avg_loss:.4f}")
        
#         save_path = os.path.join(save_dir, f"atf_epoch_{epoch+1}.pth")
#         torch.save(atf_model.state_dict(), save_path)
#         print(f"💾 权重已自动保存至: {save_path}\n")

# if __name__ == "__main__":
#     train()
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import clip
from torchvision import transforms as T
from PIL import Image
import pandas as pd
import numpy as np
from tqdm import tqdm 

# ==========================================
# 1. 核心网络：完全体 ATF (序列自注意力 + 高级门控)
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
# 2. 数据读取器：全量真实数据读取
# ==========================================
class DeepFashionDataset(Dataset):
    def __init__(self, data_dir, ann_file, clip_transform, dino_transform):
        self.data_dir = data_dir
        self.clip_transform = clip_transform
        self.dino_transform = dino_transform
        
        print(f"📂 正在读取羽毛文件: {ann_file} ...")
        self.df = pd.read_feather(ann_file)
        self.df = self.df.dropna(subset=['path', 'caption'])
        
        # 🌟 已经去除了 .head(320) 外挂，现在是全量 1.2 万张图的真实战场！
        print(f"✅ 成功加载全量数据：共 {len(self.df)} 条有效图文！")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_rel_path = str(row['path']).strip()
        img_path = os.path.normpath(os.path.join(self.data_dir, img_rel_path))
        text = str(row['caption']).strip()
        
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"\n💥 致命路径错误！找不到图片: {img_path}")
            
        image = Image.open(img_path).convert("RGB")
        img_clip = self.clip_transform(image)
        img_dino = self.dino_transform(image)
        text_token = clip.tokenize([text], truncate=True)[0]
        
        return img_clip, img_dino, text_token

# ==========================================
# 3. 损失函数：大厂级 InfoNCE (带自适应温度系数)
# ==========================================
class ContrastiveLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.logit_scale = nn.Parameter(torch.ones([]) * np.log(1 / 0.07))
        self.cross_entropy = nn.CrossEntropyLoss()

    def forward(self, super_vectors, text_features):
        super_vectors = nn.functional.normalize(super_vectors, dim=-1)
        text_features = nn.functional.normalize(text_features, dim=-1)
        
        logit_scale = self.logit_scale.exp()
        logits = logit_scale * torch.matmul(super_vectors, text_features.T)
        
        labels = torch.arange(logits.shape[0]).to(logits.device)
        loss_i2t = self.cross_entropy(logits, labels)
        loss_t2i = self.cross_entropy(logits.T, labels)
        
        return (loss_i2t + loss_t2i) / 2

# ==========================================
# 4. 主训练循环 (稳健长跑版)
# ==========================================
def train():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 正在使用 {device} 准备全量数据炼丹...")

    # ⚠️ 上云服务器后，请根据云端的实际路径修改这里！
    data_dir = r"D:\dress_recommender\DeepFashion_Data\selected_images" 
    ann_file = r"D:\dress_recommender\DeepFashion_Data\labels_front.feather" 
    save_dir = r"D:\dress_recommender\weights" 
    os.makedirs(save_dir, exist_ok=True)

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
    criterion = ContrastiveLoss().to(device)
    
    # 全量数据长跑，使用稳健的 1e-4 学习率
    params = list(atf_model.parameters()) + list(criterion.parameters())
    optimizer = optim.AdamW(params, lr=1e-4, weight_decay=1e-4)

    dataset = DeepFashionDataset(data_dir, ann_file, clip_preprocess, dino_transform)
    
    # 🌟 云端服务器通常 CPU 核心多，可以把 num_workers 开到 4 或 8 加速读图
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4, pin_memory=True)

    num_epochs = 30
    print("🔥 全量引擎点火！挂机开始！")
    
    for epoch in range(num_epochs):
        atf_model.train()
        total_loss = 0
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{num_epochs}")
        
        for batch_idx, (img_clip, img_dino, text_tokens) in enumerate(pbar):
            img_clip = img_clip.to(device)
            img_dino = img_dino.to(device)
            text_tokens = text_tokens.to(device)
            
            with torch.no_grad():
                raw_f_clip = clip_model.encode_image(img_clip)
                raw_f_dino = dino_model(img_dino)
                text_features = clip_model.encode_text(text_tokens).float()
                
                f_clip = torch.nn.functional.normalize(raw_f_clip, dim=-1).float()
                f_dino = torch.nn.functional.normalize(raw_f_dino, dim=-1).float()
            
            optimizer.zero_grad()
            super_vectors = atf_model(f_clip, f_dino)
            loss = criterion(super_vectors, text_features)
            
            loss.backward()
            optimizer.step()
            
            # 降低全量训练时的打印频率，避免满屏都是日志
            if batch_idx % 50 == 0:
                sim_matrix = torch.matmul(nn.functional.normalize(super_vectors, dim=-1), 
                                          nn.functional.normalize(text_features, dim=-1).T)
                correct_score = sim_matrix[0, 0].item()
                wrong_score = sim_matrix[0, 1].item()
                tqdm.write(f"   👉 [监控] 正确得分: {correct_score:.3f} | 错配得分: {wrong_score:.3f} | 温度: {criterion.logit_scale.exp().item():.2f}")
            
            total_loss += loss.item()
            pbar.set_postfix({"Loss": f"{loss.item():.4f}"})
            
        avg_loss = total_loss / len(dataloader)
        print(f"🌟 Epoch {epoch+1} 完成! 平均 Loss: {avg_loss:.4f}\n")
        
        # 每个 Epoch 跑完自动保存权重！
        save_path = os.path.join(save_dir, f"atf_epoch_{epoch+1}.pth")
        torch.save(atf_model.state_dict(), save_path)
        print(f"💾 权重已安全保存至: {save_path}\n")

if __name__ == "__main__":
    train()