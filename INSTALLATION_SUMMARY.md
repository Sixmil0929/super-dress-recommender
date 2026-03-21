# CLIP 和 DINOv2 模型本地安装完成! ✓

## 安装状态

### ✓ 已安装的Python包:
- **torch** (2.10.0) - 深度学习框架
- **torchvision** (0.25.0) - PyTorch视觉库
- **clip** (1.0) - OpenAI CLIP模型
- **open-clip-torch** - 开源CLIP实现
- **timm** - PyTorch图像模型库  
- **Pillow** - 图像处理库
- **numpy** - 数值计算库

### ✓ 已下载的预训练模型:

#### 1. CLIP 模型
- **模型**: ViT-B/32 (Vision Transformer Base, 32像素patch)
- **大小**: 338 MB
- **位置**: `C:\Users\LOUASUS\.cache\torch\checkpoints\`
- **功能**: 图像-文本匹配、零样本分类

#### 2. DINOv2 模型  
- **模型**: dinov2_vitb14 (Vision Transformer Base 14)
- **大小**: 330 MB
- **位置**: `C:\Users\LOUASUS\.cache\torch\hub\checkpoints\dinov2_vitb14_pretrain.pth`
- **功能**: 自监督特征提取

## 快速开始

### 1. CLIP模型使用
```python
import clip
import torch
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# 加载图像
image = preprocess(Image.open("your_image.jpg")).unsqueeze(0).to(device)

# 准备文本标签
text = clip.tokenize(["white jacket", "red dress", "blue shirt"]).to(device)

# 计算相似度
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)
    similarity = (image_features @ text_features.T).softmax(dim=-1)
    
print(similarity)  # 打印相似度分数
```

### 2. DINOv2模型使用
```python
import torch
from PIL import Image
from torchvision import transforms as T

device = "cuda" if torch.cuda.is_available() else "cpu"
model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14').to(device)
model.eval()

# 图像预处理
transform = T.Compose([
    T.Resize((252, 252)),
    T.ToTensor(),
    T.Normalize(mean=(0.485, 0.456, 0.406), 
                std=(0.229, 0.224, 0.225)),
])

# 加载和处理图像
image_tensor = transform(Image.open("your_image.jpg")).unsqueeze(0).to(device)

# 提取特征
with torch.no_grad():
    features = model(image_tensor)  # 输出形状: [1, 768]
```

## Python环境信息

- **环境类型**: Virtual Environment
- **Python版本**: 3.11.9
- **CUDA**: 不可用 (使用CPU)
- **环境位置**: `d:/dress_recommender/.venv`
- **Python执行路径**: `d:/dress_recommender/.venv/Scripts/python.exe`

## 创建脚本

已为您创建了两个脚本:

### 1. `setup_models.py`
- 功能: 验证模型安装并下载预训练模型
- 用途: 初始化环境，第一次运行时会下载大型模型

### 2. `demo_models.py`
- 功能: 演示CLIP和DINOv2的实际使用
- 用途: 参考代码了解如何使用这两个模型

## 可用的模型变体

### CLIP模型变体:
- `ViT-B/32` ✓ (已下载)
- `ViT-B/16` - 精度更高但更慢
- `ViT-L/14` - 最高精度但最慢
- `ViT-L/14@336px` - 更高分辨率版本

### DINOv2模型变体:
- `dinov2_vits14` - 小模型 (300MB)
- `dinov2_vitb14` ✓ (已下载) - 中等模型 (330MB)  
- `dinov2_vitl14` - 大模型 (1.3GB)
- `dinov2_vitg14` - 最大模型 (2.5GB)

## 使用建议

### 对于服装推荐系统:

1. **CLIP适合用于**:
   - 基于文本描述搜索衣服
   - 零样本属性分类 (如"红色"、"夏季"等)
   - 衣服的跨模态搜索

2. **DINOv2适合用于**:
   - 提取高质量的视觉特征
   - 计算衣服之间的视觉相似度
   - 聚类相似的衣服款式

3. **结合使用**:
   - 使用CLIP进行文本到图像的匹配
   - 使用DINOv2进行图像到图像的相似度搜索
   - 结合两者实现更强大的推荐系统

## 故障排除

如果出现问题:

```bash
# 重新安装CLIP
python -m pip install git+https://github.com/openai/CLIP.git

# 重新下载DINOv2 (会自动缓存)
python -c "import torch; torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14')"

# 清除缓存 (如需要)
# Windows: 删除 C:\Users\[username]\.cache\torch\
```

## 性能提示

- **CPU模式**: 推理速度较慢，但占用内存少，适合测试
- **GPU加速** (如果有CUDA): 
  ```bash
  pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu118
  ```

