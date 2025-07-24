import asyncio
import json
import time
import gzip
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitrue", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression="gzip",
            ping_payload=None,
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        self.symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="depth_step0")
            for sym in self.symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in self.symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.lower().replace("-", "")

    def build_sub_msg(self, symbol: str) -> dict:
        return {
            "event": "sub",
            "params": {
                "channel": f"market_{symbol}_depth_step0",
                "cb_id": symbol
            }
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Bitrue WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            sub_msg = self.build_sub_msg(req.symbol)
            await self.ws.send(json.dumps(sub_msg))
            self.log(f"📨 已订阅: market_{req.symbol}_depth_step0")
            await asyncio.sleep(0.1)

    async def handle_message(self, data):
        if "ping" in data:
            self.log(data, level="DEBUG")
            pong_msg = {"pong": data["ping"]}
            await self.ws.send(json.dumps(pong_msg))
            
            self.log(f"🔁 收到 ping → 已发送 pong: {pong_msg}")
            return
        
        if "channel" in data and "tick" in data:
            channel = data["channel"]
            symbol = channel.replace("market_", "").replace("_depth_step0", "")
            raw_symbol = self.symbol_map.get(symbol, symbol)

            bids = data["tick"].get("buys", [])
            asks = data["tick"].get("asks", [])

            bid1, bid_vol1 = map(float, bids[0][:2]) if bids else (0.0, 0.0)
            ask1, ask_vol1 = map(float, asks[0][:2]) if asks else (0.0, 0.0)
            timestamp = int(data.get("ts", time.time() * 1000))

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
            self.log(f"未知消息格式: {data}", level="DEBUG")

    # run由基类统一管理，不再重写
