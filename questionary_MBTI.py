import questionary
import matplotlib.pyplot as plt
import numpy as np

# MBTI维度说明
DIMENSIONS = [
    ("外向(E)", "内向(I)"),
    ("实感(S)", "直觉(N)"),
    ("思考(T)", "情感(F)"),
    ("判断(J)", "感知(P)")
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
    scores = [0] * 4  # 每个维度的得分（E/S/T/J倾向为正）
    
    for q in QUESTIONS:
        answer = questionary.select(
            q["question"],
            choices=q["options"],
            use_shortcuts=True
        ).ask()
        
        # 每个问题第一个选项对应正维度加分
        if answer == q["options"][0]:
            scores[q["dimension"]] += 1
        else:
            scores[q["dimension"]] -= 1
            
    return scores

def determine_type(scores):
    """根据得分确定MBTI类型"""
    type_code = ""
    for i, score in enumerate(scores):
        type_code += DIMENSIONS[i][0][0] if score >= 0 else DIMENSIONS[i][1][0]
    return type_code

def main():
    print("欢迎参加MBTI人格测试！请根据直觉回答以下问题：\n")
    scores = conduct_test()
    mbti_type = determine_type(scores)
    print(f"\n你的MBTI人格类型是：{mbti_type}")

if __name__ == "__main__":
    main()