import websocket
import json

WS_URL = "wss://phemex.com/ws"
CONTRACTS = ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "LTCUSD"]

def on_open(ws):
    print("✅ 已连接 Phemex WebSocket")

    for i, symbol in enumerate(CONTRACTS):
        sub_msg = {
            "id": i + 1,
            "method": "orderbook.subscribe",
            "params": [symbol]
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: orderbook.subscribe → {symbol}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ 示例字段说明（orderBook10 推送结构）：
        # 'asks': [ [价格, 数量], ... ] → 卖单列表（升序）
        # 'bids': [ [价格, 数量], ... ] → 买单列表（降序）
        # 'symbol': 合约名称，如 BTCUSD

        if "asks" in data and "bids" in data and "symbol" in data:
            symbol = data["symbol"]
            bid_price, bid_qty = data["bids"][0] if data["bids"] else ("-", "-")
            ask_price, ask_qty = data["asks"][0] if data["asks"] else ("-", "-")
            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

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
