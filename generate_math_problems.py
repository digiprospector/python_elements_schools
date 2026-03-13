#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题库生成器 - 一位数和两位数加减法
"""

import random
import json
from datetime import datetime


def generate_all_addition_problems():
    """生成所有可能的加法题目"""
    problems = []
    # 生成所有数字：一位数(1-9)和两位数(10-99)
    numbers = list(range(1, 10)) + list(range(10, 100))

    for num1 in numbers:
        for num2 in numbers:
            answer = num1 + num2
            problems.append({
                'question': f'{num1} + {num2} = ?',
                'answer': answer,
                'type': '加法'
            })
    return problems


def generate_all_subtraction_problems():
    """生成所有可能的减法题目（确保结果为非负数）"""
    problems = []
    # 生成所有数字：一位数(1-9)和两位数(10-99)
    numbers = list(range(1, 10)) + list(range(10, 100))

    for num1 in numbers:
        for num2 in numbers:
            # 只保留被减数大于等于减数的情况
            if num1 >= num2:
                answer = num1 - num2
                problems.append({
                    'question': f'{num1} - {num2} = ?',
                    'answer': answer,
                    'type': '减法'
                })
    return problems


def save_to_txt(problems, filename='math_problems.txt'):
    """保存为文本文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'数学题库 - 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write('=' * 50 + '\n\n')

        for i, problem in enumerate(problems, 1):
            f.write(f'{i}. {problem["question"]}\n')

        f.write('\n' + '=' * 50 + '\n')
        f.write('答案:\n')
        f.write('=' * 50 + '\n\n')

        for i, problem in enumerate(problems, 1):
            f.write(f'{i}. {problem["question"]} {problem["answer"]}\n')


def save_to_json(problems, filename='math_problems.json'):
    """保存为JSON文件"""
    data = {
        'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_count': len(problems),
        'problems': problems
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print('开始生成完整题库...')

    # 生成所有题目
    print('正在生成加法题目...')
    addition_problems = generate_all_addition_problems()

    print('正在生成减法题目...')
    subtraction_problems = generate_all_subtraction_problems()

    # 合并题目（不打乱顺序，保持分类）
    all_problems = addition_problems + subtraction_problems

    # 保存文件
    print('正在保存文件...')
    save_to_txt(all_problems, 'math_problems_complete.txt')
    save_to_json(all_problems, 'math_problems_complete.json')

    print(f'\n成功生成完整题库！')
    print(f'  - 加法题: {len(addition_problems)} 道')
    print(f'  - 减法题: {len(subtraction_problems)} 道')
    print(f'  - 总计: {len(all_problems)} 道')
    print(f'\n文件已保存:')
    print(f'  - math_problems_complete.txt (文本格式)')
    print(f'  - math_problems_complete.json (JSON格式)')


if __name__ == '__main__':
    main()
