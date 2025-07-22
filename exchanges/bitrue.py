import asyncio, json, websockets

WS_FUTURES = "wss://fapiws.bitrue.com"
SYMBOLS = ["btcusdt","ethusdt","solusdt","xrpusdt","ltcusdt"]

async def subscribe_futures(ws, symbol):
    params = {"event":"sub","params":{"channel":f"market_{symbol}_ticker","cb_id":symbol}}
    await ws.send(json.dumps(params))
    print(f"✅ subscribed futures ticker: {symbol}")

async def main():
    async with websockets.connect(WS_FUTURES) as ws:
        for s in SYMBOLS:
            await subscribe_futures(ws, s)
        async for msg in ws:
            print("📩", json.loads(msg))

asyncio.run(main())
