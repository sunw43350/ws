import asyncio
import websockets
import json

WS_URL = "wss://api.paradex.trade/v1/ws"

async def subscribe_ticker():
    async with websockets.connect(WS_URL) as ws:
        print("✅ WebSocket 连接成功")
        # 订阅两个合约
        for symbol in ["ETH-USD", "BTC-USD"]:
            sub_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "subscribe",
                "params": {
                    "channel": "ticker",
                    "symbol": symbol
                }
            }
            await ws.send(json.dumps(sub_msg))
        while True:
            message = await ws.recv()
            print(message)

if __name__ == "__main__":
    asyncio.run(subscribe_ticker())