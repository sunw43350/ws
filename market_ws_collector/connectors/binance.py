import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="binance", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression=None,  # Binance 组合流默认不压缩
            ping_interval=None,  # Binance 组合流默认有协议层 ping，不需要应用层
            ping_payload=None,
            pong_keywords=["pong"],
        )
        self.queue = queue
        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])

        self.formatted_symbols = [self.format_symbol(s) for s in self.raw_symbols]
        self.symbol_map = {self.format_symbol(s): s for s in self.raw_symbols}

        streams = [f"{sym}@ticker" for sym in self.formatted_symbols]
        self.ws_url = ws_url or f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"

    def format_symbol(self, generic_symbol: str) -> str:
        return generic_symbol.lower().replace("-", "")

    async def connect(self):
        self.ws = await websockets.connect(
            self.ws_url,
            ping_interval=20  # Binance 支持协议层 ping，设为20秒即可
        )
        self.log(f"✅ Binance WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        # Binance 组合流已经在 URL 里订阅，不用发送订阅消息
        self.log("📡 Binance 使用组合流，不需要发送订阅消息。")

    async def handle_message(self, data):
        # 组合流数据格式:
        # {"stream": "btcusdt@ticker", "data": {...ticker_data...}}
        payload = data.get("data")
        if not payload:
            return

        symbol = payload.get("s")  # Binance 原始符号，如 BTCUSDT
        if not symbol:
            return

        raw_symbol = self.symbol_map.get(symbol.lower(), symbol)

        try:
            price = float(payload.get("c", 0.0))  # 最新成交价
            timestamp = int(payload.get("E", time.time() * 1000))
        except Exception as e:
            self.log(f"数据解析错误: {e}", level="WARNING")
            return

        snapshot = MarketSnapshot(
            exchange=self.exchange_name,
            symbol=symbol,
            raw_symbol=raw_symbol,
            bid1=price,
            ask1=price,
            bid_vol1=0.0,
            ask_vol1=0.0,
            timestamp=timestamp
        )

        if self.queue:
            await self.queue.put(snapshot)

    async def run(self):
        await self.run_forever()
