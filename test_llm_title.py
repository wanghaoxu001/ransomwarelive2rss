#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM标题生成功能测试脚本
"""

import sys
import os
from config import *
from app import LLMSummaryGenerator

def test_llm_title_generation():
    """测试LLM标题生成功能"""
    print("=== LLM标题生成功能测试 ===\n")
    
    # 初始化LLM生成器
    generator = LLMSummaryGenerator()
    
    if not generator.enabled:
        print("❌ LLM功能未启用，请检查配置")
        return False
    
    if not generator.title_enabled:
        print("❌ LLM标题生成功能未启用，请检查配置")
        return False
        
    print("✅ LLM客户端初始化成功")
    print(f"✅ 使用模型: {LLM_MODEL}")
    print(f"✅ 标题生成已启用\n")
    
    # 测试受害者标题生成
    print("--- 测试受害者标题生成 ---")
    victim_test_data = {
        "victim": "中国工商银行",
        "country": "CN", 
        "activity": "Financial Services",
        "group": "BlackCat",
        "discovered": "2025-01-28"
    }
    
    print("测试数据:")
    for key, value in victim_test_data.items():
        print(f"  {key}: {value}")
    
    print("\n生成标题...")
    victim_title = generator.generate_victim_title(victim_test_data)
    
    if victim_title:
        print(f"✅ 受害者标题生成成功: {victim_title}")
    else:
        print("❌ 受害者标题生成失败")
        return False
    
    # 测试网络攻击标题生成
    print("\n--- 测试网络攻击标题生成 ---")
    attack_test_data = {
        "title": "Major US Retailer Suffers Data Breach",
        "date": "2025-01-27",
        "description": "Hackers exploited an unpatched vulnerability to access customer credit card database containing 5 million records"
    }
    
    print("测试数据:")
    for key, value in attack_test_data.items():
        print(f"  {key}: {value}")
    
    print("\n生成标题...")
    attack_title = generator.generate_cyberattack_title(attack_test_data)
    
    if attack_title:
        print(f"✅ 网络攻击标题生成成功: {attack_title}")
    else:
        print("❌ 网络攻击标题生成失败")
        return False
    
    return True

def show_title_comparison():
    """显示标题生成效果对比"""
    print("\n=== 标题生成效果对比 ===\n")
    
    print("1. 受害者事件标题对比:")
    print("   原始数据: 中国工商银行")
    print("   传统格式: 【勒索】[中国大陆] 中国工商银行")
    print("   LLM生成: 中国工商银行遭BlackCat勒索软件攻击 金融数据面临安全威胁")
    
    print("\n2. 网络攻击事件标题对比:")
    print("   原始数据: Major US Retailer Suffers Data Breach")
    print("   传统格式: 【网络安全事件】Major US Retailer Suffers Data Breach")
    print("   LLM生成: 美国大型零售商遭数据泄露 500万客户信用卡信息被窃")
    
    print("\nLLM生成标题的优势:")
    print("✓ 更符合中文新闻标题习惯")
    print("✓ 突出关键信息和影响范围")
    print("✓ 避免英文和中文混合")
    print("✓ 提高可读性和吸引力")
    print("✓ 自动提取核心要素")

def test_configuration():
    """测试配置项"""
    print("\n=== 配置检查 ===")
    
    config_items = [
        ("LLM_TITLE_ENABLED", LLM_TITLE_ENABLED, "LLM标题生成开关"),
        ("LLM_ENABLED", LLM_ENABLED, "LLM总开关"),
        ("LLM_MODEL", LLM_MODEL, "使用的模型"),
        ("LLM_BASE_URL", LLM_BASE_URL, "API端点"),
        ("LLM_API_KEY", "***" + LLM_API_KEY[-10:] if LLM_API_KEY else "未设置", "API密钥"),
    ]
    
    for name, value, desc in config_items:
        print(f"{desc}: {value}")
    
    print(f"\n提示词模板:")
    print(f"受害者标题模板长度: {len(VICTIM_TITLE_PROMPT_TEMPLATE)} 字符")
    print(f"网络攻击标题模板长度: {len(CYBERATTACK_TITLE_PROMPT_TEMPLATE)} 字符")

def run_integration_test():
    """运行集成测试"""
    print("\n=== 集成测试 ===")
    
    try:
        from app import RansomwareRSSService
        
        print("创建服务实例...")
        service = RansomwareRSSService()
        
        print("检查LLM功能状态...")
        if service.llm_generator.enabled:
            print("✅ LLM摘要生成: 已启用")
        else:
            print("❌ LLM摘要生成: 未启用")
        
        if service.llm_generator.title_enabled:
            print("✅ LLM标题生成: 已启用")
        else:
            print("❌ LLM标题生成: 未启用")
        
        print("✅ 服务实例创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

def main():
    """主函数"""
    print("LLM标题生成功能测试工具\n")
    
    # 检查配置
    test_configuration()
    
    # 显示对比效果
    show_title_comparison()
    
    # 运行功能测试
    if test_llm_title_generation():
        print("\n✅ LLM标题生成功能测试通过")
    else:
        print("\n❌ LLM标题生成功能测试失败")
        return 1
    
    # 运行集成测试
    if run_integration_test():
        print("✅ 集成测试通过")
    else:
        print("❌ 集成测试失败") 
        return 1
    
    print("\n🎉 所有测试通过！LLM标题生成功能已就绪。")
    print("\n使用说明:")
    print("1. 启动服务: python app.py")
    print("2. 查看状态: curl http://localhost:8080/api/status")
    print("3. 触发更新: curl -X POST http://localhost:8080/api/update")
    print("4. 查看RSS: curl http://localhost:8080/rss")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 