import requests
import csv
import time

REST_ENDPOINTS = {
    "ascendex": "https://ascendex.com/api/pro/v1/futures/contracts",
    "binance": "https://fapi.binance.com/fapi/v1/exchangeInfo",
    "bingx": "https://open-api.bingx.com/openApi/swap/v2/quote/contracts",
    "bitfinex": "https://api.bitfinex.com/v2/conf/pub:list:pair:exchange",
    "bitget": "https://api.bitget.com/api/mix/v1/market/contracts?productType=USDT",
    "bitmart": "https://api-cloud.bitmart.com/futures/v2/contracts",
    "bitmex": "https://www.bitmex.com/api/v1/instrument/active",
    "bitrue": "https://openapi.bitrue.com/api/v1/contracts",
    "blofin": "https://api.blofin.com/api/v1/public/contracts",
    "bybit": "https://api.bybit.com/v5/market/instruments-info?category=linear",
    "coinbase": "https://api.exchange.coinbase.com/products",  # 注意：Coinbase 是现货
    "cryptocom": "https://api.crypto.com/v2/public/get-instruments",
    "digifinex": "https://openapi.digifinex.com/v3/futures/contracts",
    "gateio": "https://api.gate.io/api/v4/futures/usdt/contracts",
    "huobi": "https://api.hbdm.com/api/v1/contract_contract_info",
    "krakenfutures": "https://futures.kraken.com/derivatives/api/v3/instruments",
    "lbank": "https://api.lbank.info/v2/contract/getAllContracts.do",
    "mexc": "https://contract.mexc.com/api/v1/contract/detail",
    "okx": "https://www.okx.com/api/v5/public/instruments?instType=SWAP",
    "oxfun": "https://api.ox.fun/api/v1/public/contracts",
    "phemex": "https://api.phemex.com/exchange/public/contracts",
}

SPOT_ONLY = {"coinbase"}  # 标注为现货的交易所
USE_PROXIES_FOR = set()  # 如有代理需求，可加进来，如 {"blofin"}

PROXIES = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}


def safe_get(url, exchange=None, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            proxies = PROXIES if exchange in USE_PROXIES_FOR else None
            response = requests.get(url, timeout=10, proxies=proxies)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"⚠️ 请求失败（第{attempt}次）[{exchange}]: {e}")
            time.sleep(1)
    return None


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
    elif exchange == "coinbase":
        return [s["id"] for s in data if isinstance(s, dict)]
    elif exchange == "bitfinex":
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data[0]  # bitfinex返回的是 [["BTCUSD", "ETHUSD", ...]]
    elif exchange == "bitmex":
        return [s["symbol"] for s in data if "symbol" in s]
    elif exchange == "huobi":
        return [s["contract_code"] for s in data.get("data", [])]
    elif exchange == "ascendex":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "bingx":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "bitmart":
        return [s["symbol"] for s in data.get("contracts", [])]
    elif exchange == "blofin":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "cryptocom":
        return [s["instrument_name"] for s in data.get("result", {}).get("instruments", [])]
    elif exchange == "digifinex":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "gateio":
        return [s["name"] for s in data]
    elif exchange == "krakenfutures":
        return [s["symbol"] for s in data.get("instruments", [])]
    elif exchange == "lbank":
        return [s["symbol"] for s in data.get("data", [])]
    else:
        print(f"⚠️ 未定义 {exchange} 的解析逻辑")
        return []


def fetch_and_store_all(symbol_file="contracts.csv", summary_file="contracts_summary.csv"):
    with open(symbol_file, mode='w', newline='', encoding='utf-8') as sf, \
         open(summary_file, mode='w', newline='', encoding='utf-8') as smf:
        symbol_writer = csv.writer(sf)
        summary_writer = csv.writer(smf)

        symbol_writer.writerow(["exchange", "symbol", "type"])
        summary_writer.writerow(["exchange", "status", "count", "note"])

        for name, url in REST_ENDPOINTS.items():
            print(f"📡 获取 {name} 合约列表...")
            response = safe_get(url, exchange=name)
            if not response:
                print(f"❌ {name} 请求失败：无响应")
                summary_writer.writerow([name, "fail", 0, "no response"])
                continue

            try:
                data = response.json()
                symbols = parse_contracts(name, data)
                count = len(symbols)
                print(f"✅ {name} 合约数：{count}")
                for symbol in symbols:
                    typ = "spot" if name in SPOT_ONLY else "future"
                    symbol_writer.writerow([name, symbol, typ])
                summary_writer.writerow([name, "ok", count, ""])
            except Exception as e:
                print(f"❌ {name} 解析失败：{e}")
                summary_writer.writerow([name, "fail", 0, f"parse error: {e}"])


if __name__ == "__main__":
    fetch_and_store_all()
