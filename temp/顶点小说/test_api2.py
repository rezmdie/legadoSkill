import requests
import re
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 等待3秒后重试
time.sleep(3)

# 获取首页提取加密参数
response = requests.get('https://www.0826j.com/', headers=headers, timeout=30)
html = response.text

# 提取所有加密参数
params = {}
var_pattern = r'var\s+(\w+)\s*=\s*["\']([^"\']*)["\']'
matches = re.findall(var_pattern, html)
for name, value in matches:
    params[name] = value

# 构建API请求
api_url = 'https://www.0826j.com/api/search'
data = {
    'q': '斗破',
    'vw': params.get('vw', ''),
    'abw': params.get('abw', ''),
    'ru': params.get('ru', ''),
    'jrt': params.get('jrt', ''),
    'van': params.get('van', ''),
    'fw': params.get('fw', ''),
    'cwl': params.get('cwl', ''),
    'gpr': params.get('gpr', ''),
    'uyoo': params.get('uyoo', ''),
    'tz': params.get('tz', ''),
    'euu': params.get('euu', ''),
    'tsn': params.get('tsn', ''),
    'eju': params.get('eju', ''),
    'um': params.get('um', ''),
    'fp': params.get('fp', ''),
    'dvm': params.get('dvm', ''),
    'jpk': params.get('jpk', ''),
    'deblkx': params.get('deblkx', ''),
    'ht': params.get('ht', ''),
    'azy': params.get('azy', ''),
    'sna': params.get('sna', ''),
    'wqx': params.get('wqx', ''),
    'fpp': params.get('fpp', ''),
    'rup': params.get('rup', ''),
    'jwj': params.get('jwj', ''),
    'bgt': params.get('bgt', ''),
    'qp': params.get('qp', ''),
    'yf': params.get('yf', ''),
    'cw': params.get('cw', ''),
    'wq': params.get('wq', ''),
    'sign': params.get('sign', ''),
}

print('=== 调用API ===')
api_response = requests.post(api_url, data=data, headers=headers, timeout=30)
print('状态码:', api_response.status_code)
print('响应内容:', api_response.text)
