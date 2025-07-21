import websocket
import json
import time

WS_URL = "wss://contract.mexc.com/edge"
CONTRACTS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "LTC_USDT"]

def on_open(ws):
    print("✅ 已连接 MEXC 合约 WebSocket")

    for symbol in CONTRACTS:
        sub_msg = {
            "method": "sub.ticker",
            "param": {
                "symbol": symbol
            }
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: sub.ticker → {symbol}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ 示例字段说明（push.ticker 推送结构）：
        # 'ask1': 卖一价格
        # 'bid1': 买一价格
        # 'symbol': 合约名称，如 BTC_USDT

        if data.get("channel") == "push.ticker" and "data" in data:
            ticker = data["data"]
            symbol = ticker.get("symbol", "unknown")
            bid_price = ticker.get("bid1", "-")
            ask_price = ticker.get("ask1", "-")
            print(f"📊 {symbol} | 买一: {bid_price} | 卖一: {ask_price}")

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
