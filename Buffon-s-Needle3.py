import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import math

# 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC']  # 谷歌思源黑体

# 实验参数设置
a = 1        # 平行线间距
l = 0.5      # 针的长度
n = 10**6    # 投掷次数
sample_size = 5000  # 绘图采样量

# ========== 向量化计算 ==========
# 生成所有随机数（一次性生成）
x = np.random.uniform(0, a/2, n)          # 针中点距离
phi = np.random.uniform(0, math.pi, n)    # 针角度

# 判断相交（向量化操作）
crosses = (l * np.sin(phi) / 2) >= x
m = np.sum(crosses)

# 计算圆周率
pi_estimate = (2 * l * n) / (a * m)
print(f"估算的π值: {pi_estimate:.6f}")
print(f"真实π值: {math.pi:.6f}")
print(f"绝对误差: {abs(pi_estimate - math.pi):.6f}")

# ========== 可视化 ==========
# 创建画布
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# 随机采样部分点用于绘图
sample_idx = np.random.choice(n, size=sample_size, replace=False)
phi_sample = phi[sample_idx]
x_sample = x[sample_idx]
crosses_sample = crosses[sample_idx]

# 绘制散点图
scatter = ax.scatter(
    phi_sample,
    x_sample,
    c=crosses_sample,
    cmap='bwr',
    alpha=0.6,
    s=10,
    label='实验点 (红=相交)'
)

# 添加理论概率曲线
phi_line = np.linspace(0, math.pi, 200)
y_line = (l/2) * np.sin(phi_line)
ax.plot(
    phi_line,
    y_line,
    color='green',
    linestyle='--',
    linewidth=2,
    label=r'理论边界 $y=(l/2)\sin\phi$'
)

# 美化图形
ax.set_xlabel('针角度 φ (弧度)', fontsize=12)
ax.set_ylabel('针中点距离 y', fontsize=12)
ax.set_title(f'布丰投针实验 (n={n:,d})', fontsize=14)
ax.set_xticks([0, math.pi/2, math.pi])
ax.set_xticklabels(['0', 'π/2', 'π'])
ax.set_yticks([0, a/4, a/2])
ax.set_yticklabels(['0', 'a/4', 'a/2'])
ax.grid(alpha=0.2)
ax.legend()

# 添加颜色条
cbar = plt.colorbar(scatter)
cbar.set_label('相交状态', rotation=270, labelpad=15)

plt.tight_layout()
plt.show()