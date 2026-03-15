#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题库练习系统 - Web应用
"""

import os
import sys
import shutil
from flask import Flask, render_template, request, jsonify, session
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 配置加载：检查 config.py 是否存在
config_path = os.path.join(os.path.dirname(__file__), 'config.py')
config_sample_path = os.path.join(os.path.dirname(__file__), 'config_sample.py')

if not os.path.exists(config_path):
    shutil.copy(config_sample_path, config_path)
    print('已生成 config.py，请编辑填入 Supabase URL 和 Key 后重新运行')
    sys.exit(1)

from config import SUPABASE_URL, SUPABASE_KEY

if SUPABASE_URL == 'https://your-project.supabase.co' or SUPABASE_KEY == 'your-anon-key':
    print('请先编辑 config.py，填入真实的 Supabase URL 和 Key')
    sys.exit(1)

from database_v3 import MathDatabase

# 数据库实例
db = MathDatabase(SUPABASE_URL, SUPABASE_KEY)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/practice')
def practice():
    """练习页面"""
    return render_template('practice.html')


@app.route('/statistics')
def statistics():
    """统计页面"""
    return render_template('statistics.html')


@app.route('/wrong-book')
def wrong_book():
    """错题本页面"""
    return render_template('wrong_book.html')


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()

    if not username:
        return jsonify({'success': False, 'message': '用户名不能为空'})

    user_id = db.add_user(username)

    session['user_id'] = user_id
    session['username'] = username

    return jsonify({'success': True, 'user_id': user_id, 'username': username})


@app.route('/api/get_problems', methods=['GET'])
def get_problems():
    """获取题目"""
    count = request.args.get('count', 10, type=int)
    problem_type = request.args.get('type', None)
    tags = request.args.getlist('tags[]')  # 获取标签数组

    problems = db.get_problems_by_filters(count, problem_type, tags if tags else None)

    return jsonify({'success': True, 'problems': problems})


@app.route('/api/debug_problems', methods=['GET'])
def debug_problems():
    """Debug: 打印SQL并返回全部符合条件的题目"""
    problem_type = request.args.get('type', None)
    tags = request.args.getlist('tags[]')

    desc, problems = db.debug_problems_by_filters(problem_type, tags if tags else None)

    # 在后台打印查询描述
    print(f'\n[DEBUG] Query: {desc}')
    print(f'[DEBUG] 符合条件的题目数量: {len(problems)}')

    return jsonify({'success': True, 'sql': desc, 'total': len(problems), 'problems': problems})


@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """提交答案"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    data = request.get_json()
    problem_id = data.get('problem_id')
    user_answer = data.get('user_answer')

    if problem_id is None or user_answer is None:
        return jsonify({'success': False, 'message': '参数错误'})

    try:
        user_answer = int(user_answer)
    except ValueError:
        return jsonify({'success': False, 'message': '答案必须是数字'})

    is_correct = db.record_answer(session['user_id'], problem_id, user_answer)

    # 获取正确答案
    problem = db.get_problem_by_id(problem_id)
    correct_answer = problem['answer'] if problem else None

    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': correct_answer
    })


@app.route('/api/get_statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    stats = db.get_user_statistics(session['user_id'])

    # 计算正确率
    if stats['total_answers'] > 0:
        stats['accuracy'] = round(stats['correct_count'] / stats['total_answers'] * 100, 1)
    else:
        stats['accuracy'] = 0

    stats['username'] = session.get('username', '')

    return jsonify({'success': True, 'statistics': stats})


@app.route('/api/logout', methods=['POST'])
def logout():
    """退出登录"""
    session.clear()
    return jsonify({'success': True})


@app.route('/api/get_wrong_problems', methods=['GET'])
def get_wrong_problems():
    """获取错题本"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    wrong_problems = db.get_wrong_problems(session['user_id'])

    return jsonify({'success': True, 'wrong_problems': wrong_problems})


@app.route('/api/get_similar_problems', methods=['POST'])
def get_similar_problems():
    """获取相似题目"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    data = request.get_json()
    tags = data.get('tags')
    count = data.get('count', 10)
    exclude_id = data.get('exclude_id')

    if not tags:
        return jsonify({'success': False, 'message': '参数错误'})

    problems = db.get_similar_problems(tags, count, exclude_id)

    return jsonify({'success': True, 'problems': problems})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
