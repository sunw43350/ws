import websocket
import json

WS_URL = "wss://api.ox.fun/v2/websocket"
CONTRACTS = ["BTC-USD-SWAP-LIN", "ETH-USD-SWAP-LIN", "SOL-USD-SWAP-LIN", "XRP-USD-SWAP-LIN", "LTC-USD-SWAP-LIN"]
import time

def on_open(ws):
    print("✅ 已连接 OX.FUN WebSocket")

    for symbol in CONTRACTS:
        sub_msg = {
            "op": "subscribe",
            "args": [f"depth:{symbol}"]
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: depth → {symbol}")
        time.sleep(0.5)  # ✅ 每次订阅之间延迟 500ms


def on_message(ws, message):
    try:
        data = json.loads(message)

        print(data)  # 打印原始消息以便调试

        # ✅ 示例字段说明（depth 推送结构）：
        # 'bids': [ [价格, 数量], ... ]
        # 'asks': [ [价格, 数量], ... ]
        # 'instrument': 合约名称，如 BTC-USD-SWAP-LIN

        if "channel" in data and data["channel"].startswith("depth") and "data" in data:
            symbol = data.get("instrument", "unknown")
            bids = data["data"].get("bids", [])
            asks = data["data"].get("asks", [])

            bid_price, bid_qty = bids[0] if bids else ("-", "-")
            ask_price, ask_qty = asks[0] if asks else ("-", "-")

            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

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
