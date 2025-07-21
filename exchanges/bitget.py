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
