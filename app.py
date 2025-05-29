#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import json
import requests
import schedule
import time
import threading
from datetime import datetime, timezone, timedelta
from flask import Flask, Response, jsonify
from feedgen.feed import FeedGenerator
import logging

# 导入配置
from config import *

# 配置日志
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# LLM API支持
try:
    from openai import OpenAI

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("OpenAI库未安装，将使用固定模板生成摘要")

app = Flask(__name__)


class RansomwareRSSService:
    def __init__(self):
        self.init_database()
        self.llm_generator = LLMSummaryGenerator()

    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # 创建受害者表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS victims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                country TEXT,
                activity TEXT,
                group_name TEXT,
                discovered TEXT,
                published TEXT,
                description TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 创建网络攻击表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cyberattacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                date TEXT,
                description TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")

    def get_existing_urls(self, table_name):
        """获取数据库中已存在的URL列表"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT url FROM {table_name}")
        existing_urls = {row[0] for row in cursor.fetchall()}
        conn.close()
        return existing_urls

    def fetch_recent_victims(self):
        """获取最近的受害者数据"""
        try:
            # 获取已存在的URL
            existing_urls = self.get_existing_urls("victims")

            response = requests.get(
                f"{RANSOMWARE_API_BASE}/recentvictims", timeout=API_TIMEOUT
            )
            response.raise_for_status()
            all_victims = response.json()

            # 计算一周前的时间
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

            # 过滤掉一周前的数据和已存在的数据
            new_victims = []
            for victim in all_victims:
                url = victim.get("url")
                if not url or url in existing_urls:
                    continue
                
                # 解析discovered时间
                discovered = victim.get("discovered")
                if discovered:
                    try:
                        # 尝试解析时间字符串
                        if "T" in discovered:
                            victim_time = datetime.fromisoformat(discovered.replace("Z", "+00:00"))
                        else:
                            victim_time = datetime.fromisoformat(discovered + "+00:00")
                        
                        # 只保留一周内的数据
                        if victim_time >= one_week_ago:
                            new_victims.append(victim)
                    except:
                        # 如果时间解析失败，跳过该条数据
                        continue

            logger.info(
                f"获取到 {len(all_victims)} 条受害者数据，其中 {len(new_victims)} 条为新数据且在一周内"
            )
            return new_victims
        except Exception as e:
            logger.error(f"获取受害者数据失败: {e}")
            return []

    def fetch_recent_cyberattacks(self):
        """获取最近的网络攻击数据"""
        try:
            # 获取已存在的URL
            existing_urls = self.get_existing_urls("cyberattacks")

            response = requests.get(
                f"{RANSOMWARE_API_BASE}/recentcyberattacks", timeout=API_TIMEOUT
            )
            response.raise_for_status()
            all_attacks = response.json()

            # 计算一周前的时间
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

            # 过滤掉一周前的数据和已存在的数据
            new_attacks = []
            for attack in all_attacks:
                url = attack.get("url")
                if not url or url in existing_urls:
                    continue
                
                # 解析added时间
                added = attack.get("added")
                if added:
                    try:
                        # 尝试解析时间字符串
                        if "T" in added:
                            attack_time = datetime.fromisoformat(added.replace("Z", "+00:00"))
                        else:
                            attack_time = datetime.fromisoformat(added + "+00:00")
                        
                        # 只保留一周内的数据
                        if attack_time >= one_week_ago:
                            new_attacks.append(attack)
                    except:
                        # 如果时间解析失败，跳过该条数据
                        continue

            logger.info(
                f"获取到 {len(all_attacks)} 条网络攻击数据，其中 {len(new_attacks)} 条为新数据且在一周内"
            )
            return new_attacks
        except Exception as e:
            logger.error(f"获取网络攻击数据失败: {e}")
            return []

    def filter_china_financial_victims(self, victims_data):
        """筛选中国地区的受害者或金融服务行业的受害者"""
        filtered = []

        for victim in victims_data:
            country = victim.get("country", "").upper()
            activity = victim.get("activity", "")

            # 修改为OR逻辑：中国地区 或 金融服务行业
            if country in CHINA_COUNTRY_CODES or TARGET_ACTIVITY in activity:
                filtered.append(victim)

        return filtered

    def generate_victim_summary(self, victim):
        """为受害者生成新闻摘要"""
        # API v2字段映射
        company_name = victim.get("victim", "未知公司")  # v2使用victim字段
        country = victim.get("country", "未知")
        group_name = victim.get("group", "未知勒索软件组织")  # v2使用group字段
        discovered = victim.get("discovered", "未知时间")
        activity = victim.get("activity", "")
        description = victim.get("description", "")

        # 获取国家名称
        country_name = COUNTRY_NAMES.get(country, country)

        # 优先使用LLM生成摘要
        if self.llm_generator.enabled:
            try:
                prompt = VICTIM_PROMPT_TEMPLATE.format(
                    victim=company_name,
                    country=country_name,
                    activity=activity or "未知行业",
                    group=group_name,
                    discovered=discovered,
                    description=description or "暂无详细描述",
                )

                llm_summary = self.llm_generator.generate_summary(prompt)
                if llm_summary:
                    logger.debug(f"使用LLM生成受害者摘要: {company_name}")
                    return llm_summary
                else:
                    logger.warning(f"LLM生成摘要失败，回退到固定模板: {company_name}")
            except Exception as e:
                logger.error(f"LLM摘要生成异常: {e}")

        # 回退到固定模板
        # 根据行业生成不同的描述
        if TARGET_ACTIVITY in activity:
            industry_desc = "金融服务机构"
            risk_desc = "可能涉及敏感的客户数据和财务信息"
        else:
            # 简化行业名称
            if activity:
                industry_desc = f"{activity}行业企业"
            else:
                industry_desc = "企业"
            risk_desc = "可能涉及重要的业务数据和信息"

        # 生成摘要
        if country in CHINA_COUNTRY_CODES:
            summary = f"【勒索】{country_name}{industry_desc}{company_name}遭到{group_name}勒索软件组织攻击。"
        else:
            summary = f"【勒索】{industry_desc}{company_name}遭到{group_name}勒索软件组织攻击。"

        summary += f"该攻击于{discovered}被发现，{risk_desc}。"
        summary += f"此次攻击再次凸显了网络安全威胁的严重性，相关机构应加强防护措施。"

        logger.debug(f"使用固定模板生成受害者摘要: {company_name}")
        return summary

    def generate_cyberattack_summary(self, attack):
        """为网络攻击生成新闻摘要"""
        title = attack.get("title", "网络攻击事件")
        date = attack.get("date", "未知时间")
        description = attack.get("description", "")
        country = attack.get("country", "")

        # 优先使用LLM生成摘要
        if self.llm_generator.enabled:
            try:
                prompt = CYBERATTACK_PROMPT_TEMPLATE.format(
                    title=title,
                    date=date,
                    summary=description or "暂无详细描述",
                    country=country or "未知地区",
                )

                llm_summary = self.llm_generator.generate_summary(prompt)
                if llm_summary:
                    logger.debug(f"使用LLM生成网络攻击摘要: {title}")
                    return llm_summary
                else:
                    logger.warning(f"LLM生成摘要失败，回退到固定模板: {title}")
            except Exception as e:
                logger.error(f"LLM摘要生成异常: {e}")

        # 回退到固定模板
        # 构建日期信息
        date_info = f"该事件发生于{date}，" if date != "未知时间" else ""

        # 构建描述信息
        if description:
            description_info = f"据报告，{description[:100]}..."
        else:
            description_info = "详细信息正在调查中。"

        # 使用模板生成摘要
        summary = CYBERATTACK_SUMMARY_TEMPLATE.format(
            title=title, date_info=date_info, description_info=description_info
        )

        logger.debug(f"使用固定模板生成网络攻击摘要: {title}")
        return summary

    def save_new_victims(self, victims):
        """保存新的受害者数据"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        new_count = 0

        for victim in victims:
            # API v2字段映射
            url = victim.get("url", "")  # v2使用url字段
            if not url:
                continue

            try:
                summary = self.generate_victim_summary(victim)

                # 使用INSERT OR IGNORE避免重复插入
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO victims (url, title, country, activity, group_name, discovered, published, description, summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        url,
                        victim.get("victim", ""),  # v2使用victim字段作为title
                        victim.get("country", ""),
                        victim.get("activity", ""),
                        victim.get("group", ""),  # v2使用group字段
                        victim.get("discovered", ""),
                        victim.get(
                            "attackdate", ""
                        ),  # v2使用attackdate字段作为published
                        victim.get("description", ""),
                        summary,
                    ),
                )

                # 检查是否真的插入了新记录
                if cursor.rowcount > 0:
                    new_count += 1

            except Exception as e:
                logger.warning(f"保存受害者记录失败 (URL: {url}): {e}")
                continue

        conn.commit()
        conn.close()
        logger.info(f"保存了 {new_count} 条新的受害者记录")
        return new_count

    def save_new_cyberattacks(self, attacks):
        """保存新的网络攻击数据"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        new_count = 0

        for attack in attacks:
            url = attack.get("url", "")
            if not url:
                continue

            try:
                summary = self.generate_cyberattack_summary(attack)

                # 使用INSERT OR IGNORE避免重复插入
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO cyberattacks (url, title, date, description, summary)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        url,
                        attack.get("title", ""),
                        attack.get("date", ""),
                        attack.get("description", ""),
                        summary,
                    ),
                )

                # 检查是否真的插入了新记录
                if cursor.rowcount > 0:
                    new_count += 1

            except Exception as e:
                logger.warning(f"保存网络攻击记录失败 (URL: {url}): {e}")
                continue

        conn.commit()
        conn.close()
        logger.info(f"保存了 {new_count} 条新的网络攻击记录")
        return new_count

    def get_recent_news(self, limit=None):
        """获取最近的新闻条目"""
        if limit is None:
            limit = RSS_MAX_ITEMS

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # 合并受害者和网络攻击数据
        cursor.execute(
            """
            SELECT 'victim' as type, url, title, summary, created_at, country, group_name
            FROM victims
            UNION ALL
            SELECT 'cyberattack' as type, url, title, summary, created_at, '', ''
            FROM cyberattacks
            ORDER BY created_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        results = cursor.fetchall()
        conn.close()

        news_items = []
        for row in results:
            news_items.append(
                {
                    "type": row[0],
                    "url": row[1],
                    "title": row[2],
                    "summary": row[3],
                    "created_at": row[4],
                    "country": row[5],
                    "group_name": row[6],
                }
            )

        return news_items

    def generate_rss_feed(self):
        """生成RSS feed"""
        fg = FeedGenerator()
        fg.title(RSS_TITLE)
        fg.link(href=f"http://localhost:{PORT}", rel="alternate")
        fg.description(RSS_DESCRIPTION)
        fg.language(RSS_LANGUAGE)
        fg.lastBuildDate(datetime.now(timezone.utc))
        fg.generator(RSS_GENERATOR)

        news_items = self.get_recent_news()

        for item in news_items:
            fe = fg.add_entry()

            # 根据类型设置标题前缀
            if item["type"] == "victim":
                title_prefix = "【勒索】"
                if item["country"]:
                    country_name = COUNTRY_NAMES.get(item["country"], item["country"])
                    title_prefix += f"[{country_name}] "
            else:
                title_prefix = "【网络安全事件】"

            fe.title(f"{title_prefix}{item['title']}")
            fe.link(href=item["url"])
            fe.description(item["summary"])
            fe.guid(item["url"])

            # 处理时间格式
            try:
                if "T" in item["created_at"]:
                    pub_date = datetime.fromisoformat(
                        item["created_at"].replace("Z", "+00:00")
                    )
                else:
                    pub_date = datetime.fromisoformat(item["created_at"] + "+00:00")
                fe.pubDate(pub_date)
            except:
                fe.pubDate(datetime.now(timezone.utc))

        return fg.rss_str(pretty=True)

    def update_data(self):
        """更新数据的定时任务"""
        start_time = datetime.now()
        logger.info(f"开始更新勒索软件数据... (时间: {start_time.isoformat()})")

        try:
            # 获取受害者数据
            logger.info("正在获取受害者数据...")
            victims_data = self.fetch_recent_victims()
            if victims_data:
                logger.info(f"获取到 {len(victims_data)} 条受害者原始数据")
                filtered_victims = self.filter_china_financial_victims(victims_data)
                logger.info(f"筛选后的受害者数据: {len(filtered_victims)} 条")
                saved_victims = self.save_new_victims(filtered_victims)
                logger.info(f"保存了 {saved_victims} 条新的受害者记录")
            else:
                logger.warning("未获取到受害者数据")

            # 获取网络攻击数据
            logger.info("正在获取网络攻击数据...")
            attacks_data = self.fetch_recent_cyberattacks()
            if attacks_data:
                logger.info(f"获取到 {len(attacks_data)} 条网络攻击原始数据")
                saved_attacks = self.save_new_cyberattacks(attacks_data)
                logger.info(f"保存了 {saved_attacks} 条新的网络攻击记录")
            else:
                logger.warning("未获取到网络攻击数据")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"数据更新完成 (耗时: {duration:.2f}秒, 完成时间: {end_time.isoformat()})")
            
        except Exception as e:
            logger.error(f"数据更新过程中发生异常: {e}", exc_info=True)


