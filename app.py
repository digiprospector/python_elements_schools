#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题库练习系统 - Web应用
"""

from flask import Flask, render_template, request, jsonify, session
from database import MathDatabase
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 数据库实例
db = MathDatabase()


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


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()

    if not username:
        return jsonify({'success': False, 'message': '用户名不能为空'})

    db.connect()
    user_id = db.add_user(username)
    db.close()

    session['user_id'] = user_id
    session['username'] = username

    return jsonify({'success': True, 'user_id': user_id, 'username': username})


@app.route('/api/get_problems', methods=['GET'])
def get_problems():
    """获取题目"""
    count = request.args.get('count', 10, type=int)
    problem_type = request.args.get('type', None)

    db.connect()
    problems = db.get_random_problems(count, problem_type)
    db.close()

    return jsonify({'success': True, 'problems': problems})


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

    db.connect()
    is_correct = db.record_answer(session['user_id'], problem_id, user_answer)

    # 获取正确答案
    cursor = db.conn.cursor()
    cursor.execute('SELECT answer FROM problems WHERE id = ?', (problem_id,))
    correct_answer = cursor.fetchone()[0]

    db.close()

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

    db.connect()
    stats = db.get_user_statistics(session['user_id'])
    db.close()

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
