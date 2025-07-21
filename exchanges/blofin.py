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
