import websocket
import json
import time

WS_URL = "wss://ws.bitmex.com/realtime"
CONTRACTS = ["XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD", "LTCUSD"]

def on_open(ws):
    print("✅ 已连接 BitMEX WebSocket")

    # ✅ 订阅 quote 和 orderBookL2_25（前 25 档深度）
    sub_msg = {
        "op": "subscribe",
        "args": [f"quote:{symbol}" for symbol in CONTRACTS] +
                [f"orderBookL2_25:{symbol}" for symbol in CONTRACTS]
    }
    ws.send(json.dumps(sub_msg))
    print("📨 已发送订阅请求:", sub_msg)

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ quote 推送结构：买一卖一价格
        if data.get("table") == "quote" and data.get("action") == "insert":
            for quote in data.get("data", []):
                symbol = quote.get("symbol", "unknown")
                bid = quote.get("bidPrice", "-")
                ask = quote.get("askPrice", "-")
                print(f"📊 {symbol} | 买一: {bid} | 卖一: {ask}")

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
