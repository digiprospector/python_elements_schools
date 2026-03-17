# 数学题库练习系统

一个面向小学数学练习的 Web 应用，当前采用 `Flask + Supabase` 架构。  
系统支持按 `科目 / 年级 / 项目` 组织题库，并在应用启动时自动检查 Supabase 中是否已有对应项目题库；如果没有，会自动生成并写入题库。

## 当前已支持的项目

### 1. 数学 / 小二下 / 一位数和两位数加减法

- 题库总数：`14751`
- 题型：
  - 加法
  - 减法
- 答题方式：单一数值答案

### 2. 数学 / 小二下 / 带余数的除法

- 题库总数：`324`
- 题目范围：
  - 被除数小于 `100`
  - 除数是 `1` 位数
  - 商是 `1` 位数
  - 余数不能为 `0`
- 题型：
  - 除法
- 答题方式：输入 `商` 和 `余数`

## 主要功能

- 用户登录
- 登录后按 `科目 / 年级 / 项目` 选择学习路径
- 按题型和标签筛选题目
- 在线作答与即时反馈
- 错题本
- 相似题练习
- 答题统计
- PDF 导出

## 技术架构

- 后端：`Python + Flask`
- 数据库：`Supabase`
- 前端：`HTML + CSS + JavaScript`
- 题库组织方式：
  - 每道题都写入 `problems` 表
  - 题目的 `tags` 中包含范围标签
  - 例如：`科目:数学`、`年级:小二下`、`项目:带余数的除法`

## 启动逻辑

应用启动时会执行以下流程：

1. 读取 `config.py` 中的 Supabase 配置
2. 检查 Supabase 表结构是否存在
3. 遍历项目注册表
4. 如果某个项目在 Supabase 中没有题库，就自动生成并写入
5. 启动 Flask Web 服务

这意味着：

- 不再以本地 SQLite 题库作为主流程
- 新增项目时，只需要注册新项目和生成器
- 后续启动时会自动补题

## 安装与启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Supabase

复制并编辑 `config.py`：

```python
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

### 3. 初始化 Supabase 表结构

在 Supabase SQL Editor 中执行：

- [supabase_schema.sql](C:/walt/git/hub/python_elements_schools/supabase_schema.sql)

注意：

- 应用会自动生成题库数据
- 但不会自动创建 Supabase 的表和 RPC 函数
- 所以 `supabase_schema.sql` 仍然需要先执行一次

### 4. 启动应用

```bash
python app.py
```

或：

```bash
bash start.sh
```

启动后访问：

```text
http://localhost:5000
```

## 部署到 Vercel

仓库已包含 `vercel.json` 和 `api/index.py`，可以直接按 Flask Serverless 应用部署到 Vercel。

### 1. 配置环境变量

在 Vercel 项目设置中添加：

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FLASK_SECRET_KEY`

说明：

- `SUPABASE_URL`、`SUPABASE_KEY` 用于连接 Supabase
- `FLASK_SECRET_KEY` 需要固定，否则 Vercel 冷启动后 session 可能失效

### 2. 初始化 Supabase

先在 Supabase SQL Editor 中执行：

- [supabase_schema.sql](C:/walt/git/hub/python_elements_schools/supabase_schema.sql)

### 3. 预先写入题库

Vercel 默认不自动补题库，因为首次批量生成题目可能超过 serverless 的冷启动时间。

推荐流程：

1. 在本地配置好 `SUPABASE_URL` 和 `SUPABASE_KEY`
2. 本地运行一次 `python app.py`
3. 等待题库自动写入 Supabase
4. 再部署到 Vercel

如果你确认当前题库规模可以接受，也可以额外设置：

- `AUTO_SEED_PROBLEM_BANKS=true`

但更推荐只在本地或一次性初始化时补题。

### 4. 部署命令

```bash
vercel
```

生产部署：

```bash
vercel --prod
```

## 使用流程

