# Forked from https://blog.csdn.net/2301_79376014/article/details/142071980
import random as rd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'SimHei'  # 或者 'Microsoft YaHei'
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'

#%%
#定义实验基本参量
#a:平行线距离,l:针长,n:投掷次数
a=1
l=0.5
n=100000
k=100
#%%
#进行实验,x:针与最近平行线之间的距离，φ：针角度,m:相交次数,PI:最终计算圆周率
#绘图项:x_history,phi_history,joint_list
m=0
x_history=[]
phi_history=[]
joint_list=[]


for i in range(n):
    x=rd.uniform(0,a/2)
    phi=rd.uniform(0,math.pi)
    x_history.append(x)
    phi_history.append(phi)
#判断相交：l*sin(phi)/2>x
    if l*math.sin(phi)/2>=x:
        m+=1
        joint_list.append(1)
    else:
        joint_list.append(0)

PI=2*l*n/(a*m)

#输出结果
print(f'模拟所得圆周率:{PI}')

#绘制投针phi-x分布图
plt.scatter(phi_history, x_history, c=joint_list, cmap='bwr', alpha=0.5)
plt.colorbar(label='是否相交')
plt.xlabel('针角度')
plt.ylabel('针中点与最近平行线距离')
plt.title('布丰模拟实验分布图')
plt.xticks([0, math.pi/2, math.pi], ['0', 'π/2', 'π'])  # 显示π符号
plt.yticks([0, a/2], ['0', 'a/2'])  # 纵轴标记为0和a/2
plt.show()

