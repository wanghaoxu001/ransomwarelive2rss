#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
from datetime import datetime


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_section(title):
    """打印章节标题"""
    print(f"\n--- {title} ---")


def demo_api_status():
    """演示API状态"""
    print_section("服务状态")
    try:
        response = requests.get("http://localhost:15000/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 服务状态: {data['status']}")
            print(f"✓ 受害者数据: {data['victims_count']} 条")
            print(f"✓ 网络攻击数据: {data['cyberattacks_count']} 条")
            print(f"✓ 更新间隔: {data['config']['update_interval_hours']} 小时")
            print(f"✓ 目标地区: {', '.join(data['config']['target_countries'])}")
            print(f"✓ 目标行业: {data['config']['target_activity']}")
            if data["last_attack_update"]:
                print(f"✓ 最后更新: {data['last_attack_update']}")
        else:
            print(f"✗ 无法获取状态 (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ 连接失败: {e}")


def demo_news_data():
    """演示新闻数据"""
    print_section("最新威胁情报数据")
    try:
        response = requests.get("http://localhost:15000/api/news", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取到 {data['count']} 条威胁情报")

            if data["data"]:
                print("\n最新5条威胁情报:")
                for i, item in enumerate(data["data"][:5], 1):
                    print(f"\n{i}. 【{item['type']}】{item['title'][:50]}...")
                    print(f"   摘要: {item['summary'][:80]}...")
                    print(f"   时间: {item['created_at']}")
                    if item["country"]:
                        print(f"   地区: {item['country']}")
                    if item["group_name"]:
                        print(f"   组织: {item['group_name']}")
        else:
            print(f"✗ 无法获取数据 (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ 连接失败: {e}")


def demo_rss_feed():
    """演示RSS feed"""
    print_section("RSS Feed")
    try:
        response = requests.get("http://localhost:15000/rss", timeout=5)
        if response.status_code == 200:
            content = response.text
            print(f"✓ RSS Feed 生成成功")
            print(f"✓ Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"✓ 内容长度: {len(content)} 字符")

            # 显示RSS的前几行
            lines = content.split("\n")[:10]
            print("\nRSS Feed 预览:")
            for line in lines:
                if line.strip():
                    print(f"  {line.strip()}")
        else:
            print(f"✗ 无法获取RSS (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ 连接失败: {e}")


def demo_manual_update():
    """演示手动更新"""
    print_section("手动数据更新")
    try:
        print("正在触发手动更新...")
        response = requests.post("http://localhost:15000/api/update", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 更新成功: {data['message']}")
        else:
            print(f"✗ 更新失败 (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ 更新失败: {e}")


def check_service():
    """检查服务是否运行"""
    try:
        response = requests.get("http://localhost:15000/", timeout=3)
        return response.status_code == 200
    except:
        return False


def main():
    """主演示函数"""
    print_header("勒索软件威胁情报RSS服务演示")

    print("正在检查服务状态...")
    if not check_service():
        print("✗ 服务未运行，请先启动服务:")
        print("  python3 app.py")
        print("  或者使用: ./start.sh")
        return 1

    print("✓ 服务正在运行")

    # 演示各项功能
    demo_api_status()
    demo_news_data()
    demo_rss_feed()
    demo_manual_update()

    print_header("演示完成")
    print("RSS订阅地址: http://localhost:15000/rss")
    print("Web界面: http://localhost:15000/")
    print("筛选规则: 中国地区受害者 或 全球金融服务行业受害者")
    print("API文档: 查看README.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
