import asyncio
import json
import re
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import SubscriptionRequest, MarketSnapshot
from connectors.base import BaseAsyncConnector


class Connector(BaseAsyncConnector):
    def __init__(self, exchange="ascendex", symbols=None, ws_url=None, queue=None):
        super().__init__(
            exchange=exchange,
            compression=None,  # AscendEX 数据不压缩
            ping_interval=20,  # 该交易所没官方说明ping频率，20秒心跳一般安全
            ping_payload={"op": "ping"},  # AscendEX 心跳包格式
            pong_keywords=["pong", "ping"],  # 简单判断pong消息
        )
        self.queue = queue
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)

        generic_symbols = symbols or DEFAULT_SYMBOLS.get(exchange, [])
        self.subscriptions = [
            SubscriptionRequest(symbol=self.format_symbol(sym), channel="depth", depth_level=0)
            for sym in generic_symbols
        ]

        self.symbol_map = {
            self.format_symbol(sym): sym
            for sym in generic_symbols
        }

    def format_symbol(self, generic_symbol: str) -> str:
        # 将 BTC-USDT 之类格式转换成 BTC-PERP
        return re.sub(r"-USDT$", "", generic_symbol.upper()) + "-PERP"

    def build_sub_msg(self, request: SubscriptionRequest) -> dict:
        return {
            "op": "sub",
            "id": f"{request.channel}_{request.symbol}",
            "ch": f"{request.channel}:{request.symbol}:{request.depth_level}"
        }

    async def connect(self):
        self.ws = await websockets.connect(
            self.ws_url,
            ping_interval=None  # 禁用协议层心跳，用应用层
        )
        self.log(f"✅ AscendEX WebSocket 已连接 → {self.ws_url}")

    async def subscribe(self):
        for req in self.subscriptions:
            msg = self.build_sub_msg(req)
            await self.ws.send(json.dumps(msg))
            self.log(f"📨 已订阅: {req.symbol}")
            await asyncio.sleep(0.1)

    async def handle_message(self, data):
        # 只处理 depth 消息
        if data.get("m") == "depth" and "symbol" in data:
            symbol = data["symbol"]
            raw_symbol = self.symbol_map.get(symbol, symbol)

            bids = data["data"].get("bids", [])
            asks = data["data"].get("asks", [])

            bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
            ask1, ask_vol1 = map(float, asks[0]) if asks else (0.0, 0.0)

            # depth 数据无时间戳，使用本地时间
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

        elif any(k in str(data).lower() for k in self.pong_keywords):
            self.log("🔁 收到 pong 心跳回复")

        else:
            # 其他消息忽略或可打印调试
            pass

    async def run(self):
        await self.run_forever()
