import asyncio
import websockets
import json

BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

# 要订阅的合约交易对（USDT本位）
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "ADAUSDT"]

async def subscribe_bybit_tickers():
    async with websockets.connect(BYBIT_WS_URL) as ws:
        print("✅ Connected to Bybit WebSocket")

        # 构造订阅请求
        subscribe_msg = {
            "op": "subscribe",
            "args": [f"tickers.{symbol}" for symbol in SYMBOLS]
        }
        await ws.send(json.dumps(subscribe_msg))
        print("📨 Sent subscription:", subscribe_msg)

        # 持续接收消息
        while True:
            message = await ws.recv()
            try:
                data = json.loads(message)
                # 可根据需要过滤 tickers 消息处理
                print("📩 Received:", json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print("❌ Failed to decode message:", message)

# 运行主程序
if __name__ == "__main__":
    try:
        asyncio.run(subscribe_bybit_tickers())
    except KeyboardInterrupt:
        print("🚪 Exit on user interrupt")
