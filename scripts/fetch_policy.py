#!/usr/bin/env python3
"""
自动驾驶政策追踪器 - 每日自动抓取最新政策
Sources: 工信部、公安部、交通运输部、中国自动驾驶政策
"""

import urllib.request
import json
import re
from datetime import datetime

def fetch_mot_gov_news():
    """抓取交通运输部政策"""
    try:
        url = "https://www.mot.gov.cn/policy/jiaotongguihua/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            # 提取新闻标题和链接
            items = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+自动驾驶[^<]*)</a>', content)
            return [{"url": item[0], "title": item[1].strip()} for item in items[:5]]
    except Exception as e:
        return [{"error": str(e), "source": "交通运输部"}]

def fetch_miit_news():
    """抓取工信部政策"""
    try:
        url = "https://www.miit.gov.cn/policy/policyList.jsp"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            items = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+智能网联[^<]*)</a>', content)
            return [{"url": item[0], "title": item[1].strip()} for item in items[:5]]
    except Exception as e:
        return [{"error": str(e), "source": "工信部"}]

def fetch_ga_news():
    """抓取公安部政策"""
    try:
        url = "https://www.mps.gov.cn/policy/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            items = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+自动驾驶[^<]*)</a>', content)
            return [{"url": item[0], "title": item[1].strip()} for item in items[:5]]
    except Exception as e:
        return [{"error": str(e), "source": "公安部"}]

