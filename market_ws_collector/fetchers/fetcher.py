import requests

import requests
import csv

REST_ENDPOINTS = {
    "binance": "https://fapi.binance.com/fapi/v1/exchangeInfo",
    "bitget": "https://api.bitget.com/api/mix/v1/market/contracts",
    "okx": "https://www.okx.com/api/v5/public/instruments?instType=SWAP",
    "bybit": "https://api.bybit.com/v5/market/instruments-info?category=linear",
    "mexc": "https://contract.mexc.com/api/v1/contract/detail",
    "oxfun": "https://api.ox.fun/api/v1/public/contracts",
    "phemex": "https://api.phemex.com/exchange/public/contracts",
}

def fetch_and_store_all(filename="contracts.csv"):
    # 初始化 CSV 文件（含表头）
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["exchange", "symbol"])

    for name, url in REST_ENDPOINTS.items():
        print(f"📡 获取 {name} 合约列表...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ {name} 请求失败：{e}")
            continue

        # 调用对应交易所解析函数
        symbols = parse_contracts(name, data)
        print(f"✅ {name} 合约数：{len(symbols)}")

        # 写入 CSV
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for symbol in symbols:
                writer.writerow([name, symbol])

def parse_contracts(exchange, data):
    if exchange == "binance":
        return [s["symbol"] for s in data.get("symbols", [])]
    elif exchange == "bitget":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "okx":
        return [s["instId"] for s in data.get("data", [])]
    elif exchange == "bybit":
        return [s["symbol"] for s in data.get("result", {}).get("list", [])]
    elif exchange == "mexc":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "oxfun":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "phemex":
        return [s["symbol"] for s in data.get("data", [])]
    else:
        print(f"⚠️ 未定义 {exchange} 的解析逻辑")
        return []

