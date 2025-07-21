import asyncio
import json
import time
import websockets

from connectors.base import BaseAsyncConnector
from models.base import SubscriptionRequest, MarketSnapshot

class Connector(BaseAsyncConnector):
    def __init__(self):
        super().__init__("ascendex")
        self.ws = None
        self.symbols = ["BTC-PERP", "ETH-PERP", "SOL-PERP", "XRP-PERP", "LTC-PERP"]

    async def connect(self):
        url = "wss://ascendex.com/1/api/pro/v2/stream"
        self.ws = await websockets.connect(url)
        print("✅ AscendEX WebSocket 已连接")

    async def subscribe(self, request: SubscriptionRequest):
        # AscendEX 使用 depth:{symbol}:0 频道获取买一卖一
        sub_msg = {
            "op": "sub",
            "id": f"depth_{request.symbol}",
            "ch": f"depth:{request.symbol}:0"
        }
        await self.ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: depth → {request.symbol}")

    async def run(self):
        await self.connect()

        # 批量订阅所有合约
        for symbol in self.symbols:
            req = SubscriptionRequest(symbol=symbol, channel="depth")
            await self.subscribe(req)
            await asyncio.sleep(0.3)  # 控制订阅速率

        while True:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)

                if data.get("m") == "depth" and "symbol" in data:
                    symbol = data["symbol"]
                    bids = data.get("data", {}).get("bids", [])
                    asks = data.get("data", {}).get("asks", [])

                    bid_price, bid_qty = bids[0] if bids else ("-", "-")
                    ask_price, ask_qty = asks[0] if asks else ("-", "-")

                    snapshot = MarketSnapshot(
                        exchange=self.exchange_name,
                        symbol=symbol,
                        best_bid=float(bid_price),
                        best_ask=float(ask_price),
                        timestamp=time.time()
                    )

                    print(f"📊 {snapshot.symbol} | 买一: {snapshot.best_bid} | 卖一: {snapshot.best_ask}")

            except Exception as e:
                print(f"❌ AscendEX 解码失败: {e}")
                await asyncio.sleep(1)
