import websocket
import json
import gzip

# ✅ KuCoin Futures WebSocket 地址（公共频道）
WS_URL = "wss://futures-api.ws.kucoin.com/"

# ✅ 要订阅的合约（产品 ID）
SYMBOLS = ["XBTUSDM", "ETHUSDM", "SOLUSDM", "LTCUSDM", "XRPUSDM"]

def on_open(ws):
    print("✅ 已连接 KuCoin Futures WebSocket")

    for i, symbol in enumerate(SYMBOLS):
        sub_msg = {
            "id": str(i + 1),
            "type": "subscribe",
            "topic": f"/contractMarket/ticker:{symbol}",
            "privateChannel": False,
            "response": True
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 ticker:{symbol}")

def on_message(ws, message):
    try:
        # 🔄 KuCoin Futures 返回的是 gzip 压缩数据，需先解压
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        # 📊 示例字段说明（ticker 数据结构）：
        # 'bestBidPrice' : 买一价格（Best Bid）
        # 'bestBidSize'  : 买一挂单量
        # 'bestAskPrice' : 卖一价格（Best Ask）
        # 'bestAskSize'  : 卖一挂单量
        # 'price'        : 最新成交价（Last Trade Price）
        # 'symbol'       : 合约代码（如 XBTUSDM）

        if "data" in data and "topic" in data:
            ticker = data["data"]
            symbol = ticker.get("symbol", "unknown")
            print(f"📊 {symbol} | 买一: {ticker['bestBidPrice']} ({ticker['bestBidSize']}) | 卖一: {ticker['bestAskPrice']} ({ticker['bestAskSize']})")

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
