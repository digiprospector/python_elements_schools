#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库内容
"""

from database import MathDatabase

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

# 显示几个示例题目
print('\n示例题目:')
cursor.execute('SELECT * FROM problems LIMIT 5')
for row in cursor.fetchall():
    print(f'  ID {row[0]}: {row[1]} 答案: {row[2]}')

db.close()
