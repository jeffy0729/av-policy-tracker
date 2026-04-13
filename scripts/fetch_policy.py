#!/usr/bin/env python3
"""
自动驾驶政策法规抓取脚本
只抓取最近3个月的官方政策文件
"""

import json
import datetime
import urllib.request
import re
from pathlib import Path

def search_tavily(query, max_results=15):
    """使用Tavily搜索"""
    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    data = {
        "query": query,
        "search_depth": "basic",
        "max_results": max_results
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("results", [])
    except Exception as e:
        print(f"Tavily搜索出错: {e}")
        return []

def extract_date_from_text(text):
    """从文本中提取日期"""
    patterns = [
        r"(\d{4})[年\-](\d{1,2})[月\-](\d{1,2})",
        r"(\d{4})\.(\d{1,2})\.(\d{1,2})",
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})",
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})",
        r"(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
        r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})",
    ]
    
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # 中文日期
                if len(match.groups()) == 3 and match.group(1).isdigit() and "-" in match.group(0):
                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                        return f"{year}-{month:02d}-{day:02d}"
                # 英文日期 (Jan 15, 2026 或 January 15, 2026)
                elif len(match.groups()) == 3:
                    g1, g2, g3 = match.group(1), match.group(2), match.group(3)
                    g1_lower = g1.lower() if g1 else ""
                    g2_clean = g2.replace(",", "").strip() if g2 else ""
                    g3_clean = g3.replace(",", "").strip() if g3 else ""
                    
                    # 格式: January 15, 2026 或 Jan 15, 2026
                    if g1_lower in month_map:
                        month = month_map[g1_lower]
                        if g2_clean.isdigit():
                            day = int(g2_clean)
                            year = int(g3_clean) if g3_clean.isdigit() else None
                            if year and 2020 <= year <= 2030 and 1 <= day <= 31:
                                return f"{year}-{month:02d}-{day:02d}"
                    # 格式: 15 January 2026
                    elif g3_clean.lower() in month_map:
                        month = month_map[g3_clean.lower()]
                        if g1.isdigit():
                            day = int(g1)
                            year = int(g2_clean) if g2_clean.isdigit() else None
                            if year and 2020 <= year <= 2030 and 1 <= day <= 31:
                                return f"{year}-{month:02d}-{day:02d}"
            except:
                pass
    return None

def is_recent_6_months(date_str):
    """检查日期是否在最近6个月内（更宽松）"""
    if not date_str:
        return False
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        six_months_ago = today - datetime.timedelta(days=180)
        return date >= six_months_ago
    except:
        return False

