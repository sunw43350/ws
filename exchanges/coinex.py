import websocket
import json
import gzip

WS_URL = "wss://socket.coinex.com/"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "LTCUSDT"]

def on_open(ws):
    print("✅ 已连接 CoinEx WebSocket")

    for i, symbol in enumerate(SYMBOLS):
        sub_msg = {
            "id": i + 1,
            "method": "state.subscribe",
            "params": [symbol]
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 ticker.{symbol}")

def on_message(ws, message):
    try:
        # CoinEx 返回 gzip 压缩数据
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        # 示例字段说明（ticker 数据结构）：
        # 'ticker': {
        #     'buy': 买一价格（Best Bid）
        #     'buy_amount': 买一挂单量
        #     'sell': 卖一价格（Best Ask）
        #     'sell_amount': 卖一挂单量
        #     'last': 最新成交价
        #     'vol': 24h 成交量
        #     ...
        # }

        if "ticker" in data.get("params", {}):
            ticker = data["params"]["ticker"]
            symbol = data["params"]["market"]
            print(f"📊 {symbol} | 买一: {ticker['buy']} ({ticker['buy_amount']}) | 卖一: {ticker['sell']} ({ticker['sell_amount']})")

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
