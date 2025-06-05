# 勒索软件RSS服务管理命令

.PHONY: help build start stop restart deploy logs status clean test

# 默认目标
help:
	@echo "勒索软件RSS服务管理命令："
	@echo ""
	@echo "构建和部署："
	@echo "  make build     - 构建Docker镜像"
	@echo "  make deploy    - 完整重新部署（推荐用于代码更新）"
	@echo "  make start     - 启动服务"
	@echo "  make stop      - 停止服务"
	@echo "  make restart   - 快速重启服务"
	@echo ""
	@echo "监控和调试："
	@echo "  make logs      - 查看实时日志"
	@echo "  make status    - 查看服务状态"
	@echo "  make test      - 运行健康检查"
	@echo ""
	@echo "维护："
	@echo "  make clean     - 清理未使用的镜像和容器"
	@echo ""

# 构建镜像
build:
	@echo "🔨 构建Docker镜像..."
	docker compose build

# 完整部署（代码更新后使用）
deploy:
	@echo "🚀 完整重新部署..."
	@if [ -f "./deploy.sh" ]; then \
		./deploy.sh; \
	else \
		docker compose down; \
		docker compose build --no-cache; \
		docker compose up -d; \
		@echo "✅ 部署完成"; \
	fi

# 启动服务
start:
	@echo "▶️  启动服务..."
	docker compose up -d
	@echo "✅ 服务已启动"

# 停止服务
stop:
	@echo "⏹️  停止服务..."
	docker compose down
	@echo "✅ 服务已停止"

# 快速重启
restart:
	@echo "🔄 重启服务..."
	@if [ -f "./restart.sh" ]; then \
		./restart.sh; \
	else \
		docker compose restart; \
		@echo "✅ 重启完成"; \
	fi

# 查看日志
logs:
	@echo "📋 查看实时日志 (按Ctrl+C退出)..."
	docker compose logs -f

# 查看状态
status:
	@echo "📊 服务状态："
	docker compose ps
	@echo ""
	@echo "🧪 API健康检查："
	@curl -s -f http://localhost:8080/api/status > /dev/null && echo "✅ API响应正常" || echo "❌ API响应异常"

# 运行测试
test:
	@echo "🧪 运行健康检查..."
	@if [ -f "test_llm_title.py" ]; then \
		python test_llm_title.py; \
	fi
	@if [ -f "test_service.py" ]; then \
		python test_service.py; \
	fi

# 清理
clean:
	@echo "🧹 清理未使用的Docker资源..."
	docker system prune -f
	@echo "✅ 清理完成"

# 更新代码并部署
update:
	@echo "📥 更新代码并重新部署..."
	git pull
	make deploy 