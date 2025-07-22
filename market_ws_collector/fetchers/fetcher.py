import requests
import csv
import time

REST_ENDPOINTS = {
    "ascendex": "https://ascendex.com/api/pro/v1/futures/contracts",
    "binance": "https://fapi.binance.com/fapi/v1/exchangeInfo",
    "bingx": "https://open-api.bingx.com/openApi/swap/v2/quote/contracts",
    "bitfinex": "https://api.bitfinex.com/v2/conf/pub:list:pair:exchange",
    "bitget": "https://api.bitget.com/api/mix/v1/market/contracts?productType=USDT",
    "bitmart": "https://api-cloud.bitmart.com/contract/v1/ifcontract/contracts",
    "bitmex": "https://www.bitmex.com/api/v1/instrument/active",
    "bitrue": "https://openapi.bitrue.com/api/v1/contracts",
    "blofin": "https://api.blofin.com/api/v1/public/contracts",
    "bybit": "https://api.bybit.com/v5/market/instruments-info?category=linear",
    "coinbase": "https://api.exchange.coinbase.com/products",  # ⚠️ 现货-only
    "cryptocom": "https://api.crypto.com/v2/public/get-instruments",
    "digifinex": "https://openapi.digifinex.com/v3/futures/contracts",
    "gateio": "https://api.gateio/ws/api/v4/futures/usdt/contracts",
    "huobi": "https://api.hbdm.com/api/v1/contract_contract_info",
    "krakenfutures": "https://futures.kraken.com/derivatives/api/v3/instruments",
    "lbank": "https://api.lbank.info/v2/contract/getAllContracts.do",
    "mexc": "https://contract.mexc.com/api/v1/contract/detail",
    "okx": "https://www.okx.com/api/v5/public/instruments?instType=SWAP",
    "oxfun": "https://api.ox.fun/api/v1/public/contracts",  # ⛔ 接口失效
    "phemex": "https://api.phemex.com/exchange/public/contracts",  # ⛔ 需认证
}

SPOT_ONLY = {"coinbase"}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def safe_get(url, retries=3, headers=None, verify_ssl=True):
    for attempt in range(retries):
        try:
            return requests.get(url, headers=headers, timeout=10, verify=verify_ssl)
        except Exception as e:
            print(f"⚠️ 请求失败（第{attempt + 1}次）：{e}")
            time.sleep(1)
    return None


def fetch_and_store_all(filename="contracts.csv", error_log="contracts_errors.log"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file, \
         open(error_log, mode='w', encoding='utf-8') as err_file:

        writer = csv.writer(file)
        writer.writerow(["exchange", "symbol", "type"])

        for name, url in REST_ENDPOINTS.items():
            print(f"📡 获取 {name} 合约列表...")

            verify_ssl = not name.startswith("gateio")  # gateio证书问题
            response = safe_get(url, headers=HEADERS, verify_ssl=verify_ssl)

            if not response or response.status_code != 200:
                msg = f"{name} 请求失败：{response.status_code if response else '无响应'}\n"
                print("❌ " + msg.strip())
                err_file.write(msg)
                continue

            try:
                data = response.json()
                symbols = parse_contracts(name, data)
                print(f"✅ {name} 合约数：{len(symbols)}")
                for symbol in symbols:
                    writer.writerow([name, symbol, "spot" if name in SPOT_ONLY else "future"])
            except Exception as e:
                msg = f"{name} 解析失败：{e}\n"
                print("❌ " + msg.strip())
                err_file.write(msg)


def parse_contracts(exchange, data):
    if exchange == "binance":
        return [s["symbol"] for s in data.get("symbols", [])]
    elif exchange == "bitget":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "bitmart":
        return [s["symbol"] for s in data.get("data", {}).get("contracts", [])]
    elif exchange == "okx":
        return [s["instId"] for s in data.get("data", [])]
    elif exchange == "bybit":
        return [s["symbol"] for s in data.get("result", {}).get("list", [])]
    elif exchange == "mexc":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "phemex":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "bitmex":
        return [s["symbol"] for s in data]
    elif exchange == "blofin":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "gateio":
        return [s["name"] for s in data]
    elif exchange == "krakenfutures":
        return [s["symbol"] for s in data.get("instruments", [])]
    elif exchange == "ascendex":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "huobi":
        return [s["contract_code"] for s in data.get("data", [])]
    elif exchange == "digifinex":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "bitfinex":
        if isinstance(data, list) and len(data) > 0:
            return data[0]
    elif exchange == "bitrue":
        return [s["symbol"] for s in data]
    elif exchange == "bingx":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "cryptocom":
        return [s["instrument_name"] for s in data.get("result", {}).get("instruments", [])]
    elif exchange == "lbank":
        return [s["symbol"] for s in data.get("data", [])]
    elif exchange == "coinbase":
        return [s["id"] for s in data]
    else:
        print(f"⚠️ 未定义 {exchange} 的解析逻辑")
        return []


if __name__ == "__main__":
    fetch_and_store_all()
