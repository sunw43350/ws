import os

BASE_DIR = "./"
FILES = {
    "config.py": '''# 接口配置，可根据需要修改
REST_ENDPOINTS = {
    "binance": "https://fapi.binance.com/fapi/v1/exchangeInfo",
    # 添加其他交易所...
}
''',

    "fetcher.py": '''import requests

def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None
''',

    "parser.py": '''def parse_binance(data):
    symbols = []
    for item in data.get("symbols", []):
        symbols.append(item.get("symbol"))
    return symbols

# 可继续添加其他交易所的解析方法
''',

    "main.py": '''from config import REST_ENDPOINTS
from fetcher import fetch
from parser import parse_binance

def main():
    for name, url in REST_ENDPOINTS.items():
        print(f"Fetching from {name}...")
        data = fetch(url)
        if name == "binance" and data:
            symbols = parse_binance(data)
            print(f"{name} 合约数量: {len(symbols)}")

if __name__ == "__main__":
    main()
''',

    "requirements.txt": "requests\n",
}

def create_project():
    os.makedirs(BASE_DIR, exist_ok=True)
    for filename, content in FILES.items():
        path = os.path.join(BASE_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    print("✅ 项目初始化完成！")

if __name__ == "__main__":
    create_project()
