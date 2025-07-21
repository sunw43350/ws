import websocket
import json

WS_URL = "wss://www.lbkex.net/ws/V2/"
SYMBOLS = ["btc_usdt", "eth_usdt", "sol_usdt", "ltc_usdt", "xrp_usdt"]

def on_open(ws):
    print("✅ 已连接 LBank WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "action": "subscribe",
            "subscribe": "depth",  # ✅ 订阅深度数据
            "depth": "1",          # ✅ 只请求前 1 档（买一卖一）
            "pair": symbol         # ✅ 交易对格式为 xxx_yyy
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 depth:{symbol}")

def on_message(ws, message):
    data = json.loads(message)

    # ✅ 示例字段说明（depth 数据结构）：
    # 'depth': {
    #     'bids': [ [price, amount], ... ]  # 买一挂单列表（按价格降序）
    #     'asks': [ [price, amount], ... ]  # 卖一挂单列表（按价格升序）
    # }
    # 'pair': 交易对名称，如 'btc_usdt'

    if data.get("type") == "depth" and "depth" in data:
        symbol = data.get("pair", "unknown")
        bids = data["depth"].get("bids", [])
        asks = data["depth"].get("asks", [])

        # 提取买一和卖一
        bid_price, bid_amount = bids[0] if bids else ("-", "-")
        ask_price, ask_amount = asks[0] if asks else ("-", "-")

        print(f"📊 {symbol} | 买一: {bid_price} ({bid_amount}) | 卖一: {ask_price} ({ask_amount})")

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
