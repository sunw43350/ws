import asyncio
import json
import re
import time
import websockets

from connectors.base import BaseAsyncConnector
from models.base import SubscriptionRequest, MarketSnapshot
from config import DEFAULT_SYMBOLS, WS_ENDPOINTS

class Connector(BaseAsyncConnector):
    def __init__(self, symbols=None, ws_url=None):
        super().__init__("ascendex")

        # 使用传入的 symbols 或默认配置
        generic_symbols = symbols if symbols is not None else DEFAULT_SYMBOLS.get("ascendex", [])
        self.symbols = [self.format_symbol(sym) for sym in generic_symbols]

        # 使用传入的 WebSocket 地址或默认配置
        self.ws_url = ws_url if ws_url is not None else WS_ENDPOINTS.get("ascendex")

        self.ws = None

    def format_symbol(self, generic):
        # BTC-USDT → BTC-PERP
        base = re.sub(r"-USDT$", "", generic.upper())
        return f"{base}-PERP"

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ AscendEX WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self, symbol):
        sub_msg = {
            "op": "sub",
            "id": f"depth_{symbol}",
            "ch": f"depth:{symbol}:0"
        }
        await self.ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 AscendEX 合约: {symbol}")

    async def run(self):
        await self.connect()

        # 批量订阅所有 symbol
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
