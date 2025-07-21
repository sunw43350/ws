import asyncio
import websockets
import json

BITMART_WS_URL = "wss://openapi-ws-v2.bitmart.com/api?protocol=1.1"


# 订阅的合约交易对（示例）
SYMBOLS = ["BTCUSDT", "ETHUSDT"]

async def subscribe_bitmart():
    async with websockets.connect(BITMART_WS_URL) as ws:
        print("✅ 已连接 BitMart WebSocket")

        # 构造订阅消息
        subscribe_msg = {
            "action": "subscribe",
            "args": [f"futures/ticker:{symbol}" for symbol in SYMBOLS]
        }

        # {
        # "action":"subscribe",
        # "args":["futures/ticker:BTCUSDT"]
        # }
        
        await ws.send(json.dumps(subscribe_msg))
        print("📨 已发送订阅请求:", subscribe_msg)

        while True:
            message = await ws.recv()
            print("📩 收到消息:", message)

if __name__ == "__main__":
    try:
        asyncio.run(subscribe_bitmart())
    except KeyboardInterrupt:
        print("🚪 用户终止连接")
