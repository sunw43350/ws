import websocket
import json
import time

WS_URL = "wss://ascendex.com/1/api/pro/v2/stream"
CONTRACTS = ["BTC-PERP", "ETH-PERP", "SOL-PERP", "XRP-PERP", "LTC-PERP"]

def on_open(ws):
    print("✅ 已连接 AscendEX WebSocket")

    for i, symbol in enumerate(CONTRACTS):
        # ✅ 使用 depth:{symbol}:0 频道订阅买一卖一深度
        sub_msg = {
            "op": "sub",
            "id": f"depth_{i}",
            "ch": f"depth:{symbol}:0"
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: depth → {symbol}")
        time.sleep(0.3)  # ✅ 控制订阅速率，防止限速或拒绝

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ 推送字段结构说明（depth:...:0 推送）
        # 'm': 'depth'
        # 'symbol': 合约代码，如 BTC-PERP
        # 'data': {
        #     'bids': [ [价格, 数量], ... ],
        #     'asks': [ [价格, 数量], ... ]
        # }

        if data.get("m") == "depth" and "symbol" in data:
            symbol = data["symbol"]
            bids = data.get("data", {}).get("bids", [])
            asks = data.get("data", {}).get("asks", [])

            bid_price, bid_qty = bids[0] if bids else ("-", "-")
            ask_price, ask_qty = asks[0] if asks else ("-", "-")
            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print(f"❌ 解码失败: {e}")

def on_error(ws, error):
    print(f"❌ WebSocket 错误: {error}")

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import asyncio
import websockets
import json

# 构建订阅的合约列表
SYMBOLS = ["btcusdt", "ethusdt", "solusdt", "bnbusdt", "adausdt"]
STREAMS = [f"{symbol}@ticker" for symbol in SYMBOLS]

# 拼接成组合流地址
STREAM_URL = f"wss://stream.binance.com:9443/stream?streams={'/'.join(STREAMS)}"

async def binance_ws():
    async with websockets.connect(STREAM_URL) as ws:
        print("✅ 已连接 Binance WebSocket，订阅以下合约:")
        for s in SYMBOLS:
            print(f"🔔 {s.upper()} @ticker")

        while True:
            message = await ws.recv()
            try:
                data = json.loads(message)
                stream = data.get("stream")
                payload = data.get("data")

                if payload:
                    symbol = payload.get("s")
                    price = payload.get("c")  # 最新成交价
                    print(f"📈 {symbol} 最新价格: {price}")
            except Exception as e:
                print("❌ 解码错误:", e)
                print("原始消息:", message)

if __name__ == "__main__":
    try:
        asyncio.run(binance_ws())
    except KeyboardInterrupt:
        print("🚪 用户终止连接")
import websocket
import json
import gzip

# ✅ 正确的 WebSocket 地址
WS_URL = "wss://open-api-ws.bingx.com/market"

# ✅ BingX 支持的交易对格式（务必大写，如 BTC-USDT）
SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]