class LLMSummaryGenerator:
    """LLM摘要生成器"""

    def __init__(self):
        self.client = None
        self.enabled = False
        self.init_llm_client()

    def init_llm_client(self):
        """初始化LLM客户端"""
        if not LLM_AVAILABLE or not LLM_ENABLED:
            logger.info("LLM摘要生成已禁用，使用固定模板")
            return

        # 从环境变量或配置文件获取API密钥
        api_key = os.getenv("LLM_API_KEY") or LLM_API_KEY
        if not api_key:
            logger.warning("未设置LLM API密钥，将使用固定模板生成摘要")
            return

        try:
            self.client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL)
            self.enabled = True
            logger.info(f"LLM客户端初始化成功，使用模型: {LLM_MODEL}")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            self.enabled = False

    def generate_summary(self, prompt):
        """使用LLM生成摘要"""
        if not self.enabled or not self.client:
            return None

        try:
            response = self.client.chat.completions.create(
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
            logger.debug(f"LLM生成摘要成功: {summary[:50]}...")
            return summary

        except Exception as e:
            logger.error(f"LLM生成摘要失败: {e}")
            return None


# 创建服务实例
rss_service = RansomwareRSSService()


@app.route("/")
def index():
    """主页"""
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{RSS_TITLE}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .endpoint {{ background: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .code {{ background: #f0f0f0; padding: 10px; border-radius: 3px; font-family: monospace; }}
            .status {{ background: #e8f8e8; padding: 10px; border-radius: 3px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{RSS_TITLE}</h1>
            <p>{RSS_DESCRIPTION}</p>
        </div>
        
        <h2>服务说明</h2>
        <ul>
            <li>每{UPDATE_INTERVAL_HOURS}小时自动调用Ransomware.live API获取最新数据</li>
            <li>筛选中国地区（{', '.join(CHINA_COUNTRY_CODES)}）受害者或全球{TARGET_ACTIVITY}行业受害者</li>
            <li>收集全球网络攻击事件信息</li>
            <li>{'使用LLM智能生成中文新闻摘要' if LLM_ENABLED and rss_service.llm_generator.enabled else '使用固定模板生成中文新闻摘要'}</li>
            <li>通过RSS格式输出威胁情报</li>
        </ul>
        
        <div class="status">
            <h3>当前配置</h3>
            <ul>
                <li>LLM摘要生成: {'✓ 已启用 (' + LLM_MODEL + ')' if LLM_ENABLED and rss_service.llm_generator.enabled else '✗ 已禁用（使用固定模板）'}</li>
                <li>更新频率: 每{UPDATE_INTERVAL_HOURS}小时</li>
                <li>RSS最大条目: {RSS_MAX_ITEMS}</li>
            </ul>
        </div>
        
        <h2>API端点</h2>
        <div class="endpoint">
            <h3>RSS Feed</h3>
            <div class="code">GET /rss</div>
            <p>获取RSS格式的威胁情报feed</p>
        </div>
        
        <div class="endpoint">
            <h3>JSON格式数据</h3>
            <div class="code">GET /api/news</div>
            <p>获取JSON格式的最新威胁情报</p>
        </div>
        
        <div class="endpoint">
            <h3>手动更新数据</h3>
            <div class="code">POST /api/update</div>
            <p>手动触发数据更新</p>
        </div>
        
        <div class="endpoint">
            <h3>服务状态</h3>
            <div class="code">GET /api/status</div>
            <p>查看服务运行状态</p>
        </div>
        
        <h2>RSS订阅地址</h2>
        <div class="code">http://localhost:{PORT}/rss</div>
        
        <p><small>数据来源：<a href="https://www.ransomware.live" target="_blank">Ransomware.live</a></small></p>
    </body>
    </html>
    """
    return html


@app.route("/rss")
def rss_feed():
    """RSS feed端点"""
    try:
        rss_content = rss_service.generate_rss_feed()
        return Response(rss_content, mimetype="application/rss+xml; charset=utf-8")
    except Exception as e:
        logger.error(f"生成RSS feed失败: {e}")
        return Response("RSS生成失败", status=500)


@app.route("/api/news")
def api_news():
    """JSON格式的新闻API"""
    try:
        news_items = rss_service.get_recent_news()
        return jsonify(
            {"status": "success", "count": len(news_items), "data": news_items}
        )
    except Exception as e:
        logger.error(f"获取新闻数据失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/update", methods=["POST"])
def api_update():
    """手动更新数据"""
    try:
        rss_service.update_data()
        return jsonify({"status": "success", "message": "数据更新完成"})
    except Exception as e:
        logger.error(f"手动更新失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/status")
def api_status():
    """服务状态"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM victims")
        victims_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM cyberattacks")
        attacks_count = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(created_at) FROM victims")
        last_victim_update = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(created_at) FROM cyberattacks")
        last_attack_update = cursor.fetchone()[0]

        conn.close()

        return jsonify(
            {
                "status": "running",
                "victims_count": victims_count,
                "cyberattacks_count": attacks_count,
                "last_victim_update": last_victim_update,
                "last_attack_update": last_attack_update,
                "current_time": datetime.now().isoformat(),
                "config": {
                    "update_interval_hours": UPDATE_INTERVAL_HOURS,
                    "target_countries": CHINA_COUNTRY_CODES,
                    "target_activity": TARGET_ACTIVITY,
                    "rss_max_items": RSS_MAX_ITEMS,
                    "llm_enabled": LLM_ENABLED and rss_service.llm_generator.enabled,
                    "llm_model": LLM_MODEL if LLM_ENABLED else None,
                    "llm_available": LLM_AVAILABLE,
                },
            }
        )
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/scheduler")
def api_scheduler():
    """定时任务状态"""
    try:
        scheduler_info = {
            "jobs_count": len(schedule.jobs),
            "jobs": []
        }
        
        for job in schedule.jobs:
            job_info = {
                "interval": job.interval,
                "unit": job.unit,
                "next_run": job.next_run.isoformat() if job.next_run else None,
                "job_func": str(job.job_func),
                "last_run": getattr(job, 'last_run', None)
            }
            scheduler_info["jobs"].append(job_info)
        
        return jsonify({
            "status": "success",
            "scheduler_info": scheduler_info,
            "current_time": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取定时任务状态失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def run_scheduler():
    """运行定时任务"""
    logger.info("定时任务线程启动")
    
    # 根据配置设置更新间隔
    if UPDATE_INTERVAL_HOURS == 1:
        schedule.every().hour.do(rss_service.update_data)
        logger.info("定时任务配置：每小时执行一次")
    else:
        schedule.every(UPDATE_INTERVAL_HOURS).hours.do(rss_service.update_data)
        logger.info(f"定时任务配置：每{UPDATE_INTERVAL_HOURS}小时执行一次")

    # 启动时立即执行一次更新
    logger.info("执行启动时的初始数据更新")
    try:
        rss_service.update_data()
        logger.info("初始数据更新完成")
    except Exception as e:
        logger.error(f"初始数据更新失败: {e}")

    logger.info("开始定时任务循环")
    loop_count = 0
    while True:
        try:
            loop_count += 1
            if loop_count % 60 == 0:  # 每小时记录一次心跳
                logger.info(f"定时任务线程运行正常，循环次数: {loop_count}")
            
            # 检查是否有待执行的任务
            pending_jobs = schedule.jobs
            if pending_jobs:
                next_run = min(job.next_run for job in pending_jobs) if pending_jobs else None
                if loop_count % 60 == 0:  # 每小时记录一次
                    logger.info(f"下次执行时间: {next_run}")
            
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
        except Exception as e:
            logger.error(f"定时任务循环异常: {e}")
            time.sleep(60)


if __name__ == "__main__":
    # 启动定时任务线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    logger.info(f"{RSS_TITLE}启动")
    logger.info(f"服务地址: http://{HOST}:{PORT}")
    logger.info(f"RSS订阅地址: http://{HOST}:{PORT}/rss")

    app.run(host=HOST, port=PORT, debug=DEBUG)
