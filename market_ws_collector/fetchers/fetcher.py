import requests

import requests
import csv

REST_ENDPOINTS = {
    "ascendex": "https://ascendex.com/api/pro/v1/futures/contracts",
    "binance": "https://fapi.binance.com/fapi/v1/exchangeInfo",
    "bingx": "https://open-api.bingx.com/openApi/swap/v2/quote/contracts",
    "bitfinex": "https://api.bitfinex.com/v2/conf/pub:list:pair:exchange",
    "bitget": "https://api.bitget.com/api/mix/v1/market/contracts",
    "bitmart": "https://api-cloud.bitmart.com/futures/v2/contracts",
    "bitmex": "https://www.bitmex.com/api/v1/instrument/active",
    "bitrue": "https://openapi.bitrue.com/api/v1/contracts",
    "blofin": "https://api.blofin.com/api/v1/public/contracts",
    "bybit": "https://api.bybit.com/v5/market/instruments-info?category=linear",
    "coinbase": "https://api.exchange.coinbase.com/products",  # 注意：Coinbase 不支持合约，但此为现货产品列表
    "cryptocom": "https://api.crypto.com/v2/public/get-instruments",
    "digifinex": "https://openapi.digifinex.com/v3/futures/contracts",
    "gateio": "https://api.gate.io/api/v4/futures/usdt/contracts",
    "huobi": "https://api.hbdm.com/api/v1/contract_contract_info",
    "krakenfutures": "https://futures.kraken.com/derivatives/api/v3/instruments",
    "lbank": "https://api.lbkex.com/v2/futuresInfo.do",
    "mexc": "https://contract.mexc.com/api/v1/contract/detail",
    "okx": "https://www.okx.com/api/v5/public/instruments?instType=SWAP",
    "oxfun": "https://api.ox.fun/api/v1/public/contracts",  # ⚠️ 当前可能不可用或已废弃
    "phemex": "https://api.phemex.com/exchange/public/contracts",  # ⚠️ 可能需要身份认证
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


if __name__ == "__main__":
    fetch_and_store_all()
