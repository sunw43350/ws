import websocket
import json
import time
from threading import Thread

WS_URL = "wss://api.delta.exchange:2096"
CONTRACTS = ["BTCUSD_29Mar", "ETHUSD_29Mar", "SOLUSD_29Mar", "XRPUSD_29Mar", "LTCUSD_29Mar"]

def on_open(ws):
    print("✅ 已连接 Delta Exchange WebSocket")

    sub_msg = {
        "type": "subscribe",
        "payload": {
            "channels": [
                {
                    "name": "l2_orderbook",
                    "symbols": CONTRACTS
                }
            ]
        }
    }
    ws.send(json.dumps(sub_msg))
    print(f"📨 已订阅: l2_orderbook → {', '.join(CONTRACTS)}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ 示例字段说明（l2_orderbook 推送结构）：
        # 'symbol': 合约名称，如 BTCUSD_29Mar
        # 'bids': [ [价格, 数量], ... ]
        # 'asks': [ [价格, 数量], ... ]

        if "symbol" in data and "bids" in data and "asks" in data:
            symbol = data["symbol"]
            bid_price, bid_qty = data["bids"][0] if data["bids"] else ("-", "-")
            ask_price, ask_qty = data["asks"][0] if data["asks"] else ("-", "-")
            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

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
    thread = Thread(target=ws.run_forever)
    thread.daemon = True
    thread.start()

    # 保持主线程运行
    while True:
        time.sleep(5)
