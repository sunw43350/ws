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
