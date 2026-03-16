import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 获取首页提取加密参数
response = requests.get('https://www.0826j.com/', headers=headers, timeout=30)
html = response.text

# 提取所有加密参数
params = {}
var_pattern = r'var\s+(\w+)\s*=\s*["\']([^"\']*)["\']'
matches = re.findall(var_pattern, html)
print('=== 提取的参数 ===')
for name, value in matches:
    if len(value) > 3:
        print(f'{name}: {value}')
        params[name] = value

print('\n=== 尝试调用API ===')
# 构建API请求
api_url = 'https://www.0826j.com/api/search'
data = {
    'q': '斗破',
    **params
}
print('请求参数:', json.dumps(data, ensure_ascii=False, indent=2))
api_response = requests.post(api_url, data=data, headers=headers, timeout=30)
print('状态码:', api_response.status_code)
print('响应内容:', api_response.text[:2000])
