import websocket
import json
import time

WS_URL = "wss://ascendex.com/1/api/pro/v2/stream"
CONTRACTS = ["BTC-PERP", "ETH-PERP", "SOL-PERP", "XRP-PERP", "LTC-PERP"]

def on_open(ws):
    print("✅ 已连接 AscendEX WebSocket")

    for i, symbol in enumerate(CONTRACTS):
        sub_msg = {
            "op": "sub",
            "id": f"ticker_{i}",
            "ch": f"ticker:{symbol}"
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: ticker → {symbol}")
        time.sleep(0.3)  # 控制订阅速率，避免触发限速

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ 示例字段说明（ticker 推送结构）：
        # 'm': 'ticker'
        # 'symbol': 合约名称，如 BTC-PERP
        # 'bid': 买一价格
        # 'ask': 卖一价格

        if data.get("m") == "ticker":
            symbol = data.get("symbol", "unknown")
            bid = data.get("bid", "-")
            ask = data.get("ask", "-")
            print(f"📊 {symbol} | 买一: {bid} | 卖一: {ask}")

    except Exception as e:
        print(f"❌ 解码失败: {e}")

def on_error(ws, error):
    print(f"❌ WebSocket 错误: {error}")

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
