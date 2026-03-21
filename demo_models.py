#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLIP和DINOv2模型使用示例
"""

import torch
import clip
from PIL import Image
import numpy as np
from pathlib import Path

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")

# ===========================
# CLIP 模型使用示例
# ===========================
print("\n" + "=" * 50)
print("CLIP 模型演示")
print("=" * 50)

# 加载CLIP模型
clip_model, preprocess = clip.load("ViT-B/32", device=device)

# 示例：图像-文本相似度
sample_image_path = "./P1_Dataset/images"  # 修改为你的实际图片路径
image_paths = list(Path(sample_image_path).glob("*.jpg")) + list(Path(sample_image_path).glob("*.png"))

if image_paths:
    # 加载第一张图片作为示例
    image = preprocess(Image.open(image_paths[0])).unsqueeze(0).to(device)
    
    # 准备文本标签
    text_labels = ["red dress", "blue shirt", "black pants", "white jacket", "summer outfit"]
    text_tokens = clip.tokenize(text_labels).to(device)
    
    # 获取图像和文本的特征向量
    with torch.no_grad():
        image_features = clip_model.encode_image(image)
        text_features = clip_model.encode_text(text_tokens)
        
        # 计算相似度
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    
    print(f"\n图片: {image_paths[0].name}")
    print("与各标签的相似度:")
    for label, sim in zip(text_labels, similarity[0]):
        print(f"  {label}: {sim.item():.4f}")
else:
    print("未找到示例图片，跳过CLIP演示")

# ===========================
# DINOv2 模型使用示例
# ===========================
print("\n" + "=" * 50)
print("DINOv2 模型演示")
print("=" * 50)

# 加载DINOv2模型
dinov2_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14').to(device)
dinov2_model.eval()

if image_paths:
    # 加载图片
    image_pil = Image.open(image_paths[0]).convert('RGB')
    
    # DINOv2需要的预处理
    transform = torch.nn.Sequential(
        torch.nn.Identity()  # 在实际应用中需要适当的预处理
    )
    
    # 使用torchvision的标准预处理
    from torchvision import transforms as T
    
    IMAGENET_DEFAULT_MEAN = (0.485, 0.456, 0.406)
    IMAGENET_DEFAULT_STD = (0.229, 0.224, 0.225)
    
    transform = T.Compose([
        T.Resize((252, 252)),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD),
    ])
    
    image_tensor = transform(image_pil).unsqueeze(0).to(device)
    
    # 提取特征
    with torch.no_grad():
        features = dinov2_model(image_tensor)
    
    print(f"\n图片: {image_paths[0].name}")
    print(f"DINOv2特征向量维度: {features.shape}")
    print(f"特征向量前5个值: {features[0][:5]}")
else:
    print("未找到示例图片，跳过DINOv2演示")

print("\n" + "=" * 50)
print("示例演示完成!")
print("=" * 50)

# ===========================
# 保存模型使用说明
# ===========================
usage_guide = """
# 模型使用指南

## CLIP 模型
- 用途: 图像-文本匹配和分类
- 模型: ViT-B/32 (可选: ViT-B/16, ViT-L/14等)
- 特点: 可以通过自然语言描述进行图像检索

示例代码:
```python
import clip
import torch
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# 加载图像
image = preprocess(Image.open("dress.jpg")).unsqueeze(0).to(device)

# 准备文本
text = clip.tokenize(["red dress", "blue shirt"]).to(device)

with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)
    
    similarity = (image_features @ text_features.T).softmax(dim=-1)
```

## DINOv2 模型
- 用途: 自监督特征提取
- 模型: ViT-B/14 (可选: ViT-B/14_reg, ViT-L/14等)
- 特点: 提供高质量的、未标记的特征表示

示例代码:
```python
import torch
from torchvision import transforms as T

device = "cuda" if torch.cuda.is_available() else "cpu"
model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14').to(device)
model.eval()

# 预处理
transform = T.Compose([
    T.Resize((252, 252)),
    T.ToTensor(),
    T.Normalize(mean=(0.485, 0.456, 0.406), 
                std=(0.229, 0.224, 0.225)),
])

# 获取特征
import PIL.Image as Image
image = Image.open("dress.jpg").convert('RGB')
image_tensor = transform(image).unsqueeze(0).to(device)

with torch.no_grad():
    features = model(image_tensor)  # 形状: [1, 257, 768]
```

## 可用的模型变体

### CLIP 模型:
- ViT-B/32: 最常用，速度快
- ViT-B/16: 精度更高
- ViT-L/14: 最准确但最慢
- ViT-L/14@336px: 340像素版本

### DINOv2 模型:
- dinov2_vits14: 小模型，快速
- dinov2_vitb14: 中等模型，推荐
- dinov2_vitl14: 大模型，精度高
- dinov2_vitg14: 最大模型，最高精度

## 常见操作

### 1. 图像分类 (使用CLIP)
所有不同的图像分类任务都可以通过CLIP的文本编码器实现零样本分类

### 2. 特征提取 (使用DINOv2)
提取图像特征用于聚类、相似度搜索等任务

### 3. 相似性搜索
使用CLIP或DINOv2提取特征后，可以计算特征之间的余弦相似度
"""

with open("./MODEL_USAGE_GUIDE.md", "w", encoding="utf-8") as f:
    f.write(usage_guide)

print("\n💡 详细使用指南已保存到: MODEL_USAGE_GUIDE.md")
