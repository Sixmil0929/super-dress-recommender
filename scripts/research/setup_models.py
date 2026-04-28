#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置CLIP和DINOv2模型脚本
"""

import sys
import os
import torch
import torchvision.transforms as transforms
from PIL import Image

print("=" * 50)
print("开始模型设置")
print("=" * 50)

# 检查CUDA
print(f"\n✓ torch版本: {torch.__version__}")
print(f"✓ CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ CUDA设备: {torch.cuda.get_device_name(0)}")
    print(f"✓ CUDA版本: {torch.version.cuda}")

# 安装并验证CLIP
print("\n" + "=" * 50)
print("安装CLIP模型")
print("=" * 50)
try:
    import clip
    print("✓ CLIP库已安装")
    print(f"✓ 可用的模型: {clip.available_models()}")
    
    # 下载预训练模型
    print("\n下载CLIP模型 (ViT-B/32)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    print("✓ CLIP模型下载并加载成功!")
    
except ImportError as e:
    print(f"✗ CLIP库安装失败: {e}")
    print("尝试从GitHub安装...")
    os.system(f"{sys.executable} -m pip install git+https://github.com/openai/CLIP.git")
except Exception as e:
    print(f"✗ 加载CLIP模型失败: {e}")

# 安装并验证DINOv2
print("\n" + "=" * 50)
print("安装DINOv2模型")
print("=" * 50)
try:
    # DINOv2可以通过timm或直接从torch.hub加载
    dinov2_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14')
    print("✓ DINOv2 ViT-B/14 模型下载成功!")
    print(f"✓ 模型设备: {next(dinov2_model.parameters()).device}")
    
except Exception as e:
    print(f"⚠ DINOv2从torch.hub加载失败: {e}")
    print("尝试通过timm加载...")
    try:
        from timm.models import create_model
        dinov2_model = create_model('vit_base_patch14_dinov2', pretrained=True)
        print("✓ DINOv2 ViT-B/14 模型加载成功!")
    except Exception as e2:
        print(f"✗ DINOv2加载失败: {e2}")
        print("请手动运行以下命令:")
        print(f"  {sys.executable} -m pip install git+https://github.com/facebookresearch/dinov2.git")

# 创建模型目录
print("\n" + "=" * 50)
print("创建模型目录")
print("=" * 50)
models_dir = "./models"
os.makedirs(models_dir, exist_ok=True)
print(f"✓ 模型目录已创建: {os.path.abspath(models_dir)}")

print("\n" + "=" * 50)
print("模型设置完成!")
print("=" * 50)
print("\n可以开始在你的项目中使用这些模型了。")
