import websocket
import json
import gzip

# ✅ 正确的 WebSocket 地址
WS_URL = "wss://open-api-ws.bingx.com/market"

# ✅ BingX 支持的交易对格式（务必大写，如 BTC-USDT）
SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]

def on_open(ws):
    print("✅ 已连接 BingX WebSocket")

    # ✅ 按官方格式发送订阅请求：使用 reqType 和 dataType
    for i, symbol in enumerate(SYMBOLS):
        sub_msg = {
            "id": f"depth-{i+1}",                # 唯一标识符
            "reqType": "sub",                    # 订阅类型
            "dataType": f"{symbol}@depth20"      # ✅ 订阅前 20 档深度，@depth、@depth20、@depth100 均可
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: {sub_msg['dataType']}")

def on_message(ws, message):
    try:
        # ✅ BingX 返回的是 Gzip 压缩字节流，需解压
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        # ✅ 示例字段说明（depth 推送结构）：
        # 'data': {
        #   'bids': [ [价格, 数量], ... ]   → 买一挂单列表（降序）
        #   'asks': [ [价格, 数量], ... ]   → 卖一挂单列表（升序）
        # }
        # 'dataType': 如 'BTC-USDT@depth20'

        if "data" in data and "dataType" in data:
            symbol = data["dataType"].split("@")[0]
            bids = data["data"].get("bids", [])
            asks = data["data"].get("asks", [])

            bid_price, bid_qty = bids[0] if bids else ("-", "-")
            ask_price, ask_qty = asks[0] if asks else ("-", "-")

            print(f"📊 {symbol} | 买一: {bid_price} ({bid_qty}) | 卖一: {ask_price} ({ask_qty})")

    except Exception as e:
        print("❌ 解压或解析失败:", e)

def on_error(ws, error):
    print("❌ WebSocket 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    # ✅ 启动 WebSocket 客户端
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
