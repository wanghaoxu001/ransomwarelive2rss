# 勒索软件威胁情报RSS服务

基于Ransomware.live API的威胁情报聚合服务，专注于中国地区金融服务行业和全球网络攻击事件的RSS输出。

## 功能特性

- 🕐 **定时更新**: 每小时自动调用Ransomware.live API获取最新数据
- 🎯 **精准筛选**: 筛选中国地区（CN、HK、MO）受害者或全球金融服务行业受害者
- 🌍 **全球监控**: 收集全球网络攻击事件信息
- 🤖 **智能摘要**: 支持LLM API生成高质量中文新闻摘要，失败时自动回退到固定模板
- 📰 **多模式摘要**: 可配置使用LLM智能生成或固定模板生成摘要
- 📡 **RSS输出**: 通过标准RSS格式输出威胁情报
- 🔄 **去重处理**: 基于URL字段确保只处理新增条目
- 💾 **数据持久化**: 使用SQLite数据库存储历史数据

## 数据来源

本服务调用以下Ransomware.live API v2端点：

1. `/recentvictims` - 获取最近的勒索软件受害者信息
2. `/recentcyberattacks` - 获取最近的网络攻击事件

> **注意**: 本服务使用[Ransomware.live API v2](https://api.ransomware.live/v2)，该版本提供免费访问但有每日调用限制。

## 筛选规则

### 受害者数据筛选
- **地区**: 中国大陆(CN)、香港(HK)、澳门(MO) **或**
- **行业**: Financial Services (金融服务)

### 网络攻击数据
- 收集所有全球网络攻击事件，无地区限制

## 安装和运行

### 方式一：直接运行

#### 环境要求
- Python 3.7+
- pip

#### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd ransomware2rss
```

2. 使用启动脚本（推荐）
```bash
chmod +x start.sh
./start.sh
```

或者手动安装：

```bash
pip install -r requirements.txt
python app.py
```

#### LLM配置（可选）

如果要使用LLM智能生成摘要，需要配置API密钥：

```bash
# 方式一：环境变量（推荐）
export LLM_API_KEY='your-api-key-here'

# 方式二：修改config.py
# 在config.py中设置: LLM_API_KEY = 'your-api-key-here'
```

支持的LLM服务：
- **OpenAI**: 官方API，需要API密钥
- **其他兼容服务**: 修改`LLM_BASE_URL`配置

如果不配置LLM，服务将自动使用固定模板生成摘要。

### 方式二：Docker部署（推荐）

#### 使用Docker Compose（最简单）
```bash
# 克隆项目
git clone <repository-url>
cd ransomware2rss

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 使用Docker
```bash
# 构建镜像
docker build -t ransomware-rss .

# 运行容器
docker run -d \
  --name ransomware-rss \
  -p 15000:15000 \
  -v $(pwd)/data:/app/data \
  ransomware-rss

# 查看日志
docker logs -f ransomware-rss
```

服务将在 `http://localhost:15000` 启动。

## API端点

### RSS Feed
```
GET /rss
```
获取RSS格式的威胁情报feed，可直接在RSS阅读器中订阅。

### JSON格式数据
```
GET /api/news
```
获取JSON格式的最新威胁情报数据。

### 手动更新数据
```
POST /api/update
```
手动触发数据更新，无需等待定时任务。

### 服务状态
```
GET /api/status
```
查看服务运行状态，包括数据统计和最后更新时间。

## RSS订阅

将以下地址添加到您的RSS阅读器：
```
http://localhost:15000/rss
```

## 测试服务

项目包含测试脚本，可以验证服务是否正常运行：

```bash
# 启动服务后，在另一个终端运行测试
python test_service.py
```

测试脚本会检查：
- 主页是否可访问
- RSS feed是否正常生成
- JSON API是否返回正确格式
- 服务状态API是否正常
- 手动更新功能是否工作

### LLM功能测试

如果配置了LLM，可以单独测试LLM功能：

```bash
# 测试LLM功能
python test_llm.py

# 查看LLM设置指南
python test_llm.py --help

# LLM功能演示（推荐）
python demo_llm.py              # 完整演示
python demo_llm.py --config     # 仅显示配置说明
python demo_llm.py --demo       # 仅显示摘要对比
python demo_llm.py --test       # 仅显示测试指南
```

LLM测试会检查：
- LLM配置是否正确
- API连接是否正常
- 摘要生成是否工作
- 提供详细的设置指南

演示脚本包含：
- 支持的LLM服务列表（OpenAI、Azure、Ollama等）
- 详细的配置方法和示例
- 摘要生成效果对比
- 性能调优参数说明

## 配置说明

所有配置都在 `config.py` 文件中，您可以根据需要修改。项目提供了 `config.template.py` 作为配置模板，建议按以下步骤操作：

1. 复制配置模板：
```bash
cp config.template.py config.py
```

2. 修改 `config.py` 中的配置项

### 主要配置项

#### 基础配置
- `DATABASE_PATH`: 数据库文件路径
- `RANSOMWARE_API_BASE`: Ransomware.live API基础URL
- `API_TIMEOUT`: API请求超时时间（秒）

#### 服务器配置
- `HOST`: 服务器监听地址（默认：0.0.0.0）
- `PORT`: 服务器监听端口（默认：15000）
- `DEBUG`: 是否启用调试模式

#### 数据更新配置
- `UPDATE_INTERVAL_HOURS`: 数据更新间隔（小时）

#### 筛选配置
- `CHINA_COUNTRY_CODES`: 中国地区国家代码列表
- `TARGET_ACTIVITY`: 目标行业（与中国地区为OR关系）

#### RSS配置
- `RSS_TITLE`: RSS标题
- `RSS_DESCRIPTION`: RSS描述
- `RSS_LANGUAGE`: RSS语言
- `RSS_MAX_ITEMS`: RSS中最大条目数

#### LLM配置（可选）
- `LLM_ENABLED`: 是否启用LLM生成摘要
- `LLM_BASE_URL`: LLM API基础URL
- `LLM_API_KEY`: LLM API密钥（建议通过环境变量设置）
- `LLM_MODEL`: 使用的模型名称
- `LLM_TIMEOUT`: LLM API请求超时时间
- `LLM_MAX_TOKENS`: 摘要最大token数
- `LLM_TEMPERATURE`: 生成温度

### 安全建议

1. 敏感配置（如API密钥）建议通过环境变量设置：
```bash
export LLM_API_KEY='your-api-key-here'
```

2. 不要将包含实际API密钥的 `config.py` 提交到版本控制系统

3. 确保 `config.py` 文件权限设置正确：
```bash
chmod 600 config.py
```

### 配置示例

#### 基本配置
```python
# 数据库配置
DATABASE_PATH = "ransomware_data.db"

# 服务器配置
HOST = "0.0.0.0"
PORT = 15000
DEBUG = False
```

#### LLM配置
```python
# LLM配置
LLM_ENABLED = True
LLM_BASE_URL = "https://api.openai.com/v1"  # 或其他LLM服务URL
LLM_MODEL = "gpt-3.5-turbo"  # 或其他模型名称
LLM_TIMEOUT = 30
LLM_MAX_TOKENS = 2000
LLM_TEMPERATURE = 0.3
```

## 数据格式

### RSS条目格式
每个RSS条目包含：
- **标题**: 带有类型标识和地区信息的新闻标题
- **链接**: 原始数据来源URL
- **描述**: 中文新闻摘要
- **发布时间**: 数据发现时间

### 新闻摘要示例

服务支持两种摘要生成模式：

#### LLM智能生成摘要（推荐）
当配置了LLM API时，系统会使用人工智能生成更自然、更准确的中文新闻摘要：

```
【勒索软件攻击】香港某知名银行遭到Qilin勒索软件组织攻击，该金融机构的核心业务系统
可能受到影响。攻击发生于2025年5月28日，涉及大量客户敏感数据和财务信息。此次事件
再次提醒金融行业需要加强网络安全防护，建立更完善的应急响应机制。
```

#### 固定模板摘要（备用）
当LLM不可用时，系统自动回退到固定模板生成摘要：

**中国地区金融服务机构**:
```
【勒索软件攻击】[香港]金融服务机构ABC银行遭到Qilin勒索软件组织攻击。
该攻击于2025-05-28被发现，可能涉及敏感的客户数据和财务信息。
此次攻击再次凸显了网络安全威胁的严重性，相关机构应加强防护措施。
```

**全球金融服务机构**:
```
【勒索软件攻击】金融服务机构XYZ银行遭到Akira勒索软件组织攻击。
该攻击于2025-05-28被发现，可能涉及敏感的客户数据和财务信息。
此次攻击再次凸显了网络安全威胁的严重性，相关机构应加强防护措施。
```

**中国地区其他行业**:
```
【勒索软件攻击】[中国大陆]Manufacturing行业企业某制造公司遭到Play勒索软件组织攻击。
该攻击于2025-05-28被发现，可能涉及重要的业务数据和信息。
此次攻击再次凸显了网络安全威胁的严重性，相关机构应加强防护措施。
```

**网络攻击事件类型**:
```
【网络安全事件】某公司数据泄露事件。该事件发生于2025-05-28，
据报告，攻击者获取了大量敏感数据...此类网络攻击事件提醒各组织需要
持续关注网络安全威胁并采取相应防护措施。
```

## 数据库结构

### victims表
存储勒索软件受害者信息：
- `url`: 唯一标识符，用于去重
- `title`: 受害者名称
- `country`: 国家代码
- `activity`: 行业分类
- `group_name`: 勒索软件组织名称
- `discovered`: 发现时间
- `summary`: 中文摘要

### cyberattacks表
存储网络攻击事件信息：
- `url`: 唯一标识符，用于去重
- `title`: 事件标题
- `date`: 事件日期
- `description`: 事件描述
- `summary`: 中文摘要

## 日志记录

服务包含详细的日志记录功能：
- 数据更新状态
- API调用结果
- 错误信息
- 新增数据统计

## 注意事项

1. **API限制**: Ransomware.live API可能有调用频率限制，请合理设置更新频率
2. **网络连接**: 确保服务器能够访问 `api.ransomware.live`
3. **数据准确性**: 本服务基于第三方API，数据准确性依赖于数据源
4. **存储空间**: 长期运行会积累大量数据，请定期清理或备份数据库

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查网络连接
   - 确认API服务状态
   - 查看日志中的错误信息
   - 确保使用正确的API v2端点

2. **JSON解析错误 (Expecting value: line 1 column 1)**
   - 通常是API端点错误导致
   - 确认配置文件中的`RANSOMWARE_API_BASE`为`https://api.ransomware.live/v2`
   - 检查API是否返回有效的JSON数据

3. **RSS生成失败**
   - 检查数据库连接
   - 确认数据格式正确性

4. **定时任务不执行**
   - 检查服务是否正常运行
   - 查看日志中的调度信息

5. **Docker容器无法启动**
   - 检查端口是否被占用
   - 确认Docker和docker-compose版本
   - 查看容器日志：`docker-compose logs`

6. **LLM摘要生成失败**
   - 检查API密钥是否正确设置
   - 确认LLM_BASE_URL配置正确
   - 检查网络连接到LLM服务
   - 查看日志中的详细错误信息
   - 运行`python test_llm.py`进行诊断

7. **LLM API调用超时**
   - 增加`LLM_TIMEOUT`配置值
   - 检查网络连接稳定性
   - 考虑使用更快的模型

8. **LLM生成的摘要质量不佳**
   - 调整`LLM_TEMPERATURE`参数（0.1-1.0）
   - 增加`LLM_MAX_TOKENS`限制
   - 尝试使用更高级的模型（如gpt-4）
   - 修改提示词模板以获得更好效果

## 开发和贡献

### 项目结构
```
ransomware2rss/
├── app.py              # 主应用文件
├── config.py           # 配置文件
├── requirements.txt    # Python依赖
├── start.sh           # 启动脚本
├── test_service.py    # 测试脚本
├── test_llm.py        # LLM功能测试脚本
├── demo_llm.py        # LLM功能演示脚本
├── Dockerfile         # Docker配置
├── docker-compose.yml # Docker Compose配置
├── .gitignore         # Git忽略文件
└── README.md          # 项目说明
```

### 自定义开发
1. 修改 `config.py` 中的配置
2. 在 `app.py` 中添加新的API端点
3. 自定义LLM提示词模板以获得更好的摘要效果
4. 运行测试确保功能正常

### LLM提示词自定义
可以在`config.py`中修改以下模板来优化摘要生成效果：
- `VICTIM_PROMPT_TEMPLATE`: 受害者摘要生成提示词
- `CYBERATTACK_PROMPT_TEMPLATE`: 网络攻击摘要生成提示词

## 许可证

本项目基于MIT许可证开源。

## 免责声明

本服务仅用于网络安全威胁情报收集和分析，不承担数据准确性责任。使用者应当遵守相关法律法规，合理使用威胁情报信息。