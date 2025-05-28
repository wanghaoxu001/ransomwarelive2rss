#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import *
import requests


def test_api_fix():
    """测试API修复是否成功"""
    print("测试API v2端点...")

    try:
        # 测试受害者数据
        print("\n--- 测试受害者数据 ---")
        response = requests.get(
            f"{RANSOMWARE_API_BASE}/recentvictims", timeout=API_TIMEOUT
        )
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"数据条目数: {len(data)}")

            if data:
                victim = data[0]
                print(f"第一条数据字段: {list(victim.keys())}")
                print(f'受害者: {victim.get("victim", "N/A")}')
                print(f'国家: {victim.get("country", "N/A")}')
                print(f'行业: {victim.get("activity", "N/A")}')
                print(f'组织: {victim.get("group", "N/A")}')

                # 测试筛选逻辑
                china_victims = []
                financial_victims = []
                for v in data[:10]:  # 只测试前10条
                    country = v.get("country", "").upper()
                    activity = v.get("activity", "")

                    if country in CHINA_COUNTRY_CODES:
                        china_victims.append(v)
                    if TARGET_ACTIVITY in activity:
                        financial_victims.append(v)

                print(f"前10条中中国地区受害者: {len(china_victims)}")
                print(f"前10条中金融服务受害者: {len(financial_victims)}")

        # 测试网络攻击数据
        print("\n--- 测试网络攻击数据 ---")
        response = requests.get(
            f"{RANSOMWARE_API_BASE}/recentcyberattacks", timeout=API_TIMEOUT
        )
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"数据条目数: {len(data)}")

            if data:
                attack = data[0]
                print(f"第一条数据字段: {list(attack.keys())}")
                print(f'标题: {attack.get("title", "N/A")}')
                print(f'日期: {attack.get("date", "N/A")}')
                print(f'URL: {attack.get("url", "N/A")}')

        print("\n✓ API调用测试成功")
        return True

    except Exception as e:
        print(f"\n✗ API调用失败: {e}")
        return False


if __name__ == "__main__":
    test_api_fix()
