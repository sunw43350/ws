import asyncio
import json
import time

import websockets


from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="okx", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression=None,       # OKX 不压缩
            ping_interval=None,     # OKX 自动心跳，客户端无需主动发 ping
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(s) for s in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="tickers")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(s): s
            for s in self.raw_symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.upper()

    def build_sub_msg(self) -> dict:
        return {
            "op": "subscribe",
            "args": [
                {"channel": "tickers", "instId": req.symbol}
                for req in self.subscriptions
            ]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ OKX WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        self.log(f"📨 已订阅: {[req.symbol for req in self.subscriptions]}")
        await asyncio.sleep(0.2)

    async def handle_message(self, data):
        if "arg" in data and "data" in data:
            arg = data["arg"]
            symbol = arg.get("instId")
            raw_symbol = self.symbol_map.get(symbol, symbol)

            tick = data["data"][0]
            bid1 = float(tick.get("bidPx", 0.0))
            ask1 = float(tick.get("askPx", 0.0))
            bid_vol1 = float(tick.get("bidSz", 0.0))
            ask_vol1 = float(tick.get("askSz", 0.0))
            total_volume = float(tick.get("vol24h", 0.0))
            timestamp = int(tick.get("ts", time.time() * 1000))

            snapshot = MarketSnapshot(
                exchange=self.exchange_name,
                symbol=symbol,
                raw_symbol=raw_symbol,
                bid1=bid1,
                ask1=ask1,
                bid_vol1=bid_vol1,
                ask_vol1=ask_vol1,
                total_volume=total_volume,
                timestamp=timestamp
            )

            if self.queue:
                await self.queue.put(snapshot)
        else:
            self.log(f"❗️ 未处理的消息: {data}", level="DEBUG")
