import asyncio
import json
import time
import websockets

from config import DEFAULT_SYMBOLS, WS_ENDPOINTS
from models.base import MarketSnapshot

class Connector(BaseAsyncConnector):
# class KrakenFuturesConnector:
    def __init__(self, exchange="krakenfutures", symbols=None, ws_url=None, queue=None):
        self.exchange = exchange
        self.ws_url = ws_url or WS_ENDPOINTS.get(exchange)
        self.queue = queue

        # BTC-USDT → PI_XBTUSD（Kraken Futures 格式）
        self.product_ids = [
            self.format_symbol(symbol)
            for symbol in symbols or DEFAULT_SYMBOLS.get(exchange, [])
        ]

    def format_symbol(self, generic_symbol: str) -> str:
        symbol = generic_symbol.upper().replace("-", "")
        symbol = symbol.replace("BTC", "XBT")
        symbol = symbol.replace("USDT", "USD")
        return f"PI_{symbol}"

    def build_sub_msg(self):
        return {
            "event": "subscribe",
            "feed": "ticker",
            "product_ids": self.product_ids
        }

    async def heartbeat(self, ws):
        while True:
            await ws.send(json.dumps({"event": "ping"}))
            await asyncio.sleep(30)

    async def run(self):
        try:
            async with websockets.connect(self.ws_url, ping_interval=None) as ws:
                print(f"✅ Kraken Futures WebSocket 已连接 → {self.ws_url}")
                await ws.send(json.dumps(self.build_sub_msg()))
                print(f"📨 Kraken Futures 已订阅: {self.product_ids}")

                asyncio.create_task(self.heartbeat(ws))

                async for raw in ws:
                    try:
                        data = json.loads(raw)
                        if data.get("feed") == "ticker" and "product_id" in data:
                            snapshot = MarketSnapshot(
                                exchange=self.exchange,
                                symbol=data["product_id"],
                                bid1=float(data.get("bid", 0.0)),
                                ask1=float(data.get("ask", 0.0)),
                                bid_vol1=float(data.get("bid_size", 0.0)),
                                ask_vol1=float(data.get("ask_size", 0.0)),
                                total_volume=float(data.get("volume", 0.0)),
                                timestamp=time.time()
                            )
                            if self.queue:
                                await self.queue.put(snapshot)
                            else:
                                print(
                                    f"[{snapshot.symbol}] 🟢 bid: {snapshot.bid1:.2f} | ask: {snapshot.ask1:.2f} | vol: {snapshot.total_volume:.2f}"
                                )
                    except Exception as e:
                        print(f"❌ 数据解析异常: {e}")
        except Exception as e:
            print(f"❌ Kraken Futures 连接异常: {e}")
