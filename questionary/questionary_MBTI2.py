import questionary

# 配置参数
DIMENSION_COUNT = 4  # MBTI维度数
MAX_SCORE = 5        # 最大标准化得分
GRID_SIZE = 13       # 坐标系大小（奇数确保中心对称）

# MBTI维度说明（标准四维）
DIMENSIONS = [
    ("外向(E)", "内向(I)"),  # 上
    ("实感(S)", "直觉(N)"),  # 右
    ("思考(T)", "情感(F)"),  # 左
    ("判断(J)", "感知(P)")   # 下
]

# 测试题目库
QUESTIONS = [
    {"question": "你更倾向于", "options": ["从与他人相处中获得能量", "从独处中获得能量"], "dimension": 0},
    {"question": "参加聚会时，你通常", "options": ["认识新朋友并活跃到最后", "与熟人交流或提前离开"], "dimension": 0},
    {"question": "你更容易注意到", "options": ["具体的现实细节", "事物的潜在可能性"], "dimension": 1},
    {"question": "学习新事物时，你倾向于", "options": ["按步骤循序渐进", "先看整体框架"], "dimension": 1},
    {"question": "做决定时，你更注重", "options": ["客观逻辑", "人情感受"], "dimension": 2},
    {"question": "面对他人问题，你通常", "options": ["分析问题提供解决方案", "表达理解提供情感支持"], "dimension": 2},
    {"question": "你更喜欢", "options": ["有计划有条理的生活", "灵活开放的选择"], "dimension": 3},
    {"question": "处理任务时，你倾向于", "options": ["提前规划按时完成", "灵活应对最后冲刺"], "dimension": 3},
]

def conduct_test():
    """进行MBTI测试并返回维度得分"""
    scores = [0] * 4  # [E/I, S/N, T/F, J/P]
    
    for q in QUESTIONS:
        answer = questionary.select(
            q["question"],
            choices=q["options"],
            use_shortcuts=True
        ).ask()
        
        scores[q["dimension"]] += 1 if answer == q["options"][0] else -1
            
    return scores

def determine_type(scores):
    """生成标准MBTI四字母类型"""
    return "".join(
        DIMENSIONS[i][0].split("(")[1][0] if score >=0 
        else DIMENSIONS[i][1].split("(")[1][0]
        for i, score in enumerate(scores)
    )

def plot_terminal_radar(type_code, scores):
    """终端四象限雷达图"""
    max_score = len(QUESTIONS) // len(DIMENSIONS)
    normalized = [min(s/max_score*MAX_SCORE, MAX_SCORE) for s in scores]
    
    # 构建标准四象限坐标系
    grid = [[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    center = GRID_SIZE // 2
    
    # 绘制坐标轴
    for i in range(GRID_SIZE):
        # 水平轴
        grid[center][i] = "─"
        # 垂直轴
        grid[i][center] = "│"
    
    # 中心符号
    grid[center][center] = "◆"
    
    # 维度向量配置
    dimensions = [
        {"dx": 0,  "dy": -1, "pos": (0, center),      "label": "E"},  # 上
        {"dx": 1,  "dy": 0,  "pos": (center, GRID_SIZE-1), "label": "S"},  # 右
        {"dx": -1, "dy": 0,  "pos": (center, 0),      "label": "T"},  # 左
        {"dx": 0,  "dy": 1,  "pos": (GRID_SIZE-1, center), "label": "J"},  # 下
    ]

    # 绘制得分轨迹
    for dim in dimensions:
        dx, dy = dim["dx"], dim["dy"]
        score = normalized[dimensions.index(dim)]
        steps = min(int(abs(score)), MAX_SCORE)
        
        # 绘制实际倾向圆点
        for step in range(1, steps + 1):
            x = center + dx * step
            y = center + dy * step
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                grid[y][x] = "\033[92m●\033[0m"
        
        # 添加维度标签
        ly, lx = dim["pos"]
        label = dim["label"][0] if score >=0 else dim["label"][1]
        grid[ly][lx] = f"\033[94m{label}\033[0m"

    # 打印四象限图
    print("\nMBTI 维度分布图（0-5级）：")
    for row in grid:
        print(" ".join(row))
    
    # 类型解析
    print(f"\n{type_code} 类型解析：")
    for i, score in enumerate(normalized):
        actual_steps = min(int(abs(score)), MAX_SCORE)
        print(f"{DIMENSIONS[i][0].split('(')[0]:<4} → "
            f"{'●'*actual_steps}{'○'*(MAX_SCORE-actual_steps)} "
            f"({actual_steps}/{MAX_SCORE}级)")
        

    # 图例说明
    print("\n图例说明：")
    print("◆ 中心基准点")
    print("● 正向倾向（E/S/T/J） ○ 反向倾向（I/N/F/P）")
    print("E: 外向 | I: 内向")
    print("S: 实感 | N: 直觉")
    print("T: 思考 | F: 情感")
    print("J: 判断 | P: 感知")

def main():
    print("欢迎参加MBTI人格测试！请根据直觉回答以下问题：\n")
    scores = conduct_test()
    mbti_type = determine_type(scores)
    
    print(f"\n你的MBTI人格类型是：{mbti_type}")
    plot_terminal_radar(mbti_type, scores)

if __name__ == "__main__":
    main()