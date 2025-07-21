import asyncio
import json
import re
import time
import websockets

from connectors.base import BaseAsyncConnector
from models.base import SubscriptionRequest, MarketSnapshot
from config import DEFAULT_SYMBOLS

class Connector(BaseAsyncConnector):
    def __init__(self, symbols=None):
        super().__init__("ascendex")

        # ✅ 使用注入的 symbol 或默认配置中的标准格式符号列表
        generic_symbols = symbols if symbols is not None else DEFAULT_SYMBOLS.get("ascendex", [])

        # ✅ 转换为 AscendEX 实际订阅符号
        self.symbols = [self.format_symbol(sym) for sym in generic_symbols]
        self.ws = None

    def format_symbol(self, generic):
        """
        将标准格式 'BTC-USDT' 转换为 AscendEX 格式 'BTC-PERP'
        """
        # 提取币种，替换 USDT 为 PERP 合约格式
        base = re.sub(r"-USDT$", "", generic.upper())
        return f"{base}-PERP"

    async def connect(self):
        url = "wss://ascendex.com/1/api/pro/v2/stream"
        self.ws = await websockets.connect(url)
        print(f"✅ AscendEX WebSocket 已连接 → {url}")

    async def subscribe(self, symbol):
        """
        使用 depth:{symbol}:0 频道订阅买一卖一行情
        """
        sub_msg = {
            "op": "sub",
            "id": f"depth_{symbol}",
            "ch": f"depth:{symbol}:0"
        }
        await self.ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 AscendEX 合约: {symbol}")

    async def run(self):
        await self.connect()

        for symbol in self.symbols:
            await self.subscribe(symbol)
            await asyncio.sleep(0.3)  # 控制订阅速率，防止限速

        while True:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)

                if data.get("m") == "depth" and "symbol" in data:
                    symbol = data["symbol"]
                    bids = data.get("data", {}).get("bids", [])
                    asks = data.get("data", {}).get("asks", [])

                    bid_price, bid_qty = bids[0] if bids else ("-", "-")
                    ask_price, ask_qty = asks[0] if asks else ("-", "-")

                    snapshot = MarketSnapshot(
                        exchange=self.exchange_name,
                        symbol=symbol,
                        best_bid=float(bid_price),
                        best_ask=float(ask_price),
                        timestamp=time.time()
                    )

                    print(f"📊 {snapshot.symbol} | 买一: {snapshot.best_bid} | 卖一: {snapshot.best_ask}")

            except Exception as e:
                print(f"❌ AscendEX 解码或连接错误: {e}")
                await asyncio.sleep(1)
