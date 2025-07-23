import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import MarketSnapshot, SubscriptionRequest
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="oxfun", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.exchange_name = exchange
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        # 输入 symbol 示例: BTC-USDT，格式化为 BTC-USD-SWAP-LIN
        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(s) for s in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="depth")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(s): s
            for s in self.raw_symbols
        }

        self.ws = None

    def format_symbol(self, symbol: str) -> str:
        # BTC-USDT → BTC-USD-SWAP-LIN
        base, _ = symbol.upper().split("-")
        return f"{base}-USD-SWAP-LIN"

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "op": "subscribe",
            "args": [f"depth:{symbol}"]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, ping_interval=None)
        self.log(f"✅ OX.FUN WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: depth → {req.symbol}")
            await asyncio.sleep(0.2)

    async def handle_message(self, data):
        if data.get("table") == "depth" and "data" in data:
            tick = data["data"]
            symbol = tick.get("marketCode")
            raw_symbol = self.symbol_map.get(symbol, symbol)

            bids = tick.get("bids", [])
            asks = tick.get("asks", [])

            bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
            ask1, ask_vol1 = map(float, asks[0]) if asks else (0.0, 0.0)
            timestamp = int(tick.get("timestamp", time.time() * 1000))

            snapshot = MarketSnapshot(
                exchange=self.exchange_name,
                symbol=symbol,
                raw_symbol=raw_symbol,
                bid1=bid1,
                ask1=ask1,
                bid_vol1=bid_vol1,
                ask_vol1=ask_vol1,
                timestamp=timestamp
            )

            if self.queue:
                await self.queue.put(snapshot)
        else:
            self.log(f"❗️ 未处理的消息: {data}", level="DEBUG")
