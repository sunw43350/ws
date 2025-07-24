import asyncio
import datetime
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import MarketSnapshot, SubscriptionRequest
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="lbank", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange,
            ping_interval=20,
            ping_payload=None,     # 每 20 秒发一次 "ping"
        )

        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]

        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="depth")
            for sym in self.formatted_symbols
        ]

        self.symbol_map = {
            self.format_symbol(raw): raw
            for raw in self.raw_symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.lower().replace("-", "_")

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "action": "subscribe",
            "subscribe": "depth",
            "depth": "1",
            "pair": symbol
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ LBank WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅 depth:{req.symbol}")
            await asyncio.sleep(0.1)

    async def handle_message(self, data):
        # ping { "action":"ping", "ping":"0ca8f854-7ba7-4341-9d86-d3327e52804e" }
        if "ping" in data:  #  {'ping': '1753282382760', 'action': 'ping'}
            pong_msg = {
                "pong": data["ping"],
                "action": "pong"
            }
            await self.ws.send(json.dumps(pong_msg))
            self.log(f"🔁 收到 ping: {data}，回复 pong: {pong_msg}")

            ping_msg = {
                "ping": f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "action": "ping"
            }
            await self.ws.send(json.dumps(ping_msg))
            self.log(f"🔁 主动发送心跳: {ping_msg}")
            return
    
        if "depth" in data and "pair" in data:
            tick = data["depth"]
            symbol = data["pair"]
            raw_symbol = self.symbol_map.get(symbol, symbol.upper())

            bids = tick.get("bids", [])
            asks = tick.get("asks", [])

            bid1, bid_vol1 = map(float, bids[0][:2]) if bids else (0.0, 0.0)
            ask1, ask_vol1 = map(float, asks[0][:2]) if asks else (0.0, 0.0)
            timestamp = int(time.time() * 1000)

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