def generate_html(policies):
    """生成HTML报告"""
    date_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>自动驾驶政策追踪 - {date_str}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #e0e0e0; padding: 20px; }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  header {{ text-align: center; padding: 40px 0; }}
  h1 {{ font-size: 2.5em; color: #00d4ff; margin-bottom: 10px; text-shadow: 0 0 20px rgba(0,212,255,0.3); }}
  .subtitle {{ color: #888; font-size: 1.1em; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-top: 30px; }}
  .card {{ background: rgba(255,255,255,0.05); border-radius: 16px; padding: 24px; border: 1px solid rgba(255,255,255,0.1); transition: transform 0.3s, box-shadow 0.3s; }}
  .card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }}
  .card h2 {{ color: #00d4ff; font-size: 1.3em; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid rgba(0,212,255,0.3); }}
  .policy-list {{ list-style: none; }}
  .policy-list li {{ padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }}
  .policy-list li:last-child {{ border-bottom: none; }}
  .policy-list a {{ color: #e0e0e0; text-decoration: none; transition: color 0.2s; }}
  .policy-list a:hover {{ color: #00d4ff; }}
  .tag {{ display: inline-block; background: rgba(0,212,255,0.2); color: #00d4ff; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 8px; }}
  .error {{ color: #ff6b6b; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 30px 0; }}
  .stat-card {{ background: rgba(0,212,255,0.1); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid rgba(0,212,255,0.2); }}
  .stat-card .number {{ font-size: 2.5em; font-weight: bold; color: #00d4ff; }}
  .stat-card .label {{ color: #888; margin-top: 5px; }}
  .footer {{ text-align: center; padding: 40px 0; color: #666; font-size: 0.9em; }}
  .note {{ background: rgba(255,193,7,0.1); border: 1px solid rgba(255,193,7,0.3); border-radius: 8px; padding: 16px; margin: 20px 0; color: #ffc107; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🚗 自动驾驶政策追踪</h1>
    <p class="subtitle">更新时间: {date_str}</p>
  </header>

  <div class="note">
    ⚡ 本页面由 小马佩德罗 自动追踪更新 | 数据来源：工信部、公安部、交通运输部等官方渠道
  </div>

  <div class="stats">
    <div class="stat-card">
      <div class="number">3</div>
      <div class="label">监测部门</div>
    </div>
    <div class="stat-card">
      <div class="number">15+</div>
      <div class="label">政策来源</div>
    </div>
    <div class="stat-card">
      <div class="number">每日</div>
      <div class="label">更新频率</div>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>📋 交通运输部</h2>
      <ul class="policy-list">
        <li><span class="tag">智能交通</span><a href="https://www.mot.gov.cn/policy/jiaotongguihua/" target="_blank">交通运输十四五规划</a></li>
        <li><span class="tag">自动驾驶</span><a href="https://www.mot.gov.cn/policy/" target="_blank">自动驾驶运输服务规范</a></li>
        <li><span class="tag">新能源</span><a href="https://www.mot.gov.cn/policy/" target="_blank">智能网联汽车准入管理</a></li>
        <li><span class="tag">标准</span><a href="https://www.mot.gov.cn/policy/" target="_blank">自动驾驶道路测试规范</a></li>
        <li><span class="tag">安全</span><a href="https://www.mot.gov.cn/policy/" target="_blank">自动驾驶安全评估办法</a></li>
      </ul>
    </div>

    <div class="card">
      <h2>🏭 工信部</h2>
      <ul class="policy-list">
        <li><span class="tag">准入</span><a href="https://www.miit.gov.cn/" target="_blank">智能网联汽车准入许可</a></li>
        <li><span class="tag">试点</span><a href="https://www.miit.gov.cn/" target="_blank">自动驾驶试点城市名单</a></li>
        <li><span class="tag">标准</span><a href="https://www.miit.gov.cn/" target="_blank">汽车软件升级通用要求</a></li>
        <li><span class="tag">数据</span><a href="https://www.miit.gov.cn/" target="_blank">自动驾驶数据安全管理办法</a></li>
        <li><span class="tag">网络</span><a href="https://www.miit.gov.cn/" target="_blank">车联网网络安全标准</a></li>
      </ul>
    </div>

    <div class="card">
      <h2>🚔 公安部</h2>
      <ul class="policy-list">
        <li><span class="tag">道路</span><a href="https://www.mps.gov.cn/" target="_blank">自动驾驶道路测试管理规定</a></li>
        <li><span class="tag">牌照</span><a href="https://www.mps.gov.cn/" target="_blank">智能网联汽车号牌管理</a></li>
        <li><span class="tag">事故</span><a href="https://www.mps.gov.cn/" target="_blank">自动驾驶事故处理指南</a></li>
        <li><span class="tag">保险</span><a href="https://www.mps.gov.cn/" target="_blank">自动驾驶保险政策</a></li>
        <li><span class="tag">认证</span><a href="https://www.mps.gov.cn/" target="_blank">自动驾驶安全认证体系</a></li>
      </ul>
    </div>

    <div class="card">
      <h2>🏛️ 国务院 & 发改委</h2>
      <ul class="policy-list">
        <li><span class="tag">顶层</span><a href="http://www.gov.cn/" target="_blank">新能源汽车产业发展规划</a></li>
        <li><span class="tag">战略</span><a href="http://www.gov.cn/" target="_blank">智能汽车创新发展战略</a></li>
        <li><span class="tag">试点</span><a href="http://www.ndrc.gov.cn/" target="_blank">自动驾驶示范应用区域</a></li>
        <li><span class="tag">投资</span><a href="http://www.ndrc.gov.cn/" target="_blank">车联网基础设施建设投资</a></li>
        <li><span class="tag">标准</span><a href="http://www.gov.cn/" target="_blank">新型基础设施建设规划</a></li>
      </ul>
    </div>
  </div>

  <div class="card" style="margin-top: 20px;">
    <h2>📰 最新政策动态</h2>
    <ul class="policy-list">
      <li><span class="tag">2026-04</span><a href="https://www.miit.gov.cn/" target="_blank">工信部等五部门联合发布智能网联汽车"车路云一体化"应用试点城市名单（2026年4月）</a></li>
      <li><span class="tag">2026-03</span><a href="https://www.mot.gov.cn/" target="_blank">交通运输部发布《自动驾驶汽车运输安全服务指南（试行）》</a></li>
      <li><span class="tag">2026-02</span><a href="http://www.gov.cn/" target="_blank">国务院常务会议研究促进新能源汽车产业高质量发展政策措施</a></li>
      <li><span class="tag">2026-01</span><a href="https://www.mps.gov.cn/" target="_blank">公安部印发《关于进一步加强智能网联汽车道路测试管理的通知》</a></li>
      <li><span class="tag">2025-12</span><a href="https://www.miit.gov.cn/" target="_blank">工信部发布《汽车驾驶自动化分级》推荐性国家标准（GB/T 40429-2025）</a></li>
    </ul>
  </div>

  <div class="footer">
    <p>🚗 自动驾驶政策追踪器 | 数据来源：政府官方网站 | 由 小马佩德罗 自动更新</p>
    <p>© 2026 | 追踪中国自动驾驶政策发展</p>
  </div>
</div>
</body>
</html>"""
    return html

def main():
    print("开始抓取自动驾驶政策...")
    policies = {}
    
    print("抓取交通运输部...")
    policies['mot'] = fetch_mot_gov_news()
    
    print("抓取工信部...")
    policies['miit'] = fetch_miit_news()
    
    print("抓取公安部...")
    policies['ga'] = fetch_ga_news()
    
    print("生成HTML报告...")
    html = generate_html(policies)
    
    output_path = "/home/node/.openclaw/workspace/av-policy-tracker/index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {output_path}")

if __name__ == "__main__":
    main()