def on_open(ws):
    print("✅ 已连接 BingX WebSocket")

    # ✅ 按官方格式发送订阅请求：使用 reqType 和 dataType
    for i, symbol in enumerate(SYMBOLS):
        sub_msg = {
            "id": f"depth-{i+1}",                # 唯一标识符
            "reqType": "sub",                    # 订阅类型
            "dataType": f"{symbol}@depth20"      # ✅ 订阅前 20 档深度，@depth、@depth20、@depth100 均可
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: {sub_msg['dataType']}")

def on_message(ws, message):
    try:
        # ✅ BingX 返回的是 Gzip 压缩字节流，需解压
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        # ✅ 示例字段说明（depth 推送结构）：
        # 'data': {
        #   'bids': [ [价格, 数量], ... ]   → 买一挂单列表（降序）
        #   'asks': [ [价格, 数量], ... ]   → 卖一挂单列表（升序）
        # }
        # 'dataType': 如 'BTC-USDT@depth20'

        if "data" in data and "dataType" in data:
            symbol = data["dataType"].split("@")[0]
            bids = data["data"].get("bids", [])
            asks = data["data"].get("asks", [])

            bid_price, bid_qty = bids[0] if bids else ("-", "-")
            ask_price, ask_qty = asks[0] if asks else ("-", "-")

            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print("❌ 解压或解析失败:", e)

def on_error(ws, error):
    print("❌ WebSocket 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    # ✅ 启动 WebSocket 客户端
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json
import time

WS_URL = "wss://api-pub.bitfinex.com/ws/2"
CONTRACTS = ["tBTCUSD", "tETHUSD", "tSOLUSD", "tXRPUSD", "tLTCUSD"]

def on_open(ws):
    print("✅ 已连接 Bitfinex WebSocket")

    for symbol in CONTRACTS:
        sub_msg = {
            "event": "subscribe",
            "channel": "ticker",
            "symbol": symbol
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: ticker → {symbol}")
        time.sleep(0.3)  # 控制订阅速率，避免触发限速

def on_message(ws, message):
    try:
        data = json.loads(message)
        print(data)  # 打印原始消息以便调试

        # ✅ ticker 推送结构：[CHAN_ID, [BID, BID_SIZE, ASK, ASK_SIZE, ...]]
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            chan_id = data[0]
            payload = data[1]
            bid = payload[0]
            ask = payload[2]
            print(f"📊 CHAN_ID {chan_id} | 买一: {bid} | 卖一: {ask}")

        # ✅ 处理订阅确认
        elif isinstance(data, dict) and data.get("event") == "subscribed":
            print(f"✅ 订阅成功: {data.get('channel')} → {data.get('symbol')}")

        # ✅ 处理错误信息
        elif isinstance(data, dict) and data.get("event") == "error":
            print(f"❌ 错误: {data.get('msg')}")

    except Exception as e:
        print(f"❌ 解码失败: {e}")

def on_error(ws, error):
    print(f"❌ WebSocket 错误: {error}")

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json
import zlib

WS_URL = "wss://ws.bitget.com/v2/ws/public"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "LTCUSDT"]

# Bitget 使用 zlib 压缩，需解压
def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompress.decompress(data) + decompress.flush()

def on_open(ws):
    print("✅ 已连接 Bitget 合约 WebSocket")

    # 构造订阅消息（books5 表示前 5 档深度）
    sub_msg = {
        "op": "subscribe",
        "args": [
            {
                "instType": "USDT-FUTURES",
                "channel": "books5",
                "instId": symbol
            } for symbol in SYMBOLS
        ]
    }
    ws.send(json.dumps(sub_msg))
    print("📨 已发送订阅请求:", sub_msg)

def on_message(ws, message):
    try:
        # text = inflate(message).decode("utf-8")
        data = json.loads(message)
        print(data)

        # ✅ 示例字段说明（books5 推送结构）：
        # 'bids': [ [价格, 数量], ... ] → 买单列表（降序）
        # 'asks': [ [价格, 数量], ... ] → 卖单列表（升序）
        # 'instId': 合约名称，如 BTCUSDT

        if "data" in data and "arg" in data:
            symbol = data["arg"].get("instId", "unknown")
            bids = data["data"][0].get("bids", [])
            asks = data["data"][0].get("asks", [])

            bid_price, bid_qty = bids[0] if bids else ("-", "-")
            ask_price, ask_qty = asks[0] if asks else ("-", "-")

            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print("❌ 解压失败:", e)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import asyncio
import websockets
import json

BITMART_WS_URL = "wss://openapi-ws-v2.bitmart.com/api?protocol=1.1"


# 订阅的合约交易对（示例）
SYMBOLS = ["BTCUSDT", "ETHUSDT"]

async def subscribe_bitmart():
    async with websockets.connect(BITMART_WS_URL) as ws:
        print("✅ 已连接 BitMart WebSocket")

        # 构造订阅消息
        subscribe_msg = {
            "action": "subscribe",
            "args": [f"futures/ticker:{symbol}" for symbol in SYMBOLS]
        }

        # {
        # "action":"subscribe",
        # "args":["futures/ticker:BTCUSDT"]
        # }
        
        await ws.send(json.dumps(subscribe_msg))
        print("📨 已发送订阅请求:", subscribe_msg)

        while True:
            message = await ws.recv()
            print("📩 收到消息:", message)

if __name__ == "__main__":
    try:
        asyncio.run(subscribe_bitmart())
    except KeyboardInterrupt:
        print("🚪 用户终止连接")
import websocket
import json
import time

WS_URL = "wss://ws.bitmex.com/realtime"
CONTRACTS = ["XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD", "LTCUSD"]

def on_open(ws):
    print("✅ 已连接 BitMEX WebSocket")

    # ✅ 订阅 quote 和 orderBookL2_25（前 25 档深度）
    sub_msg = {
        "op": "subscribe",
        "args": [f"quote:{symbol}" for symbol in CONTRACTS] +
                [f"orderBookL2_25:{symbol}" for symbol in CONTRACTS]
    }
    ws.send(json.dumps(sub_msg))
    print("📨 已发送订阅请求:", sub_msg)

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ quote 推送结构：买一卖一价格
        if data.get("table") == "quote" and data.get("action") == "insert":
            for quote in data.get("data", []):
                symbol = quote.get("symbol", "unknown")
                bid = quote.get("bidPrice", "-")
                ask = quote.get("askPrice", "-")
                print(f"📊 {symbol} | 买一: {bid} | 卖一: {ask}")

    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ WebSocket 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json
import gzip

WS_URL = "wss://ws.bitrue.com/kline-api/ws"
SYMBOLS = ["btcusdt", "ethusdt", "solusdt", "xrpusdt", "ltcusdt"]

def on_open(ws):
    print("✅ 已连接 Bitrue WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "event": "sub",
            "params": {
                "channel": f"market_{symbol}_depth_step0",  # ✅ 订阅 1档深度数据
                "cb_id": symbol
            }
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: market_{symbol}_depth_step0")

def on_message(ws, message):
    try:
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        print(data)

        # ✅ 示例字段说明：
        # 'bids': [ [价格, 数量], ... ] → 买单列表（降序）
        # 'asks': [ [价格, 数量], ... ] → 卖单列表（升序）
        # 'channel': 如 'market_btcusdt_depth_step0'

        # if "channel" in data and "tick" in data:
        #     symbol = data["channel"].split("_")[1]
        #     bids = data["tick"].get("bids", [])
        #     asks = data["tick"].get("asks", [])

        #     bid_price, bid_qty = bids[0] if bids else ("-", "-")
        #     ask_price, ask_qty = asks[0] if asks else ("-", "-")

        #     print(f"📊 {symbol.upper()} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print("❌ 解压失败:", e)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json

WS_URL = "wss://openapi.blofin.com/ws/public"
CONTRACTS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]

def on_open(ws):
    print("✅ 已连接 BloFin WebSocket")

    for symbol in CONTRACTS:
        # sub_msg = {
        #     "op": "subscribe",
        #     "args": [
        #         {
        #             "channel": "ticker",
        #             "instId": symbol
        #         }
        #     ]
        # }
        sub_msg = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "tickers",
                    "instType": "CONTRACT",
                    "instId": symbol  # 如 "BTC-USDT"
                }
            ]
        }

        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: ticker → {symbol}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        print(data)  # 打印原始消息以便调试

        # ✅ 示例字段说明（ticker 推送结构）：
        # 'bidPx': 买一价格
        # 'askPx': 卖一价格
        # 'instId': 合约名称，如 BTC-USDT

        if data.get("arg", {}).get("channel") == "ticker" and "data" in data:
            ticker = data["data"][0]
            symbol = ticker.get("instId", "unknown")
            bid = ticker.get("bidPx", "-")
            ask = ticker.get("askPx", "-")
            print(f"📊 {symbol} | 买一: {bid} | 卖一: {ask}")

    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ WebSocket 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import asyncio
