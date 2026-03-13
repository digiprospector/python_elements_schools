# 数学题库练习系统

一个用于小学生练习一位数和两位数加减法的系统。

## 功能特点

- 完整的题库：包含所有可能的一位数和两位数加减法组合（14,751道题）
- 智能分类：每道题都有详细的标签（进位/退位、数字位数、结果范围等）
- 灵活筛选：通过checkbox选择题目类型，支持多条件组合
- 错题本功能：
  - 自动记录答错的题目
  - 显示错误次数和连续正确次数
  - 可以练习与错题相似的题目
  - 连续做对同类型题目3次后，错题自动移除
- 用户管理：支持多用户使用
- 答题记录：自动记录每次答题的正确与错误
- 统计分析：查看个人答题统计和正确率
- Web界面：美观的响应式设计，支持手机和平板

## 文件说明

- `app.py` - Flask Web应用主程序
- `database_v3.py` - 数据库管理模块（支持标签筛选和错题本）
- `generate_tagged_problems.py` - 带标签的题库生成器
- `practice.py` - 命令行练习程序
- `test_tags.py` - 标签功能测试工具
- `test_wrong_book.py` - 错题本功能测试工具
- `requirements.txt` - Python依赖列表
- `TAGS_GUIDE.md` - 题目分类详细说明
- `templates/` - HTML模板文件
  - `index.html` - 首页
  - `practice.html` - 练习页面（含checkbox筛选）
  - `statistics.html` - 统计页面
  - `wrong_book.html` - 错题本页面
- `static/` - 静态资源文件
  - `css/style.css` - 样式文件
  - `js/practice.js` - 练习页面JavaScript
  - `js/wrong_book.js` - 错题本JavaScript
- `math_problems.db` - SQLite数据库文件
- `math_problems_tagged.json` - 带标签的完整题库JSON文件

## 数据库结构

### problems 表（题目表）
- `id` - 题目ID
- `question` - 题目内容
- `num1` - 第一个数字
- `num2` - 第二个数字
- `answer` - 正确答案
- `type` - 题目类型（加法/减法）
- `tags` - 题目标签（逗号分隔）
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

### wrong_problems 表（错题本表）
- `id` - 记录ID
- `user_id` - 用户ID
- `problem_id` - 题目ID
- `tags` - 题目标签
- `wrong_count` - 错误次数
- `correct_streak` - 连续正确次数
- `created_at` - 创建时间
- `updated_at` - 更新时间

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 生成带标签的题库（首次使用）

```bash
python generate_tagged_problems.py
```

### 3. 初始化数据库

```bash
python database_v3.py
```

这将创建数据库并导入所有题目及其标签。

### 3. 启动Web应用（推荐）

```bash
python app.py
```

然后在浏览器中访问: http://localhost:5000

Web应用功能：
- 用户登录
- 在线答题练习
- 灵活的题目筛选（通过checkbox选择）
  - 加法：选择是否包含一位数/两位数、是否进位、结果范围等
  - 减法：选择是否包含一位数/两位数、是否退位、结果范围等
- 实时反馈正确/错误
- 错题本功能
  - 自动收集答错的题目
  - 练习相似题目
  - 智能消除机制（连续做对3次同类型题目后自动移除）
- 查看答题统计

详细的分类说明请查看 [TAGS_GUIDE.md](TAGS_GUIDE.md)

### 4. 命令行练习（可选）

```bash
python practice.py
```

按照提示选择功能：
- 选择 1：开始练习
- 选择 2：查看统计
- 选择 3：退出

### 3. 使用数据库API

```python
from database_v3 import MathDatabase

# 创建数据库实例
db = MathDatabase()
db.connect()

# 添加用户
user_id = db.add_user('张三')

# 获取随机题目
problems = db.get_problems_by_filters(10)

# 记录答题
is_correct = db.record_answer(user_id, problem_id, user_answer)

# 获取用户统计
stats = db.get_user_statistics(user_id)

# 获取错题本
wrong_problems = db.get_wrong_problems(user_id)

# 获取相似题目
similar = db.get_similar_problems(tags, count=10)

db.close()
```

## 题库统计

- 加法题：9,801 道
- 减法题：4,950 道
- 总计：14,751 道

数字范围：1-9（一位数）和 10-99（两位数）

## 系统要求

- Python 3.6+
- Flask 3.0+
- SQLite3（Python内置）

## Web应用截图说明

1. **首页** - 用户登录界面
2. **练习页面** - 显示题目，输入答案，实时反馈
3. **统计页面** - 显示答题统计和正确率

## 后续开发建议

1. 添加学习进度跟踪
2. 添加成就系统
3. 导出学习报告
4. 添加计时功能
5. 添加排行榜功能
6. 支持打印练习题
7. 添加家长监控功能
