#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理 - 支持标签筛选和错题本
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
                num1 INTEGER NOT NULL,
                num2 INTEGER NOT NULL,
                answer INTEGER NOT NULL,
                type TEXT NOT NULL,
                tags TEXT NOT NULL,
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

        # 错题本表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wrong_problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_id INTEGER NOT NULL,
                tags TEXT NOT NULL,
                wrong_count INTEGER DEFAULT 1,
                correct_streak INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (problem_id) REFERENCES problems(id),
                UNIQUE(user_id, problem_id)
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_answers_user_id
            ON user_answers(user_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_answers_problem_id
            ON user_answers(problem_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_problems_type
            ON problems(type)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_wrong_problems_user_id
            ON wrong_problems(user_id)
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
            tags_str = ','.join(problem['tags'])
            cursor.execute('''
                INSERT INTO problems (question, num1, num2, answer, type, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (problem['question'], problem['num1'], problem['num2'],
                  problem['answer'], problem['type'], tags_str))

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
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            return cursor.fetchone()[0]

    def record_answer(self, user_id, problem_id, user_answer):
        """记录用户答题"""
        cursor = self.conn.cursor()

        # 获取题目信息
        cursor.execute('SELECT answer, tags FROM problems WHERE id = ?', (problem_id,))
        result = cursor.fetchone()
        if not result:
            return False

        correct_answer = result[0]
        tags = result[1]
        is_correct = (user_answer == correct_answer)

        # 记录答题
        cursor.execute('''
            INSERT INTO user_answers (user_id, problem_id, user_answer, is_correct)
            VALUES (?, ?, ?, ?)
        ''', (user_id, problem_id, user_answer, is_correct))

        # 处理错题本
        if not is_correct:
            # 答错了，添加到错题本或更新错误次数
            cursor.execute('''
                INSERT INTO wrong_problems (user_id, problem_id, tags, wrong_count, correct_streak)
                VALUES (?, ?, ?, 1, 0)
                ON CONFLICT(user_id, problem_id)
                DO UPDATE SET
                    wrong_count = wrong_count + 1,
                    correct_streak = 0,
                    updated_at = CURRENT_TIMESTAMP
            ''', (user_id, problem_id, tags))
        else:
            # 答对了，检查是否是错题本中的同类型题目
            self._update_correct_streak(user_id, tags)

        self.conn.commit()
        return is_correct

    def _update_correct_streak(self, user_id, tags):
        """更新连续正确次数"""
        cursor = self.conn.cursor()

        # 找出所有包含相同标签的错题
        cursor.execute('''
            SELECT id, tags, correct_streak FROM wrong_problems
            WHERE user_id = ?
        ''', (user_id,))

        wrong_problems = cursor.fetchall()
        tags_list = tags.split(',')

        for wp in wrong_problems:
            wp_tags = wp[1].split(',')
            # 如果有至少2个相同标签，认为是同类型题目
            common_tags = set(tags_list) & set(wp_tags)
            if len(common_tags) >= 2:
                new_streak = wp[2] + 1
                if new_streak >= 3:
                    # 连续做对3次，从错题本删除
                    cursor.execute('DELETE FROM wrong_problems WHERE id = ?', (wp[0],))
                else:
                    # 更新连续正确次数
                    cursor.execute('''
                        UPDATE wrong_problems
                        SET correct_streak = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (new_streak, wp[0]))

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

    def get_problems_by_filters(self, count=10, problem_type=None, required_tags=None):
        """根据筛选条件获取题目"""
        cursor = self.conn.cursor()

        query = 'SELECT * FROM problems WHERE 1=1'
        params = []

        if problem_type:
            query += ' AND type = ?'
            params.append(problem_type)

        if required_tags:
            for tag in required_tags:
                query += ' AND tags LIKE ?'
                params.append(f'%{tag}%')

        query += ' ORDER BY RANDOM() LIMIT ?'
        params.append(count)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_wrong_problems(self, user_id):
        """获取用户的错题本"""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT
                wp.id as wrong_id,
                wp.wrong_count,
                wp.correct_streak,
                wp.created_at,
                wp.updated_at,
                p.*
            FROM wrong_problems wp
            JOIN problems p ON wp.problem_id = p.id
            WHERE wp.user_id = ?
            ORDER BY wp.updated_at DESC
        ''', (user_id,))

        return [dict(row) for row in cursor.fetchall()]

    def get_similar_problems(self, tags, count=10, exclude_id=None):
        """根据标签获取相似题目"""
        cursor = self.conn.cursor()

        tags_list = tags.split(',')

        # 构建查询，找出至少包含2个相同标签的题目
        query = 'SELECT * FROM problems WHERE 1=1'
        params = []

        if exclude_id:
            query += ' AND id != ?'
            params.append(exclude_id)

        # 至少匹配2个标签
        tag_conditions = []
        for i in range(len(tags_list)):
            for j in range(i+1, len(tags_list)):
                tag_conditions.append(f"(tags LIKE ? AND tags LIKE ?)")
                params.extend([f'%{tags_list[i]}%', f'%{tags_list[j]}%'])

        if tag_conditions:
            query += ' AND (' + ' OR '.join(tag_conditions) + ')'

        query += ' ORDER BY RANDOM() LIMIT ?'
        params.append(count)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def main():
    """初始化数据库并导入题目"""
    db = MathDatabase()
    db.connect()

    print('创建数据库表...')
    db.create_tables()

    print('\n导入题目数据...')
    db.import_problems_from_json('math_problems_tagged.json')

    print('\n数据库初始化完成！')
    print(f'数据库文件: {db.db_path}')

    db.close()


if __name__ == '__main__':
    main()
