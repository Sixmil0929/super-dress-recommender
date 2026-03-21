import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==========================================
# 1. 准备数据 (正则解析日志)
# ==========================================
# 将你的日志文本粘贴到这里（为了演示，这里截取了部分特征明显的占位，建议替换为你的全量txt）
log_data = """
[此处替换为你的完整训练日志，代码会自动用正则把数据全抠出来]
"""

# 如果你已经把它存成了 txt 文件，可以用下面两行读取：
with open("双路融合模型训练.txt", "r", encoding="utf-8") as f:
    log_data = f.read()

# 正则表达式提取
loss_pattern = re.compile(r"🌟 Epoch (\d+) 完成! 平均 Loss: ([\d.]+)")
monitor_pattern = re.compile(r"👉 \[监控\] 正确得分: ([-.\d]+) \| 错配得分: ([-.\d]+) \| 温度: ([-.\d]+)")

epochs = []
losses = []
# 用于按 Epoch 分组计算平均得分和温度
current_epoch_scores = {'correct': [], 'mismatch': [], 'temp': []}
avg_correct = []
avg_mismatch = []
avg_temp = []

lines = log_data.strip().split('\n')
for line in lines:
    m_monitor = monitor_pattern.search(line)
    if m_monitor:
        current_epoch_scores['correct'].append(float(m_monitor.group(1)))
        current_epoch_scores['mismatch'].append(float(m_monitor.group(2)))
        current_epoch_scores['temp'].append(float(m_monitor.group(3)))
        
    m_loss = loss_pattern.search(line)
    if m_loss:
        epochs.append(int(m_loss.group(1)))
        losses.append(float(m_loss.group(2)))
        
        # 结算当前 Epoch 的监控平均值
        avg_correct.append(np.mean(current_epoch_scores['correct']))
        avg_mismatch.append(np.mean(current_epoch_scores['mismatch']))
        avg_temp.append(np.mean(current_epoch_scores['temp']))
        
        # 清空列表供下一个 Epoch 使用
        current_epoch_scores = {'correct': [], 'mismatch': [], 'temp': []}

# ==========================================
# 2. 科研级图表全局设置 (CVPR 风格)
# ==========================================
# 设置全局字体和清晰度 (Mac 使用 Arial，Windows 可以改用 Times New Roman)
plt.rcParams['font.sans-serif'] = ['Arial', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300  # 顶会要求的高分辨率
plt.rcParams['savefig.dpi'] = 300

# 采用 Seaborn 的学术主题
sns.set_theme(style="ticks", context="paper", font_scale=1.5)

# 学术经典配色 (借鉴 Science 调色板)
COLOR_LOSS = "#E64B35"      # 砖红色
COLOR_CORRECT = "#4DBBD5"   # 湖蓝色
COLOR_MISMATCH = "#F39B7F"  # 浅橙色
COLOR_TEMP = "#3C5488"      # 藏青色

# 创建 1x3 的横向画布
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
fig.suptitle('Training Dynamics of Dual-Path Gated Fusion (ATF)', fontsize=18, fontweight='bold', y=1.05)

# ==========================================
# 图 A: Training Loss (收敛曲线)
# ==========================================
ax1 = axes[0]
ax1.plot(epochs, losses, color=COLOR_LOSS, linewidth=2.5, marker='o', markersize=5, label='Train Loss')
ax1.set_title('(a) Average Training Loss', fontsize=16, pad=10)
ax1.set_xlabel('Epoch', fontsize=14)
ax1.set_ylabel('Contrastive Loss', fontsize=14)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='upper right', frameon=True, shadow=True)

# 增加趋势阴影增强科研感
ax1.fill_between(epochs, losses, min(losses)-0.2, color=COLOR_LOSS, alpha=0.1)

# ==========================================
# 图 B: 匹配得分分布 (正确 vs 错误)
# ==========================================
ax2 = axes[1]
ax2.plot(epochs, avg_correct, color=COLOR_CORRECT, linewidth=2.5, marker='s', markersize=5, label='Positive Pair Score')
ax2.plot(epochs, avg_mismatch, color=COLOR_MISMATCH, linewidth=2.5, marker='^', markersize=5, label='Negative Pair Score')

ax2.set_title('(b) Contrastive Similarity Scores', fontsize=16, pad=10)
ax2.set_xlabel('Epoch', fontsize=14)
ax2.set_ylabel('Cosine Similarity', fontsize=14)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='upper left', frameon=True, shadow=True)

# 填充 Correct 和 Mismatch 之间的 Margin 区域 (展示模型的区分能力)
ax2.fill_between(epochs, avg_mismatch, avg_correct, color=COLOR_CORRECT, alpha=0.1)

# ==========================================
# 图 C: 可学习温度参数 (Temperature $\tau$)
# ==========================================
ax3 = axes[2]
ax3.plot(epochs, avg_temp, color=COLOR_TEMP, linewidth=2.5, linestyle='-', marker='D', markersize=5)
ax3.set_title('(c) Learnable Temperature Parameter', fontsize=16, pad=10)
ax3.set_xlabel('Epoch', fontsize=14)
ax3.set_ylabel('Temperature ($\\tau$)', fontsize=14)
ax3.grid(True, linestyle='--', alpha=0.6)

# ==========================================
# 3. 细节打磨与保存
# ==========================================
# 移除所有子图的顶部和右侧边框 (非常重要的学术风格)
for ax in axes:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)

plt.tight_layout()
plt.savefig('ATF_Training_Dynamics.pdf', format='pdf', bbox_inches='tight')  # 保存为矢量图供论文使用
plt.savefig('ATF_Training_Dynamics.png', format='png', bbox_inches='tight')  # 保存为 PNG 供 PPT 使用
plt.show()