import websockets
import json

BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

# 要订阅的合约交易对（USDT本位）
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "ADAUSDT"]

async def subscribe_bybit_tickers():
    async with websockets.connect(BYBIT_WS_URL) as ws:
        print("✅ Connected to Bybit WebSocket")

        # 构造订阅请求
        subscribe_msg = {
            "op": "subscribe",
            "args": [f"tickers.{symbol}" for symbol in SYMBOLS]
        }
        await ws.send(json.dumps(subscribe_msg))
        print("📨 Sent subscription:", subscribe_msg)

        # 持续接收消息
        while True:
            message = await ws.recv()
            try:
                data = json.loads(message)
                # 可根据需要过滤 tickers 消息处理
                print("📩 Received:", json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print("❌ Failed to decode message:", message)

# 运行主程序
if __name__ == "__main__":
    try:
        asyncio.run(subscribe_bybit_tickers())
    except KeyboardInterrupt:
        print("🚪 Exit on user interrupt")


        # ===========================================
import websocket
import json

WS_URL = "wss://advanced-trade-ws.coinbase.com"

# 要订阅的交易对（产品 ID）
PRODUCT_IDS = ["BTC-USD", "ETH-USD", "SOL-USD", "LTC-USD", "ADA-USD"]

def on_open(ws):
    print("✅ 已连接 Coinbase WebSocket")

    # 构造订阅消息
    subscribe_msg = {
        "type": "subscribe",
        "product_ids": PRODUCT_IDS,
        "channel": "ticker"  # 可选频道：ticker, market_trades, level2, candles 等
    }
    ws.send(json.dumps(subscribe_msg))
    print("📨 已发送订阅请求:", subscribe_msg)

def on_message(ws, message):
    data = json.loads(message)
    print("📩 收到消息:", data)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws):
    print("🚪 连接关闭")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json

