#!/bin/bash

echo "数学题库练习系统 - 启动中..."
echo
echo "请确认你已经完成以下准备："
echo "1. 已在 config.py 中填入 Supabase URL 和 Key"
echo "2. 已在 Supabase SQL Editor 中执行 supabase_schema.sql"
echo
echo "应用启动后会自动检查题库。"
echo "如果当前项目在 Supabase 中没有题目，程序会自动生成并写入题库。"
echo
echo "正在启动 Web 应用..."
echo "请在浏览器中访问: http://localhost:5000"
echo

python app.py
