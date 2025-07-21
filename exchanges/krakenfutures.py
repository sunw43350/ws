import asyncio
import websockets
import json

URL = "wss://futures.kraken.com/ws/v1"

# 要订阅的合约 ID，例如：永续 BTC/USD
# PRODUCT_IDS = ["PI_XBTUSD"]

PRODUCT_IDS = ["PI_XBTUSD", "PI_ETHUSD", "PI_SOLUSD", "PI_XRPUSD", "PI_LTCUSD"]  # Kraken Futures 合约格式

# 可选的 feed 类型：ticker, trade, book, spread, heartbeat
FEEDS = [
    "ticker",
    "trade",
    "book"
]

async def subscribe(ws, feed, product_ids):
    sub_msg = {
        "event": "subscribe",
        "feed": feed,
        "product_ids": product_ids
    }
    await ws.send(json.dumps(sub_msg))
    print(f"Subscribed to {feed} for {product_ids}")

async def heartbeat(ws):
    """每 30 秒发送 ping 保持连接活跃"""
    while True:
        await ws.send(json.dumps({"event": "ping"}))
        await asyncio.sleep(30)

async def handler():
    async with websockets.connect(URL) as ws:
        # 订阅多个 feed
        for feed in FEEDS:
            await subscribe(ws, feed, PRODUCT_IDS)

        # 启动 ping 心跳
        asyncio.create_task(heartbeat(ws))

        # 接收数据
        async for msg in ws:
            try:
                data = json.loads(msg)
                feed = data.get("feed")
                if feed in FEEDS:
                    print(json.dumps(data, indent=2))
            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    asyncio.run(handler())
