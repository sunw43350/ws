import asyncio
import json
import re
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="krakenfutures", symbols=None, ws_url=None, queue=None):
        # 传入心跳参数，ping_payload 为 {"event": "ping"}, 每30秒发一次
        # super().__init__(exchange, ping_interval=30, ping_payload=None)
        super().__init__(
            exchange=exchange,
            compression=None,  # 明确无压缩
            ping_interval=10,  # Kraken Futures 使用 ping/pong 机制
            ping_payload={
            "event": "subscribe",
            "feed": "heartbeat"
            },  # 发送的 ping 消息内容
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        generic_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="ticker")
            for sym in generic_symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in generic_symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        symbol = generic_symbol.upper().replace("-", "")
        symbol = re.sub(r"USDT$", "USD", symbol)
        symbol = re.sub(r"^BTC", "XBT", symbol)
        return f"PI_{symbol}"

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ {self.exchange_name} WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        msg = {
            "event": "subscribe",
            "feed": "ticker",
            "product_ids": [req.symbol for req in self.subscriptions]
        }
        await self.ws.send(json.dumps(msg))
        self.log(f"📨 Kraken Futures 已订阅: {[req.symbol for req in self.subscriptions]}")

    async def handle_message(self, data):
        if data.get("feed") == "ticker" and "product_id" in data:
            # self.log(data, level="DEBUG")
            symbol = data["product_id"]
            raw_symbol = self.symbol_map.get(symbol, symbol)
            

            bid1 = float(data.get("bid", 0.0))
            ask1 = float(data.get("ask", 0.0))
            bid_vol1 = float(data.get("bid_size", 0.0))
            ask_vol1 = float(data.get("ask_size", 0.0))
            total_volume = float(data.get("volume", 0.0))
            timestamp = int(data.get("timestamp", time.time() * 1000))


            # if bid1 == 0.0 and ask1 == 0.0:
            #     self.log(f"❗️ {self.exchange_name} {raw_symbol} 异常价格为零数据: {data}", level="WARNING")
            #     return

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