1. 输入用户名登录
2. 选择 `科目 / 年级 / 项目`
3. 进入练习页
4. 选择题目数量、题型和标签
5. 提交答案
6. 查看统计和错题本

## 题库生成入口

项目题库统一在：

- [problem_catalog.py](C:/walt/git/hub/python_elements_schools/problem_catalog.py)

这里定义了：

- 项目注册表 `PROJECT_CATALOG`
- 每个项目的题库生成函数
- 每个项目的答题模式
- 每个项目的练习页筛选配置

如果要新增项目，通常需要：

1. 新增一个生成函数
2. 把项目注册到 `PROJECT_CATALOG`
3. 提供该项目的 `answer_mode`
4. 提供该项目的 `practice_config`

然后重启应用，系统会自动检查并补题。

## 关键文件

- [app.py](C:/walt/git/hub/python_elements_schools/app.py)
  - Flask 入口
  - 启动时自动补题
  - 登录、练习、统计、错题本 API

- [database_v3.py](C:/walt/git/hub/python_elements_schools/database_v3.py)
  - Supabase 数据访问层

- [problem_catalog.py](C:/walt/git/hub/python_elements_schools/problem_catalog.py)
  - 项目注册与题库生成逻辑

- [generate_tagged_problems.py](C:/walt/git/hub/python_elements_schools/generate_tagged_problems.py)
  - 将某个项目的题库导出为 JSON

- [templates/index.html](C:/walt/git/hub/python_elements_schools/templates/index.html)
  - 登录与学习路径选择页

- [templates/practice.html](C:/walt/git/hub/python_elements_schools/templates/practice.html)
  - 练习页面

- [templates/wrong_book.html](C:/walt/git/hub/python_elements_schools/templates/wrong_book.html)
  - 错题本页面

- [templates/statistics.html](C:/walt/git/hub/python_elements_schools/templates/statistics.html)
  - 统计页面

- [static/js/practice.js](C:/walt/git/hub/python_elements_schools/static/js/practice.js)
  - 练习页逻辑
  - 支持整数答案和“商 + 余数”双输入

- [static/js/wrong_book.js](C:/walt/git/hub/python_elements_schools/static/js/wrong_book.js)
  - 错题本和相似题练习逻辑

## 数据表说明

### `problems`

- `id`
- `question`
- `num1`
- `num2`
- `answer`
- `type`
- `tags`
- `created_at`

说明：

- `answer` 是统一存储字段
- 普通整数题直接存整数
- “带余数的除法”会把 `商` 和 `余数` 编码后存进 `answer`
- 前端展示时会再转换回 `商 余 余数`

### `users`

- `id`
- `username`
- `created_at`

### `user_answers`

- `id`
- `user_id`
- `problem_id`
- `user_answer`
- `is_correct`
- `answered_at`

### `wrong_problems`

- `id`
- `user_id`
- `problem_id`
- `tags`
- `wrong_count`
- `correct_streak`
- `created_at`
- `updated_at`

## 相似题规则

- 相似题只在当前项目内查找
- 相似度只根据题目的内容标签判断
- 不会把 `科目 / 年级 / 项目` 这些范围标签当作“相似”的依据

## 常见问题

### 启动时报“缺少必须的表或函数”

先在 Supabase SQL Editor 中执行：

- [supabase_schema.sql](C:/walt/git/hub/python_elements_schools/supabase_schema.sql)

### 为什么启动时会比较慢

如果某个项目还没有题库，应用启动时会自动生成并写入 Supabase。首次启动会比平时慢。

### 如何新增项目

在 [problem_catalog.py](C:/walt/git/hub/python_elements_schools/problem_catalog.py) 中注册新项目和生成器，然后重启应用。

### 旧的 SQLite 文件还需要吗

当前主流程不依赖本地 SQLite。仓库里保留的一些旧脚本和旧文件主要用于历史兼容或参考，不再是推荐路径。
