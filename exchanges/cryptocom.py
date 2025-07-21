import websocket
import json

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
