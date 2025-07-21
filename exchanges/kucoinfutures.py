import websocket
import json
import time

# ✅ 来自 token 响应的动态 endpoint 和 token
WS_URL = "wss://ws-api-spot.kucoin.com/"
TOKEN = "你的token字符串"  # 请替换为你从 REST API 获取的 token

TOKEN = "2neAiuYvAU61ZDXANAGAsiL4-iAExhsBXZxftpOeh_55i3Ysy2q2LEsEWU64mdzUOPusi34M_wGoSf7iNyEWJ4aBZXpWhrmY9jKtqkdWoFa75w3istPvPtiYB9J6i9GjsxUuhPw3BlrzazF6ghq4L_u0MhKxG3x8TeN4aVbNiYo=.mvnekBb8DJegZIgYLs2FBQ=="

# ✅ 要订阅的交易对（Spot）
SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]

def on_open(ws):
    print("✅ 已连接 KuCoin Spot WebSocket")

    # 🔐 发送鉴权消息（携带 token）
    auth_msg = {
        "id": int(time.time() * 1000),
        "type": "subscribe",
        "topic": "/market/ticker:" + ",".join(SYMBOLS),
        "privateChannel": False,
        "response": True
    }
    ws.send(json.dumps(auth_msg))
    print("📨 已发送订阅请求:", auth_msg)

def on_message(ws, message):
    data = json.loads(message)

    # 📊 示例字段说明（ticker 数据结构）：
    # 'bestBid'     : 买一价格（Best Bid）
    # 'bestAsk'     : 卖一价格（Best Ask）
    # 'price'       : 最新成交价
    # 'sequence'    : 更新序号
    # 'time'        : 时间戳（毫秒）
    # 'symbol'      : 交易对代码（如 BTC-USDT）

    if "data" in data and "topic" in data:
        ticker = data["data"]
        symbol = ticker.get("symbol", "unknown")
        print(f"📊 {symbol} | 买一: {ticker['bestBid']} | 卖一: {ticker['bestAsk']} | 最新价: {ticker['price']}")

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
