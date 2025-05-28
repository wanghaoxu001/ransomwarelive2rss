#!/bin/bash

echo "勒索软件威胁情报RSS服务启动脚本"
echo "================================"

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✓ 检测到Python: $python_version"
else
    echo "✗ 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查pip
if command -v pip3 &> /dev/null; then
    echo "✓ 检测到pip3"
else
    echo "✗ 未找到pip3，请先安装pip"
    exit 1
fi

# 安装依赖
echo "正在安装Python依赖..."
pip3 install -r requirements.txt

if [[ $? -eq 0 ]]; then
    echo "✓ 依赖安装完成"
else
    echo "✗ 依赖安装失败"
    exit 1
fi

# 启动服务
echo "正在启动勒索软件威胁情报RSS服务..."
echo "服务地址: http://localhost:15000"
echo "RSS订阅地址: http://localhost:15000/rss"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py 