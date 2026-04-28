
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
