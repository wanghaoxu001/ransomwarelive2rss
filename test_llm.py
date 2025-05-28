#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from config import *


# 测试LLM功能
def test_llm_functionality():
    """测试LLM摘要生成功能"""
    print("=== LLM功能测试 ===\n")

    # 检查配置
    print("1. 检查LLM配置:")
    print(f"   LLM_ENABLED: {LLM_ENABLED}")
    print(f"   LLM_BASE_URL: {LLM_BASE_URL}")
    print(f"   LLM_MODEL: {LLM_MODEL}")
    print(
        f"   LLM_API_KEY: {'已设置' if (os.getenv('LLM_API_KEY') or LLM_API_KEY) else '未设置'}"
    )

    # 检查依赖
    print("\n2. 检查依赖:")
    try:
        from openai import OpenAI

        print("   ✓ OpenAI库已安装")
    except ImportError:
        print("   ✗ OpenAI库未安装，请运行: pip install openai")
        return False

    if not LLM_ENABLED:
        print("\n   ⚠️  LLM功能已在配置中禁用")
        return False

    # 测试API连接
    print("\n3. 测试LLM API连接:")
    api_key = os.getenv("LLM_API_KEY") or LLM_API_KEY
    if not api_key:
        print("   ✗ 未设置API密钥")
        print("   请设置环境变量: export LLM_API_KEY='your-api-key'")
        print("   或在config.py中设置LLM_API_KEY")
        return False

    try:
        client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL)

        # 测试简单调用
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "请回复'测试成功'"}],
            max_tokens=10,
            timeout=LLM_TIMEOUT,
        )

        result = response.choices[0].message.content.strip()
        print(f"   ✓ API连接成功，响应: {result}")

    except Exception as e:
        print(f"   ✗ API连接失败: {e}")
        return False

    # 测试摘要生成
    print("\n4. 测试摘要生成:")

    # 测试受害者摘要
    test_victim = {
        "victim": "测试银行",
        "country": "CN",
        "activity": "Financial Services",
        "group": "TestRansomware",
        "discovered": "2024-01-01",
        "description": "这是一个测试案例",
    }

    try:
        prompt = VICTIM_PROMPT_TEMPLATE.format(
            victim=test_victim["victim"],
            country="中国大陆",
            activity=test_victim["activity"],
            group=test_victim["group"],
            discovered=test_victim["discovered"],
            description=test_victim["description"],
        )

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的网络安全新闻编辑，擅长将技术信息转化为简洁易懂的新闻摘要。",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            timeout=LLM_TIMEOUT,
        )

        summary = response.choices[0].message.content.strip()
        print(f"   ✓ 受害者摘要生成成功:")
        print(f"     {summary}")

    except Exception as e:
        print(f"   ✗ 受害者摘要生成失败: {e}")
        return False

    # 测试网络攻击摘要
    test_attack = {
        "title": "测试网络攻击事件",
        "date": "2024-01-01",
        "description": "这是一个测试的网络攻击事件描述",
        "country": "US",
    }

    try:
        prompt = CYBERATTACK_PROMPT_TEMPLATE.format(
            title=test_attack["title"],
            date=test_attack["date"],
            summary=test_attack["description"],
            country=test_attack["country"],
        )

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的网络安全新闻编辑，擅长将技术信息转化为简洁易懂的新闻摘要。",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            timeout=LLM_TIMEOUT,
        )

        summary = response.choices[0].message.content.strip()
        print(f"\n   ✓ 网络攻击摘要生成成功:")
        print(f"     {summary}")

    except Exception as e:
        print(f"\n   ✗ 网络攻击摘要生成失败: {e}")
        return False

    print("\n=== LLM功能测试完成 ===")
    print("✓ 所有测试通过，LLM功能正常工作")
    return True


def show_setup_guide():
    """显示LLM设置指南"""
    print("\n=== LLM设置指南 ===")
    print("\n1. 安装依赖:")
    print("   pip install openai")

    print("\n2. 配置API密钥:")
    print("   方式一 - 环境变量（推荐）:")
    print("   export LLM_API_KEY='your-api-key-here'")
    print("   ")
    print("   方式二 - 配置文件:")
    print("   在config.py中设置: LLM_API_KEY = 'your-api-key-here'")

    print("\n3. 配置API端点:")
    print("   OpenAI官方: https://api.openai.com/v1")
    print("   其他兼容服务: 修改config.py中的LLM_BASE_URL")

    print("\n4. 选择模型:")
    print("   OpenAI: gpt-3.5-turbo, gpt-4, gpt-4-turbo")
    print("   其他服务: 根据服务商文档选择")

    print("\n5. 启用LLM:")
    print("   在config.py中设置: LLM_ENABLED = True")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_setup_guide()
    else:
        success = test_llm_functionality()
        if not success:
            print("\n" + "=" * 50)
            show_setup_guide()
