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

### 准备工作

在开始部署前，请先确认：

- 已有可用的 Vercel 账号
- 已有可用的 Supabase 项目
- 当前仓库代码已经推送到 GitHub

### 推荐部署顺序

1. 在 Supabase SQL Editor 中执行 `supabase_schema.sql`
2. 本地先运行一次 `python app.py`
3. 等待题库自动写入 Supabase
4. 在 Vercel 中导入本仓库
5. 配置环境变量
6. 点击部署

### Vercel 环境变量

至少需要配置：

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FLASK_SECRET_KEY`

说明：

- `SUPABASE_URL`：Supabase 项目地址
- `SUPABASE_KEY`：Supabase 访问密钥
- `FLASK_SECRET_KEY`：用于保持登录 session 稳定，必须是固定值

可选变量：

- `AUTO_SEED_PROBLEM_BANKS=true`

只有在你确认要让 Vercel 自动补题时才建议设置。通常更推荐先在本地完成题库初始化。

### 后台部署步骤

1. 登录 Vercel
2. 点击 `Add New` -> `Project`
3. 选择这个 GitHub 仓库
4. Root Directory 保持仓库根目录
5. Framework Preset 选择自动识别或 `Other`
6. 在 Environment Variables 中填入上面的变量
7. 点击 `Deploy`

### CLI 部署命令

安装 CLI：

```bash
npm i -g vercel
```

登录：

```bash
vercel login
```

部署：

```bash
vercel
```

生产部署：

```bash
vercel --prod
```

说明：

- 仓库已包含 `vercel.json`
- 在 Vercel 上默认不自动补题库
- 如需强制自动补题，可设置 `AUTO_SEED_PROBLEM_BANKS=true`
- 如果登录后刷新就掉线，先检查 `FLASK_SECRET_KEY` 是否已设置且保持固定

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
