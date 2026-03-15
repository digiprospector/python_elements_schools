#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：SQLite → Supabase
将本地 math_problems.db 中的题目数据批量写入 Supabase
"""

import argparse
import sqlite3
from supabase import create_client


BATCH_SIZE = 500


def migrate(supabase_url, supabase_key, db_path='math_problems.db'):
    # 连接 SQLite
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 连接 Supabase
    client = create_client(supabase_url, supabase_key)

    # 读取所有题目
    cursor.execute('SELECT question, num1, num2, answer, type, tags FROM problems')
    rows = cursor.fetchall()
    print(f'从 SQLite 读取到 {len(rows)} 道题目')

    # 批量写入 Supabase
    problems = [dict(row) for row in rows]
    total = 0
    for i in range(0, len(problems), BATCH_SIZE):
        batch = problems[i:i + BATCH_SIZE]
        client.table('problems').insert(batch).execute()
        total += len(batch)
        print(f'已写入 {total}/{len(problems)}')

    print(f'迁移完成！共写入 {total} 道题目')
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='迁移 SQLite 数据到 Supabase')
    parser.add_argument('--supabase-url', required=True, help='Supabase 项目 URL')
    parser.add_argument('--supabase-key', required=True, help='Supabase anon key')
    parser.add_argument('--db', default='math_problems.db', help='SQLite 数据库路径')
    args = parser.parse_args()

    migrate(args.supabase_url, args.supabase_key, args.db)
