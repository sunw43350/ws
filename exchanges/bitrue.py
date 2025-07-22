import websocket
import json
import gzip

# WS_URL = "wss://ws.bitrue.com/kline-api/ws" ## error
WS_URL = "wss://fmarket-ws.bitrue.com/kline-api/ws"

# WS_URL = "wss://futuresws.bitrue.com/kline-api/ws"

	
SYMBOLS = ["btcusdt", "ethusdt", "solusdt", "xrpusdt", "ltcusdt"]

def on_open(ws):
    print("✅ 已连接 Bitrue WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "event": "sub",
            "params": {
                # "channel": f"market_{symbol}_depth_step0",
                "channel": f"market_{symbol}_ticker",
                "cb_id": ""
            }
        }
        # sub_msg = {
        #     "event": "sub",
        #     "params": {
        #         "channel": f"market_{symbol}_depth_step0",  # ✅ 订阅 1档深度数据
        #         "cb_id": symbol
        #     }
        # }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: market_{symbol}_depth_step0")

def on_message(ws, message):
    try:
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        print(data)

        if "ping" in data:
            pong = {"pong": data["ping"]}
            ws.send(json.dumps(pong))
            print(f"🔁 pong sent: {pong['pong']}")

        # ✅ 示例字段说明：
        # 'bids': [ [价格, 数量], ... ] → 买单列表（降序）
        # 'asks': [ [价格, 数量], ... ] → 卖单列表（升序）
        # 'channel': 如 'market_btcusdt_depth_step0'

        # if "channel" in data and "tick" in data:
        #     symbol = data["channel"].split("_")[1]
        #     bids = data["tick"].get("bids", [])
        #     asks = data["tick"].get("asks", [])

        #     bid_price, bid_qty = bids[0] if bids else ("-", "-")
        #     ask_price, ask_qty = asks[0] if asks else ("-", "-")

        #     print(f"📊 {symbol.upper()} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print("❌ 解压失败:", e)

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
