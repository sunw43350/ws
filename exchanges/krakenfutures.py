import asyncio
import websockets
import json

URL = "wss://futures.kraken.com/ws/v1"

# 支持的 product_id，比如 PI_XBTUSD 表示 BTC/USD 永续合约
PRODUCT_IDS = ["PI_XBTUSD", "PI_ETHUSD"]

async def subscribe_ticker(ws, product_ids):
    msg = {
        "event": "subscribe",
        "feed": "ticker",
        "product_ids": product_ids
    }
    await ws.send(json.dumps(msg))
    print("Subscribed to ticker:", product_ids)

async def heartbeat(ws):
    while True:
        await ws.send(json.dumps({"event": "ping"}))
        await asyncio.sleep(30)

async def handler():
    async with websockets.connect(URL) as ws:
        await subscribe_ticker(ws, PRODUCT_IDS)
        asyncio.create_task(heartbeat(ws))

        async for msg in ws:
            try:
                data = json.loads(msg)
                if data.get("feed") == "ticker":
                    symbol = data["product_id"]
                    bid = data["bid"]
                    ask = data["ask"]
                    ts = data.get("timestamp")
                    print(f"[{symbol}] bid: {bid} | ask: {ask} | ts: {ts}")
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    asyncio.run(handler())
