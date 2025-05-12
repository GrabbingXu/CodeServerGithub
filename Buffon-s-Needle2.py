# Forked from https://blog.csdn.net/2301_79376014/article/details/142071980
import random as rd
import math
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

# ====== 字体配置 ======
# 指定Noto Sans CJK SC字体文件路径
font_path = "/usr/share/fonts/google-noto-sans-cjk-fonts/NotoSansCJK-Regular.ttc"

# 创建字体属性对象
cn_font = FontProperties(fname=font_path)

# 全局字体设置
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# ====== 实验参数 ======
a = 1        # 平行线间距
l = 0.5      # 针的长度
n = 100000   # 投掷次数

# ====== 向量化计算优化 ======
# 使用numpy替代循环（提速约100倍）
x = np.random.uniform(0, a/2, n)
phi = np.random.uniform(0, math.pi, n)
crosses = (l * np.sin(phi) / 2) >= x
m = np.sum(crosses)

# ====== 结果计算 ======
PI = (2 * l * n) / (a * m)
print(f'模拟所得圆周率: {PI}')

# ====== 可视化配置 ======
plt.figure(figsize=(10, 6), dpi=100)

# 绘制散点图（采样5000个点）
sample_idx = np.random.choice(n, 5000, replace=False)
plt.scatter(phi[sample_idx], x[sample_idx], 
            c=crosses[sample_idx], 
            cmap='bwr', 
            alpha=0.5,
            s=10)

# 坐标轴和标签设置
plt.xticks([0, math.pi/2, math.pi], 
            ['0', 'π/2', 'π'],
            fontproperties=cn_font)
plt.yticks([0, a/4, a/2], 
            ['0', 'a/4', 'a/2'],
            fontproperties=cn_font)

plt.xlabel('针角度', fontproperties=cn_font, fontsize=12)
plt.ylabel('中点距离', fontproperties=cn_font, fontsize=12)
plt.title('布丰投针实验分布图', fontproperties=cn_font, fontsize=14)

# 颜色条设置
cbar = plt.colorbar()
cbar.set_label('相交状态', 
                fontproperties=cn_font, 
                rotation=270, 
                labelpad=15)

# 添加理论曲线
phi_line = np.linspace(0, math.pi, 200)
y_line = (l/2) * np.sin(phi_line)
plt.plot(phi_line, y_line, 
        '--', 
        color='green', 
        lw=2, 
        label='理论边界')

plt.legend(prop=cn_font)  # 图例字体设置

# 保存图像
plt.savefig("BuffonPlot2.png", 
            dpi=150, 
            bbox_inches='tight',
            facecolor='white')
print("图像已保存至 BuffonPlot2.png")
