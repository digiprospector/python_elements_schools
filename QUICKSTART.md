# 快速开始

## 首次使用

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置 Supabase

- 复制并编辑 `config.py`
- 填入真实的 `SUPABASE_URL` 和 `SUPABASE_KEY`

3. 初始化 Supabase 表结构

- 打开 Supabase SQL Editor
- 执行 `supabase_schema.sql`

4. 启动应用

```bash
bash start.sh
```

或

```bash
python app.py
```

5. 打开浏览器访问

```text
http://localhost:5000
```

## 部署到 Vercel

1. 在 Vercel 中导入本仓库
2. 配置环境变量：
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FLASK_SECRET_KEY`
3. 在 Supabase 中执行 `supabase_schema.sql`
4. 建议先本地运行一次 `python app.py`，让题库预先写入 Supabase
5. 执行部署

说明：

- 仓库已包含 `vercel.json`
- 在 Vercel 上默认不自动补题库
- 如需强制自动补题，可设置 `AUTO_SEED_PROBLEM_BANKS=true`

## 当前题库逻辑

- 题库数据以 Supabase 为准
- 应用启动时会自动检查已注册项目是否有题库
- 如果某个项目没有题目，程序会自动生成并写入 Supabase
- 当前已注册项目只有：`数学 / 小二下 / 一位数和两位数加减法`

## 使用流程

1. 登录
- 输入用户名

2. 选择学习路径
- 科目
- 年级
- 项目

3. 开始练习
- 选择题目数量
- 选择题目类型
- 按标签筛选
- 提交答案

4. 查看统计和错题本
- 统计页会显示当前选择的学习路径
- 错题本和相似题练习会限制在当前项目范围内

## 常见问题

Q: 启动时报 `缺少必须的表或函数`
A: 先去 Supabase 执行 `supabase_schema.sql`

Q: 如何新增一个项目题库
A: 在 `problem_catalog.py` 里注册新项目和生成器。应用启动时会自动检查并补题

Q: 题库数据存在哪里
A: 存在 Supabase 的 `problems` 表中
