#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题库练习系统 - 示例程序
"""

from database import MathDatabase


def practice_session(username, problem_count=10):
    """练习会话"""
    db = MathDatabase()
    db.connect()

    # 添加或获取用户
    user_id = db.add_user(username)
    print(f'\n欢迎, {username}!')

    # 获取随机题目
    problems = db.get_random_problems(problem_count)

    correct_count = 0
    wrong_count = 0

    print(f'\n开始练习，共 {len(problems)} 道题目\n')
    print('=' * 50)

    for i, problem in enumerate(problems, 1):
        print(f'\n第 {i} 题: {problem["question"]}')
        try:
            user_answer = int(input('你的答案: '))

            # 记录答题
            is_correct = db.record_answer(user_id, problem['id'], user_answer)

            if is_correct:
                print('✓ 正确!')
                correct_count += 1
            else:
                print(f'✗ 错误! 正确答案是: {problem["answer"]}')
                wrong_count += 1

        except ValueError:
            print('✗ 输入无效，跳过此题')
            wrong_count += 1
        except KeyboardInterrupt:
            print('\n\n练习中断')
            break

    # 显示本次练习统计
    print('\n' + '=' * 50)
    print(f'\n本次练习完成!')
    print(f'  正确: {correct_count} 题')
    print(f'  错误: {wrong_count} 题')
    if correct_count + wrong_count > 0:
        accuracy = correct_count / (correct_count + wrong_count) * 100
        print(f'  正确率: {accuracy:.1f}%')

    # 显示总体统计
    stats = db.get_user_statistics(user_id)
    print(f'\n总体统计:')
    print(f'  总答题数: {stats["total_answers"]} 题')
    print(f'  总正确数: {stats["correct_count"]} 题')
    print(f'  总错误数: {stats["wrong_count"]} 题')
    if stats["total_answers"] > 0:
        total_accuracy = stats["correct_count"] / stats["total_answers"] * 100
        print(f'  总正确率: {total_accuracy:.1f}%')

    db.close()


def show_statistics(username):
    """显示用户统计信息"""
    db = MathDatabase()
    db.connect()

    # 获取用户ID
    cursor = db.conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()

    if not result:
        print(f'用户 {username} 不存在')
        db.close()
        return

    user_id = result[0]

    # 获取统计信息
    stats = db.get_user_statistics(user_id)

    print(f'\n{username} 的答题统计:')
    print('=' * 50)
    print(f'总答题数: {stats["total_answers"]} 题')
    print(f'正确数: {stats["correct_count"]} 题')
    print(f'错误数: {stats["wrong_count"]} 题')

    if stats["total_answers"] > 0:
        accuracy = stats["correct_count"] / stats["total_answers"] * 100
        print(f'正确率: {accuracy:.1f}%')

    db.close()


def main():
    """主程序"""
    print('数学题库练习系统')
    print('=' * 50)
    print('1. 开始练习')
    print('2. 查看统计')
    print('3. 退出')

    choice = input('\n请选择 (1-3): ')

    if choice == '1':
        username = input('请输入用户名: ')
        try:
            count = int(input('练习题目数量 (默认10): ') or '10')
        except ValueError:
            count = 10
        practice_session(username, count)

    elif choice == '2':
        username = input('请输入用户名: ')
        show_statistics(username)

    elif choice == '3':
        print('再见!')

    else:
        print('无效选择')


if __name__ == '__main__':
    main()
