import websocket
import json

WS_URL = "wss://ws.coincatch.com/market"  # 示例地址，请替换为 CoinCatch 实际 WebSocket 地址
SYMBOLS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "LTC_USDT"]

def on_open(ws):
    print("✅ 已连接 CoinCatch WebSocket")

    for i, symbol in enumerate(SYMBOLS):
        sub_msg = {
            "id": i + 1,
            "method": "subscribe",
            "params": {
                "channel": f"ticker.{symbol}"
            }
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 ticker.{symbol}")

def on_message(ws, message):
    data = json.loads(message)

    # 假设返回结构如下（字段说明见下方注释）：
    # {
    #   "channel": "ticker.BTC_USDT",
    #   "data": {
    #     "bid": 最优买价（Best Bid）
    #     "bid_size": 买一挂单量
    #     "ask": 最优卖价（Best Ask）
    #     "ask_size": 卖一挂单量
    #     "last_price": 最新成交价
    #     ...
    #   }
    # }

    if "data" in data:
        ticker = data["data"]
        symbol = data.get("channel", "unknown").split(".")[-1]
        print(f"📊 {symbol} | 买一: {ticker['bid']} ({ticker['bid_size']}) | 卖一: {ticker['ask']} ({ticker['ask_size']})")

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
