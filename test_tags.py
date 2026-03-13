#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证带标签的数据库
"""

from database_v2 import MathDatabase

db = MathDatabase()
db.connect()

cursor = db.conn.cursor()

# 统计题目数量
cursor.execute('SELECT COUNT(*) FROM problems')
total = cursor.fetchone()[0]
print(f'题目总数: {total}')

# 按类型统计
cursor.execute('SELECT type, COUNT(*) FROM problems GROUP BY type')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} 道')

# 显示几个示例题目及其标签
print('\n示例题目:')
cursor.execute('SELECT * FROM problems LIMIT 5')
for row in cursor.fetchall():
    print(f'  {row[1]} 答案: {row[4]}')
    print(f'    标签: {row[6]}')

# 测试标签筛选
print('\n测试筛选 - 需要进位的加法题:')
problems = db.get_problems_by_filters(5, '加法', ['需要进位'])
for p in problems:
    print(f'  {p["question"]} = {p["answer"]}')

print('\n测试筛选 - 需要退位的减法题:')
problems = db.get_problems_by_filters(5, '减法', ['需要退位'])
for p in problems:
    print(f'  {p["question"]} = {p["answer"]}')

db.close()
