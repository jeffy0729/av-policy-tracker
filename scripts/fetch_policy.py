#!/usr/bin/env python3
"""
自动驾驶政策法规抓取脚本 - 官方文件版
只抓取政府部門官方发布的政策文件和法规
"""

import json
import datetime
import urllib.request
import urllib.parse
from pathlib import Path

def search_tavily(query, max_results=10):
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

def fetch_official_policy():
    """抓取官方政策文件"""
    updates = []
    
    # 中国官方政策搜索 - 使用site限定政府网站
    china_queries = [
        "site:gov.cn 自动驾驶 政策 2026",
        "site:gov.cn 智能网联汽车 管理条例",
        "site:miit.gov.cn 自动驾驶系统安全要求 2026",
        "site:mot.gov.cn 自动驾驶 法规 2026",
        "site:122.gov.cn 自动驾驶 管理规定",
        "site:gov.cn 车路云一体化 试点 通知",
    ]
    
    print("🔍 搜索中国官方政策...")
    for query in china_queries:
        results = search_tavily(query, 5)
        for r in results:
            url = r.get("url", "")
            # 只保留政府域名
            if "gov.cn" in url or "miit.gov.cn" in url or "mot.gov.cn" in url or "122.gov.cn" in url:
                updates.append({
                    "country": "中国",
                    "source": extract_domain(url),
                    "url": url,
                    "title": r.get("title", ""),
                    "date": datetime.date.today().isoformat(),
                    "type": "官方文件"
                })
    
    # 美国官方政策搜索
    us_queries = [
        "site:dot.gov autonomous vehicle policy 2026",
        "site:nhtsa.gov self-driving car regulation 2026",
        "site:transportation.gov autonomous driving guidelines 2026",
        "site:ca.gov DMV autonomous vehicle 2026",
    ]
    
    print("🔍 搜索美国官方政策...")
    for query in us_queries:
        results = search_tavily(query, 5)
        for r in results:
            url = r.get("url", "")
            if "dot.gov" in url or "nhtsa.gov" in url or ".gov" in url:
                updates.append({
                    "country": "美国",
                    "source": extract_domain(url),
                    "url": url,
                    "title": r.get("title", ""),
                    "date": datetime.date.today().isoformat(),
                    "type": "官方文件"
                })
    
    # 联合国/欧盟官方政策
    global_queries = [
        "site:un.org autonomous vehicle regulation 2026",
        "site:unece.org autonomous vehicle policy",
    ]
    
    print("🔍 搜索国际官方政策...")
    for query in global_queries:
        results = search_tavily(query, 3)
        for r in results:
            url = r.get("url", "")
            if "un.org" in url or "unece.org" in url or ".gov" in url or ".int" in url:
                updates.append({
                    "country": "全球",
                    "source": extract_domain(url),
                    "url": url,
                    "title": r.get("title", ""),
                    "date": datetime.date.today().isoformat(),
                    "type": "官方文件"
                })
    
    # 去重
    seen = set()
    unique_updates = []
    for u in updates:
        key = u["url"]
        if key not in seen:
            seen.add(key)
            unique_updates.append(u)
    
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
        .country-global {{ background: #9b59b6; color: white; }}
        .type-tag {{ padding: 4px 8px; border-radius: 8px; font-size: 11px; background: #27ae60; color: white; }}
        .date {{ color: #999; font-size: 13px; }}
        .card-title {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; line-height: 1.5; }}
        .card-title a {{ color: #333; text-decoration: none; }}
        .card-title a:hover {{ color: #1a1a2e; }}
        .card-source {{ color: #666; font-size: 13px; }}
        .empty-state {{ text-align: center; padding: 60px 20px; color: #999; }}
        .empty-state svg {{ width: 64px; height: 64px; margin-bottom: 20px; opacity: 0.5; }}
        footer {{ text-align: center; padding: 30px; color: #999; font-size: 13px; }}
        .last-update {{ margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚗 自动驾驶政策法规最新动态</h1>
            <div class="subtitle">中国政府网 | 交通运输部 | 工信部 | 美国交通部 | 官方政策文件</div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{len(updates)}</div>
                    <div class="stat-label">今日更新</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{sum(1 for u in updates if u['country'] == '中国')}</div>
                    <div class="stat-label">中国</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{sum(1 for u in updates if u['country'] == '美国')}</div>
                    <div class="stat-label">美国</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{sum(1 for u in updates if u['country'] == '全球')}</div>
                    <div class="stat-label">全球</div>
                </div>
            </div>
        </header>
'''
    
    if not updates:
        html += '''
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <p>今日暂无官方政策文件更新</p>
        </div>
'''
    else:
        html += '''
        <div class="filters">
            <button class="filter-btn active" data-filter="all">全部</button>
            <button class="filter-btn" data-filter="中国">中国</button>
            <button class="filter-btn" data-filter="美国">美国</button>
            <button class="filter-btn" data-filter="全球">全球</button>
        </div>
        
        <div class="update-list">
'''
        for u in updates:
            country_class = "country-cn" if u["country"] == "中国" else ("country-us" if u["country"] == "美国" else "country-global")
            html += f'''
            <div class="update-card" data-country="{u['country']}">
                <div class="card-header">
                    <div style="display:flex;gap:8px;align-items:center;">
                        <span class="country-tag {country_class}">{u['country']}</span>
                        <span class="type-tag">📄 官方文件</span>
                    </div>
                    <span class="date">{u['date']}</span>
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
            <div>数据来源：中国政府网(gov.cn)、交通运输部(mot.gov.cn)、工信部(miit.gov.cn)、美国交通部(dot.gov)、NHTSA等</div>
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
    
    print(f"✅ 已生成 {output_path}, 共 {len(updates)} 条官方政策更新")
    
    # 保存JSON数据
    data_path = Path(__file__).parent / "data" / "updates.json"
    data_path.parent.mkdir(exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(updates, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存数据到 {data_path}")
    
    return updates

if __name__ == "__main__":
    main()
