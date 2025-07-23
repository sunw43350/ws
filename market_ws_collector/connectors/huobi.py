import json
import time
from connectors.base import BaseAsyncConnector
from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
import websockets
import asyncio


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="huobi", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange, compression="gzip")
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(s) for s in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="ticker")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(raw): raw
            for raw in self.raw_symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.lower().replace("-", "")

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "sub": f"market.{symbol}.ticker",
            "id": symbol
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Huobi WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: market.{req.symbol}.ticker")
            await asyncio.sleep(0.05)

    async def handle_message(self, data):
        # ping 处理
        if "ping" in data:
            self.log(data, level="DEBUG")
            pong_msg = {"pong": data["ping"]}
            await self.ws.send(json.dumps(pong_msg))
            
            self.log(f"🔁 收到 ping → 已发送 pong: {pong_msg}")
            return

        # ticker 数据处理
        if "tick" in data and "ch" in data:
            tick = data["tick"]
            channel = data["ch"]
            symbol = channel.split(".")[1]
            raw_symbol = self.symbol_map.get(symbol, symbol.upper())

            bid1 = float(tick.get("bid", 0.0))
            bid_vol1 = float(tick.get("bidSize", 0.0))
            ask1 = float(tick.get("ask", 0.0))
            ask_vol1 = float(tick.get("askSize", 0.0))
            timestamp = int(tick.get("ts", time.time() * 1000))

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
            return
        else:
            self.log(f"❗️ 未处理的消息: {data}", level="DEBUG")
