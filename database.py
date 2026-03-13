#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题库数据库管理
"""

import sqlite3
import json
from datetime import datetime


class MathDatabase:
    def __init__(self, db_path='math_problems.db'):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()

        # 题目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer INTEGER NOT NULL,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 答题记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_id INTEGER NOT NULL,
                user_answer INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (problem_id) REFERENCES problems(id)
            )
        ''')

        # 创建索引以提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_answers_user_id
            ON user_answers(user_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_answers_problem_id
            ON user_answers(problem_id)
        ''')

        self.conn.commit()
        print('数据库表创建成功')

    def import_problems_from_json(self, json_file):
        """从JSON文件导入题目"""
        cursor = self.conn.cursor()

        # 先清空题目表
        cursor.execute('DELETE FROM problems')

        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 批量插入题目
        problems = data['problems']
        for problem in problems:
            cursor.execute('''
                INSERT INTO problems (question, answer, type)
                VALUES (?, ?, ?)
            ''', (problem['question'], problem['answer'], problem['type']))

        self.conn.commit()
        print(f'成功导入 {len(problems)} 道题目')

    def add_user(self, username):
        """添加用户"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f'用户 {username} 已存在')
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            return cursor.fetchone()[0]

    def record_answer(self, user_id, problem_id, user_answer):
        """记录用户答题"""
        cursor = self.conn.cursor()

        # 获取正确答案
        cursor.execute('SELECT answer FROM problems WHERE id = ?', (problem_id,))
        result = cursor.fetchone()
        if not result:
            print(f'题目 {problem_id} 不存在')
            return False

        correct_answer = result[0]
        is_correct = (user_answer == correct_answer)

        # 记录答题
        cursor.execute('''
            INSERT INTO user_answers (user_id, problem_id, user_answer, is_correct)
            VALUES (?, ?, ?, ?)
        ''', (user_id, problem_id, user_answer, is_correct))

        self.conn.commit()
        return is_correct

    def get_user_statistics(self, user_id):
        """获取用户答题统计"""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_answers,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong_count
            FROM user_answers
            WHERE user_id = ?
        ''', (user_id,))

        return dict(cursor.fetchone())

    def get_problem_statistics(self, problem_id):
        """获取题目统计（被答对和答错的次数）"""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_attempts,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong_count
            FROM user_answers
            WHERE problem_id = ?
        ''', (problem_id,))

        return dict(cursor.fetchone())

    def get_random_problems(self, count=10, problem_type=None):
        """随机获取题目"""
        cursor = self.conn.cursor()

        if problem_type:
            cursor.execute('''
                SELECT * FROM problems
                WHERE type = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (problem_type, count))
        else:
            cursor.execute('''
                SELECT * FROM problems
                ORDER BY RANDOM()
                LIMIT ?
            ''', (count,))

        return [dict(row) for row in cursor.fetchall()]


def main():
    """初始化数据库并导入题目"""
    db = MathDatabase()
    db.connect()

    print('创建数据库表...')
    db.create_tables()

    print('\n导入题目数据...')
    db.import_problems_from_json('math_problems_complete.json')

    print('\n数据库初始化完成！')
    print(f'数据库文件: {db.db_path}')

    db.close()


if __name__ == '__main__':
    main()
