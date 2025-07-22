import asyncio
import json
import websockets

BITRUE_FUTURES_WS = "wss://fapiws.bitrue.com"
SYMBOLS = ["btcusdt", "ethusdt", "solusdt", "xrpusdt", "ltcusdt"]

async def subscribe_depth(ws, symbol):
    params = {
        "event": "sub",
        "params": {
            "channel": f"market_{symbol}_depth_step0",
            "cb_id": symbol
        }
    }
    await ws.send(json.dumps(params))
    print(f"✅ 已订阅深度: {symbol}")

async def handle_messages(ws):
    while True:
        try:
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"📩 收到: {data}")
        except Exception as e:
            print(f"❌ 错误: {e}")
            break

async def ping(ws):
    while True:
        try:
            await asyncio.sleep(15)
            await ws.send("pong")  # Bitrue 需要定期回复 pong
        except Exception as e:
            print(f"⚠️ ping 失败: {e}")
            break

async def main():
    async with websockets.connect(BITRUE_FUTURES_WS) as ws:
        # 订阅所有 symbol 的深度
        for symbol in SYMBOLS:
            await subscribe_depth(ws, symbol)

        # 并发处理消息与 ping
        await asyncio.gather(
            handle_messages(ws),
            ping(ws)
        )

if __name__ == "__main__":
    asyncio.run(main())
