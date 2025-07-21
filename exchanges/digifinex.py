import asyncio
import websockets
import zlib
import json

WS_URL = "wss://openapi.digifinex.com/swap_ws/v2/"


def decompress_message(message: bytes) -> str:
    """解压 gzip binary message"""
    inflated = zlib.decompress(message) 
    return inflated.decode('utf-8')


async def subscribe_ticker():
    async with websockets.connect(WS_URL) as ws:
        print("✅ WebSocket 连接成功")

        # 订阅 ticker 数据
        sub_msg = {
            "event": "ticker.subscribe",
            "id": 1,
            "instrument_ids": ["BTCUSDTPERP", "ETHUSDTPERP"]
        }
        await ws.send(json.dumps(sub_msg))

        # 发送 ping（可选）
        await ws.send(json.dumps({"id": 1, "event": "server.ping"}))

        while True:
            message = await ws.recv()

            if isinstance(message, bytes):
                try:
                    text = decompress_message(message)
                    print("📩 收到解压消息:", text)
                except Exception as e:
                    print("❌ 解压失败:", e)
            else:
                print("📝 收到文本消息:", message)


if __name__ == "__main__":
    asyncio.run(subscribe_ticker())
