# 数学题库练习系统

一个用于小学生练习一位数和两位数加减法的系统。

## 功能特点

- 完整的题库：包含所有可能的一位数和两位数加减法组合（14,751道题）
- 用户管理：支持多用户使用
- 答题记录：自动记录每次答题的正确与错误
- 统计分析：查看个人答题统计和正确率

## 文件说明

- `generate_math_problems.py` - 题库生成器
- `database.py` - 数据库管理模块
- `practice.py` - 练习系统主程序
- `math_problems.db` - SQLite数据库文件
- `math_problems_complete.json` - 完整题库JSON文件
- `math_problems_complete.txt` - 完整题库文本文件

## 数据库结构

### problems 表（题目表）
- `id` - 题目ID
- `question` - 题目内容
- `answer` - 正确答案
- `type` - 题目类型（加法/减法）
- `created_at` - 创建时间

### users 表（用户表）
- `id` - 用户ID
- `username` - 用户名
- `created_at` - 创建时间

### user_answers 表（答题记录表）
- `id` - 记录ID
- `user_id` - 用户ID
- `problem_id` - 题目ID
- `user_answer` - 用户答案
- `is_correct` - 是否正确
- `answered_at` - 答题时间

## 使用方法

### 1. 初始化数据库

```bash
python database.py
```

这将创建数据库并导入所有题目。

### 2. 开始练习

```bash
python practice.py
```

按照提示选择功能：
- 选择 1：开始练习
- 选择 2：查看统计
- 选择 3：退出

### 3. 使用数据库API

```python
from database import MathDatabase

# 创建数据库实例
db = MathDatabase()
db.connect()

# 添加用户
user_id = db.add_user('张三')

# 获取随机题目
problems = db.get_random_problems(10)

# 记录答题
is_correct = db.record_answer(user_id, problem_id, user_answer)

# 获取用户统计
stats = db.get_user_statistics(user_id)

# 获取题目统计
problem_stats = db.get_problem_statistics(problem_id)

db.close()
```

## 题库统计

- 加法题：9,801 道
- 减法题：4,950 道
- 总计：14,751 道

数字范围：1-9（一位数）和 10-99（两位数）

## 系统要求

- Python 3.6+
- SQLite3（Python内置）

## 后续开发建议

1. 添加Web界面（使用Flask或Django）
2. 添加难度分级（按数字范围分类）
3. 添加计时功能
4. 添加错题本功能
5. 添加学习进度跟踪
6. 添加成就系统
7. 导出学习报告
