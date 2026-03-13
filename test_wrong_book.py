#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试错题本功能
"""

from database_v3 import MathDatabase

db = MathDatabase()
db.connect()

# 创建测试用户
user_id = db.add_user('测试用户')
print(f'创建用户: 测试用户 (ID: {user_id})')

# 获取一些题目
problems = db.get_problems_by_filters(10, '加法', ['需要进位'])
print(f'\n获取了 {len(problems)} 道需要进位的加法题')

# 模拟答错几道题
print('\n模拟答错题目:')
for i in range(3):
    problem = problems[i]
    wrong_answer = problem['answer'] + 1  # 故意答错
    db.record_answer(user_id, problem['id'], wrong_answer)
    print(f'  {problem["question"]} 答案: {problem["answer"]}, 用户答: {wrong_answer} (错误)')

# 查看错题本
print('\n错题本:')
wrong_problems = db.get_wrong_problems(user_id)
for wp in wrong_problems:
    print(f'  {wp["question"]} 答案: {wp["answer"]}')
    print(f'    错误次数: {wp["wrong_count"]}, 连续正确: {wp["correct_streak"]}/3')
    print(f'    标签: {wp["tags"]}')

# 获取相似题目
if wrong_problems:
    first_wrong = wrong_problems[0]
    print(f'\n获取与 "{first_wrong["question"]}" 相似的题目:')
    similar = db.get_similar_problems(first_wrong['tags'], 5, first_wrong['id'])
    for p in similar:
        print(f'  {p["question"]} = {p["answer"]}')

    # 模拟做对相似题目
    print('\n模拟连续做对相似题目:')
    for i in range(3):
        if i < len(similar):
            p = similar[i]
            db.record_answer(user_id, p['id'], p['answer'])
            print(f'  {p["question"]} = {p["answer"]} (正确)')

    # 再次查看错题本
    print('\n做对3题后的错题本:')
    wrong_problems = db.get_wrong_problems(user_id)
    if wrong_problems:
        for wp in wrong_problems:
            print(f'  {wp["question"]} 连续正确: {wp["correct_streak"]}/3')
    else:
        print('  错题本已清空！')

db.close()
