import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitmart", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression=None,  # 明确无压缩
            ping_interval=8,  # BitMart 使用 ping/pong 机制
            ping_payload="ping",  # 发送的 ping 消息内容
            pong_keywords=["pong"]  # 检测到 pong 日志打印即可
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)
        self.symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])

        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="futures/ticker")
            for sym in self.symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in self.symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.replace("-", "").upper()

    def build_sub_msg(self) -> dict:
        return {
            "action": "subscribe",
            "args": [f"futures/ticker:{req.symbol}" for req in self.subscriptions]
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ BitMart WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = self.build_sub_msg()
        await self.ws.send(json.dumps(msg))
        self.log(f"📨 已发送订阅请求: {msg}")

    async def handle_message(self, data):
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
            item = data["data"]
            symbol = item.get("symbol")
            raw_symbol = self.symbol_map.get(symbol, symbol)

            try:
                bid1 = float(item.get("bid_price", 0.0))
                bid_vol1 = float(item.get("bid_vol", 0.0))
                ask1 = float(item.get("ask_price", 0.0))
                ask_vol1 = float(item.get("ask_vol", 0.0))
                total_volume = float(item.get("volume_24", 0.0))
            except Exception as e:
                self.log(f"⚠️ 数据解析失败: {e}", level="WARNING")
                return

            timestamp = int(time.time() * 1000)

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
            self.log(f"⚠️ 无效数据格式: {data}", level="WARNING")

    async def run(self):
        await self.run_forever()
