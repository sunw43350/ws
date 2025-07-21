import websocket
import json
import gzip

WS_URL = "wss://open-api-ws.bingx.com/market"
SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]

def on_open(ws):
    print("✅ 已连接 BingX WebSocket")

    for i, symbol in enumerate(SYMBOLS):
        sub_msg = {
            "id": f"depth-{i+1}",
            "dataType": f"{symbol}@depth1"  # ✅ 订阅前 1 档深度数据
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: {sub_msg['dataType']}")

def on_message(ws, message):
    try:
        # BingX 返回 GZIP 压缩数据
        print(message[:100])  # 打印前100个字符以检查数据
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        # ✅ 示例字段说明（depth 数据结构）：
        # 'bids': [ [price, quantity], ... ]  # 买一挂单列表（按价格降序）
        # 'asks': [ [price, quantity], ... ]  # 卖一挂单列表（按价格升序）
        # 'dataType': 如 BTC-USDT@depth1

        if "data" in data and "dataType" in data:
            symbol = data["dataType"].split("@")[0]
            bids = data["data"].get("bids", [])
            asks = data["data"].get("asks", [])

            bid_price, bid_qty = bids[0] if bids else ("-", "-")
            ask_price, ask_qty = asks[0] if asks else ("-", "-")

            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

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