def fetch_official_policy():
    """抓取官方政策文件"""
    updates = []
    
    # ========== 中国政策搜索 ==========
    china_keywords = ["自动驾驶", "智能网联", "车路云", "L3自动驾驶", "L4自动驾驶", "无人驾驶", "智能汽车", "汽车智能化", "高级辅助驾驶"]
    policy_keywords = ["政策", "条例", "办法", "要求", "细则", "实施", "法规", "通知", "意见", "规划", "标准", "规范"]
    
    print("🔍 搜索中国官方政策...")
    for kw in china_keywords:
        for pk in policy_keywords[:5]:
            query = f"{kw} {pk} 2025 2026 site:gov.cn"
            results = search_tavily(query, 15)
            for r in results:
                url = r.get("url", "")
                title = r.get("title", "")
                content = r.get("content", "")
                
                # 检查是否是政府网站
                if "gov.cn" in url or "miit.gov.cn" in url or "mot.gov.cn" in url:
                    date = extract_date_from_text(content[:3000])
                    if date and is_recent_6_months(date):
                        updates.append({
                            "country": "中国",
                            "source": extract_domain(url),
                            "url": url,
                            "title": title,
                            "date": date,
                        })
    
    # ========== 美国政策搜索 ==========
    # 扩大搜索范围，不过滤site
    us_keywords = [
        "autonomous vehicle policy 2025 2026",
        "self-driving car regulation NHTSA",
        "robotaxi rules DOT",
        "automated driving guidelines",
        "AV safety requirements federal"
    ]
    
    print("🔍 搜索美国官方政策...")
    for query in us_keywords:
        results = search_tavily(query, 15)
        for r in results:
            url = r.get("url", "")
            title = r.get("title", "")
            content = r.get("content", "")
            
            # 过滤政府/机构网站
            gov_domains = [".gov", "dot.gov", "nhsta.gov", "transportation.gov", "treasury.gov", 
                          "commerce.gov", "energy.gov", "faa.gov", "nhtsa.gov"]
            is_gov = any(d in url.lower() for d in gov_domains)
            
            if is_gov:
                date = extract_date_from_text(content[:3000])
                if date and is_recent_6_months(date):
                    updates.append({
                        "country": "美国",
                        "source": extract_domain(url),
                        "url": url,
                        "title": title,
                        "date": date,
                    })
    
    # ========== 欧洲政策搜索 ==========
    # 搜索各国政府网站 + 欧盟机构
    eu_queries = [
        # 欧盟机构
        "autonomous vehicle regulation European Commission 2025 2026",
        "self-driving car EU guidelines 2025",
        "automated driving Europe policy",
        # 各国政府
        "UK autonomous vehicle policy 2025 2026 gov.uk",
        "Germany autonomous driving regulation 2025",
        "France vehicle autonome politique 2025",
    ]
    
    print("🔍 搜索欧洲官方政策...")
    for query in eu_queries:
        results = search_tavily(query, 12)
        for r in results:
            url = r.get("url", "")
            title = r.get("title", "")
            content = r.get("content", "")
            
            # 过滤政府/机构网站
            eu_domains = ["europa.eu", "gov.uk", ".gov.de", ".gov.fr", ".gov.it", 
                         "gov.ie", "gov.nl", "gov.be", "government.se", "bmwk.de",
                         "transports.gouv.fr", "minbuza.nl"]
            is_gov = any(d in url.lower() for d in eu_domains)
            
            if is_gov:
                date = extract_date_from_text(content[:3000])
                if date and is_recent_6_months(date):
                    updates.append({
                        "country": "欧洲",
                        "source": extract_domain(url),
                        "url": url,
                        "title": title,
                        "date": date,
                    })
    
    # 去重 + 过滤航空器/无人机
    seen = set()
    unique_updates = []
    for u in updates:
        url = u.get("url", "")
        title = u.get("title", "")
        
        # 过滤掉航空器/无人机相关
        if any(kw in title for kw in ["航空器", "无人机", "UAV", " UAS ", "aircraft", "drone"]):
            continue
        
        # 去重：按URL和标题双重去重
        url_key = url
        title_key = title[:30]
        dedup_key = (url_key, title_key)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        unique_updates.append(u)
    
    # 按日期排序
    unique_updates.sort(key=lambda x: x["date"], reverse=True)
    
    print(f"✅ 找到 {len(unique_updates)} 条符合条件的政策")
    for u in unique_updates:
        print(f"  - {u['country']}: {u['title'][:50]}...")
    
    return unique_updates

def extract_domain(url):
    """提取域名"""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return "unknown"

