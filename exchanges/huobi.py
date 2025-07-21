import websocket
import gzip
import json

WS_URL = "wss://api.huobi.pro/ws"
SYMBOLS = ["btcusdt", "ethusdt", "solusdt", "ltcusdt", "xrpusdt"]


# bid, b, best_bid_price	买一价格（当前市场中最高买价）
# bidSize, bs, best_bid_volume	买一挂单数量（买一对应挂单量）
# ask, k, best_ask_price	卖一价格（当前市场中最低卖价）
# askSize, ks, best_ask_volume	卖一挂单数量（卖一对应挂单量）


def on_open(ws):
    print("✅ 已连接 Huobi WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "sub": f"market.{symbol}.ticker",
            "id": symbol
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: market.{symbol}.ticker")

def on_message(ws, message):
    try:
        data = gzip.decompress(message).decode("utf-8")
        msg = json.loads(data)

        if "ping" in msg:
            pong = {"pong": msg["ping"]}
            ws.send(json.dumps(pong))
        else:
            print("📩 收到消息:", msg)
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
