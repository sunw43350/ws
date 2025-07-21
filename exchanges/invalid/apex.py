import websocket
import json

WS_URL = "wss://omni.apex.exchange/ws"
CONTRACTS = ["BTC-USDC", "ETH-USDC", "SOL-USDC", "XRP-USDC", "LTC-USDC"]

def on_open(ws):
    print("✅ 已连接 ApeX WebSocket")

    sub_msg = {
        "type": "subscribe",
        "channel": "ticker.v3",
        "instIds": CONTRACTS
    }
    ws.send(json.dumps(sub_msg))
    print(f"📨 已订阅: ticker.v3 → {', '.join(CONTRACTS)}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ 示例字段说明（ticker.v3 推送结构）：
        # 'instId': 合约名称，如 BTC-USDC
        # 'bidPx': 买一价格
        # 'askPx': 卖一价格

        if data.get("channel") == "ticker.v3" and "data" in data:
            for ticker in data["data"]:
                symbol = ticker.get("instId", "unknown")
                bid = ticker.get("bidPx", "-")
                ask = ticker.get("askPx", "-")
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
