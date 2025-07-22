import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="binance", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.raw_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])

        # 构造 symbol 映射和订阅结构（标准 → 实际订阅字段）
        self.formatted_symbols = [self.format_symbol(s) for s in self.raw_symbols]
        self.symbol_map = {
            self.format_symbol(s): s
            for s in self.raw_symbols
        }

        self.streams = [f"{sym}@ticker" for sym in self.formatted_symbols]
        self.ws_url = ws_url or f"wss://stream.binance.com:9443/stream?streams={'/'.join(self.streams)}"
        self.ws = None

    def format_symbol(self, generic_symbol: str) -> str:
        # BTC-USDT → btcusdt
        return generic_symbol.lower().replace("-", "")

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Binance WebSocket 已连接 → {self.ws_url}")

    async def run(self):
        while True:
            try:
                await self.connect()
                print("📨 已订阅 Binance ticker 合约:")
                for sym in self.formatted_symbols:
                    print(f"🔔 {sym} @ticker")

                while True:
                    raw = await self.ws.recv()
                    try:
                        data = json.loads(raw)
                    except:
                        continue

                    payload = data.get("data")
                    symbol = payload.get("s") if payload else None
                    raw_symbol = self.symbol_map.get(symbol.lower(), symbol)

                    if payload and symbol and "c" in payload:
                        price = float(payload["c"])
                        timestamp = int(payload.get("E", time.time() * 1000))

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
                            print(f"📥 {self.format_snapshot(snapshot)}")

            except websockets.exceptions.ConnectionClosedOK as e:
                print(f"🔁 Binance 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ Binance 异常: {e}")
                await asyncio.sleep(0.1)
