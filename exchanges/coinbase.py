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
