import websocket
import json

WS_URL = "wss://ws.kraken.com/v2"
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

    print("📩 收到消息:", message)
    data = json.loads(message)

    # 示例字段说明（ticker 数据结构）：
    # 'bid'       : 买一价格（Best Bid）
    # 'bidSize'   : 买一挂单量
    # 'ask'       : 卖一价格（Best Ask）
    # 'askSize'   : 卖一挂单量
    # 'last'      : 最新成交价
    # 'symbol'    : 交易对名称（如 BTC/USD）

    if data.get("channel") == "ticker" and "data" in data:
        ticker = data["data"]
        symbol = data.get("symbol", "unknown")
        print(f"📊 {symbol} | 买一: {ticker['bid']} ({ticker['bidSize']}) | 卖一: {ticker['ask']} ({ticker['askSize']})")

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