# "b": "187.08",   // 最优买价
# "bs": "0.611",   // 最优买量
# "k": "187.09",   // 最优卖价
# "ks": "0.497"    // 最优卖量


WS_URL = "wss://stream.crypto.com/exchange/v1/market"
PRODUCTS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "LTC_USDT"]

def on_open(ws):
    print("✅ 已连接 Crypto.com WebSocket")

    for i, symbol in enumerate(PRODUCTS):
        sub_msg = {
            "id": i + 1,
            "method": "subscribe",
            "params": {
                "channels": [f"ticker.{symbol}"]
            }
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 ticker.{symbol}")

def on_message(ws, message):
    print("📩 收到消息:", message)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import asyncio
import websockets
import zlib
import json

WS_URL = "wss://openapi.digifinex.com/swap_ws/v2/"


def decompress_message(message: bytes) -> str:
    """解压 gzip binary message"""
    # decompress = zlib.decompressobj(-zlib.MAX_WBITS)  # raw gzip
    inflated = zlib.decompress(message) 
    return inflated.decode('utf-8')


async def subscribe_ticker():
    async with websockets.connect(WS_URL) as ws:
        print("✅ WebSocket 连接成功")

        # 订阅 ticker 数据
        sub_msg = {
            "event": "ticker.subscribe",
            "id": 1,
            "instrument_ids": ["BTCUSDTPERP", "ETHUSDTPERP"]
        }
        await ws.send(json.dumps(sub_msg))

        # 发送 ping（可选）
        await ws.send(json.dumps({"id": 1, "event": "server.ping"}))

        while True:
            message = await ws.recv()

            if isinstance(message, bytes):
                try:
                    text = decompress_message(message)
                    print("📩 收到解压消息:", text)
                except Exception as e:
                    print("❌ 解压失败:", e)
            else:
                print("📝 收到文本消息:", message)


if __name__ == "__main__":
    asyncio.run(subscribe_ticker())
import websocket
import json
import time

WS_URL = "wss://fx-ws.gateio.ws/v4/ws/usdt"
CONTRACTS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "LTC_USDT"]

