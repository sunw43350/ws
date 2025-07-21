import websocket
import json

WS_URL = "wss://api.whitebit.com/ws"

# 要订阅的交易对（格式为：BASE_QUOTE）
SYMBOLS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "LTC_USDT"]

def on_open(ws):
    print("✅ 已连接 WhiteBIT WebSocket")

    # 构造订阅消息
    subscribe_msg = {
        "id": 1,
        "method": "lastprice_subscribe",
        "params": SYMBOLS
    }
    ws.send(json.dumps(subscribe_msg))
    print("📨 已发送订阅请求:", subscribe_msg)

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

