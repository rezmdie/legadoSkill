import requests
import re
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

session = requests.Session()
session.headers.update(headers)

try:
    # 先访问主页
    print("正在访问 http://www.wangshu.org/ ...")
    response = session.get('http://www.wangshu.org/', timeout=30, allow_redirects=True)
    
    print(f"状态码: {response.status_code}")
    print(f"最终URL: {response.url}")
    
    if response.status_code == 200:
        # 从HTTP头获取编码
        content_type = response.headers.get('Content-Type', '')
        encoding = 'utf-8'  # 默认编码
        
        if 'charset=' in content_type:
            match = re.search(r'charset=([^\s;]+)', content_type, re.IGNORECASE)
            if match:
                encoding = match.group(1).strip('"\'')
        
        print(f"从HTTP头检测到的编码: {encoding}")
        
        # 从HTML meta标签获取编码
        html_preview = response.content[:2048].decode('latin-1', errors='ignore')
        meta_patterns = [
            r'<meta\s+charset=["\']?([^"\'>\s]+)',
            r'<meta\s+http-equiv=["\']?content-type["\']?\s+content=["\']?[^"\']*charset=([^"\'>\s;]+)',
        ]
        for pattern in meta_patterns:
            match = re.search(pattern, html_preview, re.IGNORECASE)
            if match:
                encoding = match.group(1).lower()
                print(f"从HTML meta标签检测到的编码: {encoding}")
                break
        
        # 使用检测到的编码解码
        try:
            html = response.content.decode(encoding, errors='replace')
        except:
            html = response.content.decode('utf-8', errors='replace')
            encoding = 'utf-8'
            print(f"使用默认编码: {encoding}")
        
        # 保存HTML
        with open('wangshu.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML已保存到 wangshu.html")
        print(f"HTML长度: {len(html)} 字符")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
