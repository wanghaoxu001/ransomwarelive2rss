# -*- coding: utf-8 -*-
"""
勒索软件威胁情报RSS服务配置文件模板
请复制此文件为config.py并填入实际配置值
"""

# 数据库配置
DATABASE_PATH = "ransomware_data.db"  # 数据库文件路径

# API配置
RANSOMWARE_API_BASE = "https://api.ransomware.live/v2"  # Ransomware.live API基础URL
API_TIMEOUT = 30  # API请求超时时间（秒）

# 服务器配置
HOST = "0.0.0.0"  # 服务器监听地址
PORT = 15000  # 服务器监听端口
DEBUG = False  # 是否启用调试模式

# 定时任务配置
UPDATE_INTERVAL_HOURS = 1  # 数据更新间隔（小时）

# 筛选配置
CHINA_COUNTRY_CODES = ["CN", "HK", "MO"]  # 中国地区国家代码
TARGET_ACTIVITY = "Financial Services"  # 目标行业（与中国地区为OR关系）

# RSS配置
RSS_TITLE = "勒索软件威胁情报RSS"
RSS_DESCRIPTION = "基于Ransomware.live API的勒索软件威胁情报聚合服务，筛选中国地区受害者或全球金融服务行业受害者以及全球网络攻击事件"
RSS_LANGUAGE = "zh-cn"
RSS_GENERATOR = "Ransomware2RSS Service"
RSS_MAX_ITEMS = 50  # RSS中最大条目数

# 国家代码映射
COUNTRY_NAMES = {
    "CN": "中国大陆",
    "HK": "香港",
    "MO": "澳门",
    "TW": "台湾",
    "US": "美国",
    "GB": "英国",
    "DE": "德国",
    "FR": "法国",
    "JP": "日本",
    "KR": "韩国",
    "SG": "新加坡",
    "AU": "澳大利亚",
    "CA": "加拿大",
}

# 日志配置
LOG_LEVEL = "INFO"  # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# 新闻摘要模板
VICTIM_SUMMARY_TEMPLATE = "【勒索软件攻击】{country_name}金融服务机构{company_name}遭到{group_name}勒索软件组织攻击。该攻击于{discovered}被发现，目标为金融服务行业，可能涉及敏感的客户数据和财务信息。此次攻击再次凸显了金融行业面临的网络安全威胁，相关机构应加强防护措施。"

CYBERATTACK_SUMMARY_TEMPLATE = "【网络安全事件】{title}。{date_info}{description_info}此类网络攻击事件提醒各组织需要持续关注网络安全威胁并采取相应防护措施。"

# LLM API配置
LLM_ENABLED = True  # 是否启用LLM生成摘要
LLM_BASE_URL = "YOUR_LLM_API_BASE_URL"  # LLM API基础URL
LLM_API_KEY = "YOUR_LLM_API_KEY"  # LLM API密钥，请在环境变量或此处设置
LLM_MODEL = "YOUR_LLM_MODEL_NAME"  # 使用的模型
LLM_TIMEOUT = 30  # LLM API请求超时时间（秒）
LLM_MAX_TOKENS = 2000  # 摘要最大token数
LLM_TEMPERATURE = 0.3  # 生成温度

# LLM摘要提示词模板
VICTIM_PROMPT_TEMPLATE = """请为以下勒索软件攻击事件生成一段简洁的中文新闻摘要（100-150汉字）：

受害者：{victim}
国家：{country}
行业：{activity}
攻击组织：{group}
发现时间：{discovered}
描述：{description}

要求：
1. 使用【勒索软件攻击】开头
2. 突出地区、行业、受害者和攻击组织信息
3. 强调网络安全威胁的严重性
4. 语言简洁专业，适合新闻报道
5. 不要包含不确定或推测性信息"""

CYBERATTACK_PROMPT_TEMPLATE = """请为以下网络安全事件生成一段简洁的中文新闻摘要（100-150汉字）：

标题：{title}
日期：{date}
描述：{summary}
国家：{country}

要求：
1. 使用【网络安全事件】开头
2. 提取关键信息，避免重复
3. 强调网络安全威胁的重要性
4. 语言简洁专业，适合新闻报道
5. 如果信息不足，说明"详细信息正在调查中"
6. 不要包含不确定或推测性信息"""
