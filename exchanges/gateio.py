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
