import websocket
import json
import time

WS_URL = "wss://api.hyperliquid.xyz/ws"
CONTRACTS = ["BTC-PERP", "ETH-PERP", "SOL-PERP", "XRP-PERP", "LTC-PERP"]

def on_open(ws):
    print("✅ 已连接 Hyperliquid WebSocket")

    for symbol in CONTRACTS:
        # sub_msg = {
        #     "type": "subscribe",
        #     "channels": [
        #         {
        #             "type": "allMids",
        #             "coin": symbol.split("-")[0]  # ✅ 提取 coin 名称，如 BTC
        #         }
        #     ]
        # }
        sub_msg = {
            "type": "subscribe",
            "channel": "allMids"
        }
        ws.send(json.dumps(sub_msg))


        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: allMids → {symbol}")
        time.sleep(0.3)  # 控制订阅速率，避免触发限速

def on_message(ws, message):
    try:
        data = json.loads(message)
        print(data)  # 打印原始消息以便调试

        # ✅ 示例字段说明（allMids 推送结构）：
        # 'coin': 合约币种，如 BTC
        # 'bestBid': 买一价格
        # 'bestAsk': 卖一价格

        if data.get("channel") == "allMids":
            coin = data.get("coin", "unknown")
            bid = data.get("bestBid", "-")
            ask = data.get("bestAsk", "-")
            print(f"📊 {coin}-PERP | 买一: {bid} | 卖一: {ask}")

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
