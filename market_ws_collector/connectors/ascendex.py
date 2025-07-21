import asyncio
import json
import re
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, symbols=None, ws_url=None, queue=None):
        super().__init__()
        self.ws_url = ws_url if ws_url is not None else WS_ENDPOINTS.get("ascendex")
        self.queue = queue
        self.symbols = [self.format_symbol(sym) for sym in (symbols or DEFAULT_SYMBOLS.get("ascendex", []))]
        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        """标准格式 BTC-USDT → AscendEX 合约格式 BTC-PERP"""
        base = re.sub(r"-USDT$", "", generic_symbol.upper())
        return f"{base}-PERP"

    def build_sub_msg(self, symbol: str) -> dict:
        """构造订阅消息"""
        return {
            "op": "sub",
            "id": f"depth_{symbol}",
            "ch": f"depth:{symbol}:0"
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ AscendEX 已连接: {self.ws_url}")

    async def subscribe(self, symbol: str):
        msg = self.build_sub_msg(symbol)
        await self.ws.send(json.dumps(msg))
        print(f"📨 AscendEX 订阅: {symbol}")

    async def run(self):
        await self.connect()

        for symbol in self.symbols:
            await self.subscribe(symbol)
            await asyncio.sleep(0.2)

        while True:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)

                if data.get("m") == "depth" and "symbol" in data:
                    symbol = data["symbol"]
                    bids = data.get("data", {}).get("bids", [])
                    asks = data.get("data", {}).get("asks", [])

                    bid_price = float(bids[0][0]) if bids else 0.0
                    ask_price = float(asks[0][0]) if asks else 0.0

                    snapshot = MarketSnapshot(
                        exchange=self.exchange_name,
                        symbol=symbol,
                        best_bid=bid_price,
                        best_ask=ask_price,
                        timestamp=time.time()
                    )

                    if self.queue:
                        await self.queue.put(snapshot)

            except Exception as e:
                print(f"❌ AscendEX 错误: {e}")
                await asyncio.sleep(1)
