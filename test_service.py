#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys


def test_api_endpoint(url, method="GET", expected_status=200):
    """测试API端点"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=30)

        print(f"测试 {method} {url}")
        print(f"状态码: {response.status_code}")

        if response.status_code == expected_status:
            print("✓ 测试通过")
            return True
        else:
            print("✗ 测试失败")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_rss_feed(url):
    """测试RSS feed格式"""
    try:
        response = requests.get(url, timeout=10)
        print(f"测试RSS Feed: {url}")
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")

        if response.status_code == 200:
            content = response.text
            if "<?xml" in content and "<rss" in content:
                print("✓ RSS格式正确")
                return True
            else:
                print("✗ RSS格式错误")
                return False
        else:
            print("✗ RSS获取失败")
            return False

    except Exception as e:
        print(f"✗ RSS测试失败: {e}")
        return False


def test_json_api(url):
    """测试JSON API"""
    try:
        response = requests.get(url, timeout=10)
        print(f"测试JSON API: {url}")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if "status" in data and "data" in data:
                print(f"✓ JSON格式正确，包含 {data.get('count', 0)} 条数据")
                return True
            else:
                print("✗ JSON格式错误")
                return False
        else:
            print("✗ JSON API获取失败")
            return False

    except Exception as e:
        print(f"✗ JSON API测试失败: {e}")
        return False


def main():
    """主测试函数"""
    base_url = "http://localhost:15000"

    print("勒索软件威胁情报RSS服务测试")
    print("=" * 40)

    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)

    tests = [
        ("主页", lambda: test_api_endpoint(f"{base_url}/")),
        ("RSS Feed", lambda: test_rss_feed(f"{base_url}/rss")),
        ("JSON API", lambda: test_json_api(f"{base_url}/api/news")),
        ("状态API", lambda: test_json_api(f"{base_url}/api/status")),
        (
            "手动更新",
            lambda: test_api_endpoint(f"{base_url}/api/update", method="POST"),
        ),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- 测试: {test_name} ---")
        if test_func():
            passed += 1
        print()

    print("=" * 40)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("✓ 所有测试通过！服务运行正常。")
        return 0
    else:
        print("✗ 部分测试失败，请检查服务状态。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
