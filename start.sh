#!/bin/bash
# 快速启动脚本

echo "数学题库练习系统 - 启动中..."
echo ""

# 检查题库文件是否存在
if [ ! -f "math_problems_tagged.json" ]; then
    echo "题库文件不存在，正在生成..."
    python generate_tagged_problems.py
    echo ""
fi

# 检查数据库是否存在
if [ ! -f "math_problems.db" ]; then
    echo "数据库不存在，正在初始化..."
    python database_v2.py
    echo ""
fi

# 启动Web应用
echo "启动Web应用..."
echo "请在浏览器中访问: http://localhost:5000"
echo ""
python app.py
