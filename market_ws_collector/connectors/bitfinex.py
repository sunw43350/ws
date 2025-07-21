import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitfinex", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
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

        self.ws = None
        self.chan_map = {}  # chanId → symbol 映射

    def format_symbol(self, generic_symbol: str) -> str:
        # BTC-USDT → tBTCF0:USTF0（Bitfinex 永续合约）
        base, quote = generic_symbol.upper().split("-")
        return f"t{base}F0:{quote}F0"

    def build_sub_msg(self, request: SubscriptionRequest) -> dict:
        return {
            "event": "subscribe",
            "channel": "ticker",
            "symbol": request.symbol
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✅ Bitfinex WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            await self.ws.send(json.dumps(self.build_sub_msg(req)))
            print(f"📨 已订阅: {req.symbol}")
            await asyncio.sleep(0.3)

    async def run(self):
        while True:
            try:
                await self.connect()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    print(f"📥 接收到数据: {data}")

                    # 🎯 维护 chanId → symbol 映射
                    if isinstance(data, dict) and data.get("event") == "subscribed":
                        chan_id = data["chanId"]
                        symbol = data["symbol"]
                        self.chan_map[chan_id] = symbol
                        continue

                    # 📦 处理 ticker 推送数据
                    if isinstance(data, list) and len(data) == 2:
                        chan_id, tick = data

                        # 心跳包
                        if tick == "hb":
                            continue

                        symbol = self.chan_map.get(chan_id, "unknown")
                        raw_symbol = self.symbol_map.get(symbol, symbol)

                        # Bitfinex ticker 数组结构参考：
                        # [ BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE, ..., VOLUME ]
                        if isinstance(tick, list) and len(tick) >= 10:
                            bid1 = float(tick[0])
                            bid_vol1 = float(tick[1])
                            ask1 = float(tick[2])
                            ask_vol1 = float(tick[3])
                            total_volume = float(tick[7])
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

            except websockets.exceptions.ConnectionClosedOK as e:
                print(f"🔁 Bitfinex 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ Bitfinex 异常: {e}")
                await asyncio.sleep(0.1)