def on_open(ws):
    print("✅ 已连接 Gate.io 合约 WebSocket")

    for contract in CONTRACTS:
        sub_msg = {
            "time": int(time.time()),
            "channel": "futures.book_ticker",  # ✅ 买一卖一频道
            "event": "subscribe",
            "payload": [contract]
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: futures.book_ticker → {contract}")

def on_message(ws, message):
    try:
        data = json.loads(message)
        print(data)

        # ✅ 示例字段说明（book_ticker 推送结构）：
        # 'result': {
        #   'contract': 合约名称，如 BTC_USDT
        #   'ask': 卖一价格
        #   'ask_size': 卖一挂单量
        #   'bid': 买一价格
        #   'bid_size': 买一挂单量
        # }

        # if data.get("channel") == "futures.book_ticker" and data.get("event") == "update":
        #     ticker = data.get("result", {})
        #     symbol = ticker.get("contract", "unknown")
        #     print(f"📊 {symbol} | 买一: {ticker['bid']} ({ticker['bid_size']}) | 卖一: {ticker['ask']} ({ticker['ask_size']})")

    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import gzip
import json

WS_URL = "wss://api.huobi.pro/ws"
SYMBOLS = ["btcusdt", "ethusdt", "solusdt", "ltcusdt", "xrpusdt"]


# bid, b, best_bid_price	买一价格（当前市场中最高买价）
# bidSize, bs, best_bid_volume	买一挂单数量（买一对应挂单量）
# ask, k, best_ask_price	卖一价格（当前市场中最低卖价）
# askSize, ks, best_ask_volume	卖一挂单数量（卖一对应挂单量）


def on_open(ws):
    print("✅ 已连接 Huobi WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "sub": f"market.{symbol}.ticker",
            "id": symbol
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: market.{symbol}.ticker")

def on_message(ws, message):
    try:
        data = gzip.decompress(message).decode("utf-8")
        msg = json.loads(data)

        if "ping" in msg:
            pong = {"pong": msg["ping"]}
            ws.send(json.dumps(pong))
        else:
            print("📩 收到消息:", msg)
    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json

WS_URL = "wss://beta-ws.kraken.com/v2"
SYMBOLS = ["BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "LTC/USD"]

def on_open(ws):
    print("✅ 已连接 Kraken Spot WebSocket")

    # 构造订阅消息
    sub_msg = {
        "method": "subscribe",
        "params": {
            "channel": "ticker",
            "symbol": SYMBOLS
        }
    }
    ws.send(json.dumps(sub_msg))
    print("📨 已发送订阅请求:", sub_msg)

def on_message(ws, message):

    # print("📩 收到消息:", message)
    data = json.loads(message)
    print(data)

    # 示例字段说明（ticker 数据结构）：
    # 'bid'       : 买一价格（Best Bid）
    # 'bidSize'   : 买一挂单量
    # 'ask'       : 卖一价格（Best Ask）
    # 'askSize'   : 卖一挂单量
    # 'last'      : 最新成交价
    # 'symbol'    : 交易对名称（如 BTC/USD）

    # if data.get("channel") == "ticker" and "data" in data:
    #     ticker = data["data"]
    #     symbol = data.get("symbol", "unknown")
    #     print(f"📊 {symbol} | 买一: {ticker['bid']} ({ticker['bidSize']}) | 卖一: {ticker['ask']} ({ticker['askSize']})")

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json

WS_URL = "wss://www.lbkex.net/ws/V2/"
SYMBOLS = ["btc_usdt", "eth_usdt", "sol_usdt", "ltc_usdt", "xrp_usdt"]

def on_open(ws):
    print("✅ 已连接 LBank WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "action": "subscribe",
            "subscribe": "depth",  # ✅ 订阅深度数据
            "depth": "1",          # ✅ 只请求前 1 档（买一卖一）
            "pair": symbol         # ✅ 交易对格式为 xxx_yyy
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 depth:{symbol}")

def on_message(ws, message):
    data = json.loads(message)

    # ✅ 示例字段说明（depth 数据结构）：
    # 'depth': {
    #     'bids': [ [price, amount], ... ]  # 买一挂单列表（按价格降序）
    #     'asks': [ [price, amount], ... ]  # 卖一挂单列表（按价格升序）
    # }
    # 'pair': 交易对名称，如 'btc_usdt'

    if data.get("type") == "depth" and "depth" in data:
        symbol = data.get("pair", "unknown")
        bids = data["depth"].get("bids", [])
        asks = data["depth"].get("asks", [])

        # 提取买一和卖一
        bid_price, bid_amount = bids[0] if bids else ("-", "-")
        ask_price, ask_amount = asks[0] if asks else ("-", "-")

        print(f"📊 {symbol} | 买一: {bid_price} ({bid_amount}) | 卖一: {ask_price} ({ask_amount})")

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json
import time

WS_URL = "wss://contract.mexc.com/edge"
CONTRACTS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "LTC_USDT"]

def on_open(ws):
    print("✅ 已连接 MEXC 合约 WebSocket")

    for symbol in CONTRACTS:
        sub_msg = {
            "method": "sub.ticker",
            "param": {
                "symbol": symbol
            }
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: sub.ticker → {symbol}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ 示例字段说明（push.ticker 推送结构）：
        # 'ask1': 卖一价格
        # 'bid1': 买一价格
        # 'symbol': 合约名称，如 BTC_USDT

        if data.get("channel") == "push.ticker" and "data" in data:
            ticker = data["data"]
            symbol = ticker.get("symbol", "unknown")
            bid_price = ticker.get("bid1", "-")
            ask_price = ticker.get("ask1", "-")
            print(f"📊 {symbol} | 买一: {bid_price} | 卖一: {ask_price}")

    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ WebSocket 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json
import zlib

WS_URL = "wss://ws.okx.com:8443/ws/v5/public"
SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]


def on_open(ws):
    print("✅ 已连接 OKX WebSocket")

    # 构造订阅消息
    sub_msg = {
        "op": "subscribe",
        "args": [{"channel": "tickers", "instId": symbol} for symbol in SYMBOLS]
    }
    ws.send(json.dumps(sub_msg))
    print("📨 已发送订阅请求:", sub_msg)

def on_message(ws, message):
    try:
        # data = inflate(message)
        msg = json.loads(message)

        # 示例字段说明（ticker 数据结构）：
        # 'bidPx'   : 买一价格（Best Bid）
        # 'bidSz'   : 买一挂单量
        # 'askPx'   : 卖一价格（Best Ask）
        # 'askSz'   : 卖一挂单量
        # 'last'    : 最新成交价

        if "data" in msg:
            for ticker in msg["data"]:
                symbol = ticker["instId"]
                print(f"📊 {symbol} | 买一: {ticker['bidPx']} ({ticker['bidSz']}) | 卖一: {ticker['askPx']} ({ticker['askSz']})")
    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json

WS_URL = "wss://api.ox.fun/v2/websocket"
CONTRACTS = ["BTC-USD-SWAP-LIN", "ETH-USD-SWAP-LIN", "SOL-USD-SWAP-LIN", "XRP-USD-SWAP-LIN", "LTC-USD-SWAP-LIN"]
import time

def on_open(ws):
    print("✅ 已连接 OX.FUN WebSocket")

    for symbol in CONTRACTS:
        sub_msg = {
            "op": "subscribe",
            "args": [f"depth:{symbol}"]
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: depth → {symbol}")
        time.sleep(0.5)  # ✅ 每次订阅之间延迟 500ms


def on_message(ws, message):
    try:
        data = json.loads(message)

        print(data)  # 打印原始消息以便调试

        # ✅ 示例字段说明（depth 推送结构）：
        # 'bids': [ [价格, 数量], ... ]
        # 'asks': [ [价格, 数量], ... ]
        # 'instrument': 合约名称，如 BTC-USD-SWAP-LIN

        if "channel" in data and data["channel"].startswith("depth") and "data" in data:
            symbol = data.get("instrument", "unknown")
            bids = data["data"].get("bids", [])
            asks = data["data"].get("asks", [])

            bid_price, bid_qty = bids[0] if bids else ("-", "-")
            ask_price, ask_qty = asks[0] if asks else ("-", "-")

            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ WebSocket 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
import websocket
import json

# ✅ 正确 WebSocket 地址（不能添加路径或参数）
WS_URL = "wss://ws.phemex.com"
CONTRACTS = ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "LTCUSD"]

def on_open(ws):
    print("✅ 已连接 Phemex 合约 WebSocket")

    for i, symbol in enumerate(CONTRACTS):
        # ✅ 使用 orderbook.subscribe 方法订阅合约深度数据
        sub_msg = {
            "id": i + 1,
            "method": "orderbook.subscribe",
            "params": [symbol]
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: orderbook.subscribe → {symbol}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        print(data)  # 打印原始消息以便调试

        # ✅ 示例字段说明（推送结构）：
        # 'asks': [ [价格, 数量], ... ] → 卖单列表（升序）
        # 'bids': [ [价格, 数量], ... ] → 买单列表（降序）
        # 'symbol': 合约名称，如 BTCUSD

        if all(k in data for k in ("symbol", "asks", "bids")):
            symbol = data["symbol"]
            bid_price, bid_qty = data["bids"][0] if data["bids"] else ("-", "-")
            ask_price, ask_qty = data["asks"][0] if data["asks"] else ("-", "-")

            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ WebSocket 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
