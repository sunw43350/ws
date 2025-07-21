import websocket
import json
import time

WS_URL = "wss://api.gateio.ws/ws/v4/"
SYMBOLS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "LTC_USDT"]

def on_open(ws):
    print("✅ 已连接 Gate.io WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "time": int(time.time()),
            "channel": "spot.order_book",
            "event": "subscribe",
            "payload": [symbol]
        }
        sub_msg = {
            "time": int(time.time()),
            "channel": "spot.order_book",
            "event": "subscribe",
            "payload": [symbol, "1000ms", "20"]
        }

        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: spot.order_book → {symbol}")


def on_message(ws, message):
    try:
        # Gate.io 返回 gzip 压缩数据
        # decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(message)
        print(data)

        # ✅ 示例字段说明（order_book 推送结构）：
        # 'result': {
        #   'bids': [ [价格, 数量], ... ]
        #   'asks': [ [价格, 数量], ... ]
        # }
        # 'channel': 'spot.order_book'
        # 'event': 'update'

        if data.get("channel") == "spot.order_book" and data.get("event") == "update":
            symbol = data.get("result", {}).get("currency_pair", "unknown")
            bids = data["result"].get("bids", [])
            asks = data["result"].get("asks", [])

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
