#!/bin/bash

# 勒索软件RSS服务部署脚本
# 用于代码更新后重建并重启容器

set -e  # 遇到错误立即退出

echo "=== 勒索软件RSS服务部署脚本 ==="
echo "开始时间: $(date)"
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：未找到docker-compose.yml文件"
    echo "请在项目根目录下运行此脚本"
    exit 1
fi

# 显示当前Git状态（如果是Git仓库）
if [ -d ".git" ]; then
    echo "📋 Git状态："
    git status --short
    echo "📝 最新提交："
    git log -1 --oneline
    echo ""
fi

# 停止并移除现有容器
echo "🛑 停止现有容器..."
docker compose down

# 清理旧镜像（可选，释放空间）
read -p "🧹 是否清理旧的Docker镜像? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理旧镜像..."
    docker image prune -f
    # 移除项目相关的旧镜像
    OLD_IMAGE=$(docker images | grep ransomwarelive2rss | awk '{print $3}' | head -1)
    if [ ! -z "$OLD_IMAGE" ]; then
        docker rmi $OLD_IMAGE 2>/dev/null || true
    fi
fi

# 重新构建镜像
echo "🔨 重新构建Docker镜像..."
docker compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if docker compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    
    # 显示服务信息
    echo ""
    echo "📊 服务信息："
    docker compose ps
    
    echo ""
    echo "🌐 访问地址："
    echo "  - 主页: http://localhost:8080"
    echo "  - RSS: http://localhost:8080/rss"
    echo "  - API: http://localhost:8080/api/news"
    echo "  - 状态: http://localhost:8080/api/status"
    
    # 测试API
    echo ""
    echo "🧪 API健康检查："
    if curl -s -f http://localhost:8080/api/status > /dev/null; then
        echo "✅ API响应正常"
    else
        echo "⚠️  API响应异常，请检查日志"
    fi
    
else
    echo "❌ 服务启动失败！"
    echo "📋 检查日志："
    docker compose logs --tail=20
    exit 1
fi

# 显示日志选项
echo ""
read -p "📋 是否查看实时日志? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📋 实时日志 (按Ctrl+C退出)："
    docker compose logs -f
fi

echo ""
echo "🎉 部署完成！"
echo "结束时间: $(date)" 