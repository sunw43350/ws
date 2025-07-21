import websocket
import json
import gzip
import base64

WS_URL = "wss://xtsocket.xt.com/websocket"
CONTRACTS = ["btc_usdt", "eth_usdt", "sol_usdt", "xrp_usdt", "ltc_usdt"]

def decode_xt_message(message):
    try:
        decoded = base64.b64decode(message)
        decompressed = gzip.decompress(decoded).decode("utf-8")
        return json.loads(decompressed)
    except Exception as e:
        print("❌ 解码失败:", e)
        return None

def on_open(ws):
    print("✅ 已连接 XT WebSocket")

    for symbol in CONTRACTS:
        sub_msg = {
            "channel": "ex_depth_data",
            "market": symbol,
            "event": "addChannel"
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: ex_depth_data → {symbol}")

def on_message(ws, message):
    data = decode_xt_message(message)
    if not data or data.get("channel") != "ex_depth_data":
        return

    market = data.get("data", {}).get("market", "unknown")
    bids = data["data"].get("bids", [])
    asks = data["data"].get("asks", [])

    bid_price, bid_qty = bids[0] if bids else ("-", "-")
    ask_price, ask_qty = asks[0] if asks else ("-", "-")

    print(f"📊 {market.upper()} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

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
