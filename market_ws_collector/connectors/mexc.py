        
import json
import time
import asyncio
import websockets

from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector
from config import DEFAULT_SYMBOLS, WS_ENDPOINTS


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="mexc", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression=None,                 # MEXC数据不压缩
            ping_interval=20,
            ping_payload={"method": "ping"},
            pong_keywords=["pong"],
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)
        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.formatted_symbols = [self.format_symbol(sym) for sym in self.raw_symbols]
        self.subscriptions = [
            SubscriptionRequest(symbol=sym, channel="sub.ticker")
            for sym in self.formatted_symbols
        ]
        self.symbol_map = {self.format_symbol(s): s for s in self.raw_symbols}

    async def connect(self):
        self.ws = await websockets.connect(
            self.ws_url,
            ping_interval=None  # 禁用websocket协议层ping，使用应用层ping
        )
        self.log(f"✅ MEXC WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = {
                "method": req.channel,
                "param": {
                    "symbol": req.symbol
                }
            }
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: {req.channel} → {req.symbol}")
            await asyncio.sleep(0.05)

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.replace("-", "_").upper()

    async def handle_message(self, data):
        # 处理行情数据
        if data.get("channel") == "push.ticker" and "data" in data:
            tick = data["data"]
            symbol = tick.get("symbol")
            raw_symbol = self.symbol_map.get(symbol, symbol)
            try:
                bid1 = float(tick.get("bid1", 0.0))
                ask1 = float(tick.get("ask1", 0.0))
                bid_vol1 = float(tick.get("holdVol", 0.0))
                ask_vol1 = bid_vol1
                total_volume = float(tick.get("volume24", 0.0))
                timestamp = int(tick.get("timestamp", time.time() * 1000))
            except Exception as e:
                self.log(f"数据解析错误: {e}", level="WARNING")
                return

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
            self.log(f"未知消息格式: {data}", level="WARNING")
