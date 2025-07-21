import websocket
import json

WS_URL = "wss://futures.kraken.com/ws/v1"
SYMBOLS = ["PI_XBTUSD", "PI_ETHUSD", "PI_SOLUSD", "PI_LTCUSD", "PI_XRPUSD"]

def on_open(ws):
    print("✅ 已连接 Kraken Futures WebSocket")

    # 构造订阅消息
    sub_msg = {
        "event": "subscribe",
        "feed": "ticker",
        "product_ids": SYMBOLS
    }
    ws.send(json.dumps(sub_msg))
    print("📨 已发送订阅请求:", sub_msg)

def on_message(ws, message):
    data = json.loads(message)

    # 示例字段说明（ticker 数据结构）：
    # 'bid'       : 买一价格（Best Bid）
    # 'bidSize'   : 买一挂单量
    # 'ask'       : 卖一价格（Best Ask）
    # 'askSize'   : 卖一挂单量
    # 'last'      : 最新成交价
    # 'product_id': 合约名称（如 PI_XBTUSD）

    if data.get("feed") == "ticker":
        symbol = data.get("product_id", "unknown")
        print(f"📊 {symbol} | 买一: {data['bid']} ({data['bidSize']}) | 卖一: {data['ask']} ({data['askSize']})")

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
