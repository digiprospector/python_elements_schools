#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题库生成器 - 带详细分类标签
"""

import json
from datetime import datetime


def analyze_addition(num1, num2, answer):
    """分析加法题目的属性"""
    tags = []

    # 数字位数
    if num1 <= 9:
        tags.append('加数1是一位数')
    else:
        tags.append('加数1是两位数')

    if num2 <= 9:
        tags.append('加数2是一位数')
    else:
        tags.append('加数2是两位数')

    # 是否进位
    ones_sum = (num1 % 10) + (num2 % 10)
    if ones_sum >= 10:
        tags.append('需要进位')
    else:
        tags.append('不进位')

    # 结果范围
    if answer > 99:
        tags.append('结果大于99')
    elif answer > 50:
        tags.append('结果大于50')
    elif answer <= 20:
        tags.append('结果小于等于20')

    return tags


def analyze_subtraction(num1, num2, answer):
    """分析减法题目的属性"""
    tags = []

    # 数字位数
    if num1 <= 9:
        tags.append('被减数是一位数')
    else:
        tags.append('被减数是两位数')

    if num2 <= 9:
        tags.append('减数是一位数')
    else:
        tags.append('减数是两位数')

    # 是否退位
    if (num1 % 10) < (num2 % 10):
        tags.append('需要退位')
    else:
        tags.append('不退位')

    # 被减数范围
    if num1 > 50:
        tags.append('被减数大于50')

    # 结果范围
    if answer == 0:
        tags.append('结果为0')
    elif answer < 10:
        tags.append('结果小于10')
    elif answer >= 50:
        tags.append('结果大于等于50')

    return tags


def generate_all_problems_with_tags():
    """生成所有题目并添加标签"""
    problems = []

    # 生成所有数字：一位数(1-9)和两位数(10-99)
    numbers = list(range(1, 10)) + list(range(10, 100))

    print('正在生成加法题目...')
    # 加法
    for num1 in numbers:
        for num2 in numbers:
            answer = num1 + num2
            tags = analyze_addition(num1, num2, answer)
            problems.append({
                'question': f'{num1} + {num2} = ?',
                'num1': num1,
                'num2': num2,
                'answer': answer,
                'type': '加法',
                'tags': tags
            })

    print('正在生成减法题目...')
    # 减法
    for num1 in numbers:
        for num2 in numbers:
            if num1 >= num2:
                answer = num1 - num2
                tags = analyze_subtraction(num1, num2, answer)
                problems.append({
                    'question': f'{num1} - {num2} = ?',
                    'num1': num1,
                    'num2': num2,
                    'answer': answer,
                    'type': '减法',
                    'tags': tags
                })

    return problems


def save_to_json(problems, filename='math_problems_tagged.json'):
    """保存为JSON文件"""
    data = {
        'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_count': len(problems),
        'problems': problems
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print('开始生成带标签的完整题库...')

    # 生成所有题目
    problems = generate_all_problems_with_tags()

    # 保存文件
    print('正在保存文件...')
    save_to_json(problems, 'math_problems_tagged.json')

    # 统计
    addition_count = sum(1 for p in problems if p['type'] == '加法')
    subtraction_count = sum(1 for p in problems if p['type'] == '减法')

    print(f'\n成功生成完整题库！')
    print(f'  - 加法题: {addition_count} 道')
    print(f'  - 减法题: {subtraction_count} 道')
    print(f'  - 总计: {len(problems)} 道')
    print(f'\n文件已保存: math_problems_tagged.json')


if __name__ == '__main__':
    main()
