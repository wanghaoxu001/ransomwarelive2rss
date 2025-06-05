#!/bin/bash

# 快速重启脚本 - 不重新构建镜像
# 适用于配置文件修改或服务异常时的快速重启

set -e

echo "=== 快速重启勒索软件RSS服务 ==="
echo "时间: $(date)"
echo ""

# 检查docker-compose文件
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：未找到docker-compose.yml文件"
    exit 1
fi

# 重启服务
echo "🔄 重启服务..."
docker compose restart

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查状态
echo "🔍 检查服务状态..."
docker compose ps

# 简单健康检查
echo ""
echo "🧪 健康检查..."
if curl -s -f http://localhost:8080/api/status > /dev/null; then
    echo "✅ 服务重启成功，API响应正常"
else
    echo "⚠️  API响应异常，建议查看日志："
    echo "docker compose logs ransomware-rss"
fi

echo ""
echo "🎉 重启完成！" 