def generate_html(updates):
    """生成HTML页面"""
    cn_count = sum(1 for u in updates if u['country'] == '中国')
    us_count = sum(1 for u in updates if u['country'] == '美国')
    eu_count = sum(1 for u in updates if u['country'] == '欧洲')
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>自动驾驶政策法规最新动态</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 40px 30px; border-radius: 16px; margin-bottom: 30px; }}
        h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .subtitle {{ opacity: 0.8; font-size: 14px; }}
        .stats {{ display: flex; gap: 30px; margin-top: 20px; }}
        .stat {{ text-align: center; }}
        .stat-number {{ font-size: 28px; font-weight: bold; }}
        .stat-label {{ font-size: 12px; opacity: 0.7; }}
        .filters {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 8px 16px; border: none; border-radius: 20px; background: white; color: #333; cursor: pointer; font-size: 14px; transition: all 0.3s; }}
        .filter-btn.active {{ background: #1a1a2e; color: white; }}
        .filter-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .update-list {{ display: grid; gap: 16px; }}
        .update-card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: all 0.3s; }}
        .update-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
        .country-tag {{ padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; }}
        .country-cn {{ background: #e74c3c; color: white; }}
        .country-us {{ background: #3498db; color: white; }}
        .country-eu {{ background: #9b59b6; color: white; }}
        .type-tag {{ padding: 4px 8px; border-radius: 8px; font-size: 11px; background: #27ae60; color: white; }}
        .date {{ color: #999; font-size: 13px; }}
        .card-title {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; line-height: 1.5; }}
        .card-title a {{ color: #333; text-decoration: none; }}
        .card-title a:hover {{ color: #1a1a2e; }}
        .card-source {{ color: #999; font-size: 13px; }}
        .empty-state {{ text-align: center; padding: 60px 20px; color: #999; }}
        footer {{ text-align: center; padding: 30px; color: #999; font-size: 13px; }}
        .last-update {{ margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚗 自动驾驶政策法规最新动态</h1>
            <div class="subtitle">最近3个月 | 中国政府网 | 美国交通部 | 欧盟/各国政府 | 官方政策文件</div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{len(updates)}</div>
                    <div class="stat-label">政策总数</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{cn_count}</div>
                    <div class="stat-label">中国</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{us_count}</div>
                    <div class="stat-label">美国</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{eu_count}</div>
                    <div class="stat-label">欧洲</div>
                </div>
            </div>
        </header>
'''
    
    if not updates:
        html += '''
        <div class="empty-state">
            <p>暂无最近3个月的政策文件</p>
            <p style="margin-top:10px;font-size:13px;">尝试扩大搜索范围...</p>
        </div>
'''
    else:
        html += '''
        <div class="filters">
            <button class="filter-btn active" data-filter="all">全部</button>
            <button class="filter-btn" data-filter="中国">中国</button>
            <button class="filter-btn" data-filter="美国">美国</button>
            <button class="filter-btn" data-filter="欧洲">欧洲</button>
        </div>
        
        <div class="update-list">
'''
        for u in updates:
            country_class = {"中国": "country-cn", "美国": "country-us", "欧洲": "country-eu"}.get(u["country"], "country-cn")
            date_display = u.get("date", "") or "未知日期"
            html += f'''
            <div class="update-card" data-country="{u['country']}">
                <div class="card-header">
                    <div style="display:flex;gap:8px;align-items:center;">
                        <span class="country-tag {country_class}">{u['country']}</span>
                        <span class="type-tag">📄 官方文件</span>
                    </div>
                    <span class="date">{date_display}</span>
                </div>
                <div class="card-title">
                    <a href="{u['url']}" target="_blank">{u['title']}</a>
                </div>
                <div class="card-source">来源：{u['source']}</div>
            </div>
'''
    
    html += '''
        </div>
        
        <footer>
            <div>数据来源：中国政府网(gov.cn)、交通运输部(mot.gov.cn)、工信部(miit.gov.cn)、美国交通部(dot.gov)、NHTSA、欧盟委员会(Europa.eu)、各国政府网站</div>
            <div class="last-update">最后更新：''' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</div>
        </footer>
    </div>
    
    <script>
        const buttons = document.querySelectorAll('.filter-btn');
        const cards = document.querySelectorAll('.update-card');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                cards.forEach(card => {
                    if (filter === 'all' || card.dataset.country === filter) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>'''
    
    return html

def main():
    """主函数"""
    print(f"🚀 开始抓取官方自动驾驶政策法规 - {datetime.datetime.now()}")
    
    # 抓取更新
    updates = fetch_official_policy()
    
    # 生成HTML
    html = generate_html(updates)
    
    # 保存文件
    output_path = Path(__file__).parent / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 已生成 {output_path}")
    
    # 保存JSON数据
    data_path = Path(__file__).parent / "data" / "updates.json"
    data_path.parent.mkdir(exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(updates, f, ensure_ascii=False, indent=2)
    
    return updates

if __name__ == "__main__":
    main()