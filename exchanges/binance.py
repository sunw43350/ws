import asyncio
import websockets
import json

# 构建订阅的合约列表
SYMBOLS = ["btcusdt", "ethusdt", "solusdt", "bnbusdt", "adausdt"]
STREAMS = [f"{symbol}@ticker" for symbol in SYMBOLS]

# 拼接成组合流地址
STREAM_URL = f"wss://stream.binance.com:9443/stream?streams={'/'.join(STREAMS)}"

async def binance_ws():
    async with websockets.connect(STREAM_URL) as ws:
        print("✅ 已连接 Binance WebSocket，订阅以下合约:")
        for s in SYMBOLS:
            print(f"🔔 {s.upper()} @ticker")

        while True:
            message = await ws.recv()
            try:
                data = json.loads(message)
                stream = data.get("stream")
                payload = data.get("data")

                if payload:
                    symbol = payload.get("s")
                    price = payload.get("c")  # 最新成交价
                    print(f"📈 {symbol} 最新价格: {price}")
            except Exception as e:
                print("❌ 解码错误:", e)
                print("原始消息:", message)

if __name__ == "__main__":
    try:
        asyncio.run(binance_ws())
    except KeyboardInterrupt:
        print("🚪 用户终止连接")
