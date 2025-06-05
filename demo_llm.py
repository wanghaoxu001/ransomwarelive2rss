#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from config import *


def demo_llm_configuration():
    """演示LLM配置和功能"""
    print("=== 勒索软件RSS服务 - LLM功能演示 ===\n")

    print("本服务支持使用LLM API生成智能的中文新闻摘要，提供以下优势：")
    print("✓ 更自然的语言表达")
    print("✓ 智能提取关键信息")
    print("✓ 根据上下文调整描述风格")
    print("✓ 自动回退到固定模板（当LLM不可用时）")

    print("\n=== 支持的LLM服务 ===")

    llm_services = [
        {
            "name": "OpenAI官方API",
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "description": "最高质量，需要API密钥",
        },
        {
            "name": "Azure OpenAI",
            "base_url": "https://your-resource.openai.azure.com/",
            "models": ["gpt-35-turbo", "gpt-4"],
            "description": "企业级，需要Azure订阅",
        },
        {
            "name": "本地Ollama",
            "base_url": "http://localhost:11434/v1",
            "models": ["qwen2", "llama3", "mistral"],
            "description": "免费本地运行，无需API密钥",
        },
        {
            "name": "其他兼容API",
            "base_url": "https://api.your-service.com/v1",
            "models": ["自定义模型"],
            "description": "任何OpenAI兼容的API服务",
        },
    ]

    for i, service in enumerate(llm_services, 1):
        print(f"\n{i}. {service['name']}")
        print(f"   端点: {service['base_url']}")
        print(f"   推荐模型: {', '.join(service['models'])}")
        print(f"   说明: {service['description']}")

    print("\n=== 配置方法 ===")

    print("\n1. 环境变量配置（推荐）:")
    print("   export LLM_API_KEY='your-api-key'")
    print("   export LLM_BASE_URL='https://api.openai.com/v1'")
    print("   export LLM_MODEL='gpt-3.5-turbo'")

    print("\n2. 配置文件修改:")
    print("   编辑 config.py 文件：")
    print("   LLM_API_KEY = 'your-api-key'")
    print("   LLM_BASE_URL = 'https://api.openai.com/v1'")
    print("   LLM_MODEL = 'gpt-3.5-turbo'")

    print("\n=== 模板自定义 ===")

    print("\n可以在config.py中自定义提示词模板：")
    print(f"\n当前受害者摘要模板:\n{VICTIM_PROMPT_TEMPLATE[:200]}...")
    print(f"\n当前网络攻击摘要模板:\n{CYBERATTACK_PROMPT_TEMPLATE[:200]}...")

    print("\n=== 性能调优参数 ===")

    params = [
        ("LLM_MAX_TOKENS", LLM_MAX_TOKENS, "摘要最大长度", "100-500"),
        ("LLM_TEMPERATURE", LLM_TEMPERATURE, "创造性程度", "0.1-1.0"),
        ("LLM_TIMEOUT", LLM_TIMEOUT, "请求超时时间", "10-60秒"),
    ]

    for param, current, desc, range_info in params:
        print(f"• {param}: {current} ({desc}，建议范围: {range_info})")


def demo_with_mock_data():
    """使用模拟数据演示摘要生成效果"""
    print("\n=== 摘要生成效果对比 ===")

    # 模拟数据
    victim_data = {
        "victim": "中国工商银行",
        "country": "CN",
        "activity": "Financial Services",
        "group": "BlackCat",
        "discovered": "2025-05-28",
        "description": "攻击者通过钓鱼邮件获得初始访问权限，随后在网络中横向移动，最终加密了关键业务系统",
    }

    attack_data = {
        "title": "美国大型零售商遭受数据泄露",
        "date": "2025-05-27",
        "description": "攻击者利用未修补的漏洞获取了包含500万客户信用卡信息的数据库访问权限",
        "country": "US",
    }

    print("\n1. 固定模板生成（当前使用）:")
    print(
        "【勒索】中国大陆金融服务机构中国工商银行遭到BlackCat勒索软件组织攻击。"
    )
    print("该攻击于2025-05-28被发现，可能涉及敏感的客户数据和财务信息。")
    print("此次攻击再次凸显了网络安全威胁的严重性，相关机构应加强防护措施。")

    print("\n2. LLM智能生成（示例效果）:")
    print("【勒索】中国工商银行遭受BlackCat勒索软件组织精心策划的网络攻击，")
    print("攻击者通过钓鱼邮件突破防线，在银行内网进行横向渗透并加密核心业务系统。")
    print("此次事件影响重大，涉及大量客户敏感金融数据，银行业网络安全防护亟需升级。")

    print("\n可以看到LLM生成的摘要更加:")
    print("✓ 自然流畅，符合新闻写作风格")
    print("✓ 包含更多技术细节和攻击手法")
    print("✓ 突出事件的严重性和影响范围")
    print("✓ 语言更加专业和准确")


def show_testing_guide():
    """显示测试指南"""
    print("\n=== 测试和验证 ===")

    print("\n1. 测试LLM功能:")
    print("   python test_llm.py")

    print("\n2. 启动服务:")
    print("   python app.py")

    print("\n3. 检查服务状态:")
    print("   curl http://localhost:8080/api/status")

    print("\n4. 查看摘要效果:")
    print("   curl http://localhost:8080/api/news")

    print("\n5. 监控日志:")
    print("   服务日志会显示摘要生成方式:")
    print("   - '使用LLM生成摘要: xxx' - LLM成功")
    print("   - '使用固定模板生成摘要: xxx' - 回退到模板")
    print("   - 'LLM生成摘要失败，回退到固定模板' - LLM失败")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--config":
            demo_llm_configuration()
        elif sys.argv[1] == "--demo":
            demo_with_mock_data()
        elif sys.argv[1] == "--test":
            show_testing_guide()
        else:
            print("用法: python demo_llm.py [--config|--demo|--test]")
    else:
        demo_llm_configuration()
        demo_with_mock_data()
        show_testing_guide()


if __name__ == "__main__":
    main()
