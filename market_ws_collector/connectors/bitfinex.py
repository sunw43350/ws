import asyncio
import json
import time
import aiohttp
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector

class Connector(BaseAsyncConnector):
    def __init__(self, exchange="bitfinex", symbols=None, ws_url=None, queue=None):
        super().__init__(exchange)
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)
        self.symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])

        self.subscriptions = []             # SubscriptionRequest 列表
        self.symbol_map = {}                # 合约代码 → 原始币种
        self.chan_map = {}                  # chanId → 合约代码
        self.valid_contracts = set()        # 官方支持合约列表
        self.ws = None

    async def fetch_supported_contracts(self):
        url = "https://api-pub.bitfinex.com/v2/conf/pub:list:pair:futures"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                self.valid_contracts = set(data[0]) if isinstance(data, list) else set()
                self.log(f"✅ 拉取 Bitfinex 支持合约成功: {len(self.valid_contracts)} 条")

    def format_symbol(self, generic_symbol: str) -> str:
        base = generic_symbol.upper().split("-")[0]
        return f"t{base}F0:USTF0"

    async def prepare_subscriptions(self):
        await self.fetch_supported_contracts()
        for sym in self.symbols:
            formatted = self.format_symbol(sym)
            if formatted in self.valid_contracts:
                self.subscriptions.append(SubscriptionRequest(symbol=formatted, channel="ticker"))
                self.symbol_map[formatted] = sym
                self.log(f"✅ 合约有效: {formatted}")
            else:
                self.log(f"⚠️ 跳过无效合约: {formatted}")

    def build_sub_msg(self, request: SubscriptionRequest) -> dict:
        return {
            "event": "subscribe",
            "channel": "ticker",
            "symbol": request.symbol
        }

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        self.log(f"✅ Bitfinex WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: {req.symbol}")
            await asyncio.sleep(0.3)

    async def run(self):
        while True:
            try:
                await self.connect()
                # await self.prepare_subscriptions()
                await self.subscribe()

                while True:
                    raw = await self.ws.recv()
                    data = json.loads(raw)

                    # 📘 注册 chanId → symbol 映射
                    if isinstance(data, dict) and data.get("event") == "subscribed":
                        self.chan_map[data["chanId"]] = data["symbol"]
                        continue

                    # 🧊 忽略心跳包
                    if isinstance(data, list) and len(data) == 2 and data[1] == "hb":
                        continue

                    # 📈 处理 ticker 数据
                    if isinstance(data, list) and len(data) == 2:
                        chan_id, tick = data
                        symbol = self.chan_map.get(chan_id)
                        if not symbol or not isinstance(tick, list) or len(tick) < 10:
                            continue

                        raw_symbol = self.symbol_map.get(symbol, symbol)
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
                self.log(f"🔁 Bitfinex 正常断开: {e}，尝试重连...")
                await asyncio.sleep(0.5)
            except Exception as e:
                self.log(f"❌ Bitfinex 异常: {e}")
                await asyncio.sleep(0.5)
