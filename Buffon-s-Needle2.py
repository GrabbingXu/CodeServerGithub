# Improved from Buffon-s-Needle.py

import numpy as np
import matplotlib.pyplot as plt
import math

# 针的长度
l = 0.520
# 平行线宽度
a = 1.314
# 试验次数n
n = 10000
# 相交次数
count = 0
# 在0~a/2之间产生n个随机数
x = np.random.rand(n) * a / 2
phi = np.random.rand(n) * math.pi
# 储存不同颜色的点
red_phi, red_x = [], []
green_phi, green_x = [], []

def test(times):
    global count
    for i in range(0, times):
        if x[i] <= l / 2 * math.sin(phi[i]):
            count += 1
            red_phi.append(phi[i])
            red_x.append(x[i])
        else:
            green_phi.append(phi[i])
            green_x.append(x[i])
    
    plt.scatter(red_phi, red_x, c='r', marker='.', label='Intersected')
    plt.scatter(green_phi, green_x, c='g', marker='.', label='Not Intersected')
    plt.xlabel('Phi (radians)')
    plt.ylabel('X Position')
    plt.legend()

test(n)
p = count / n
mPi = (2 * l) / (a * p)
print("蒙特卡洛方法得到Pi为：",mPi)
plt.savefig("BuffonPlot2.png", dpi=150, bbox_inches='tight')
print("图像已保存至 BuffonPlot2.png")