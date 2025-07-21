from connectors import ascendex, krakenfutures, bingx, bitfinex, bitget, bitmart
from config import DEFAULT_SYMBOLS
import asyncio

class ExchangeManager:
    def __init__(self, queue):
        self.queue = queue
        self.connectors = [
            # ascendex.Connector(exchange="ascendex", queue=queue),
            # krakenfutures.Connector(exchange="krakenfutures", queue=queue),
            # bingx.Connector(exchange="bingx", queue=queue),  # ✅ 添加 BingX
            # bitfinex.Connector(exchange="bitfinex", queue=queue),  #  添加 Bitfinex  fail
            # bitget.Connector(exchange="bitget", queue=queue),  # ✅ 添加 Bitget
            bitmart.Connector(exchange="bitmart", queue=queue)  # ✅ 添加 BitMart

            # 你可以继续添加 binance、bybit 等其他交易所
        ]

    async def run_all(self):
        tasks = [asyncio.create_task(conn.run()) for conn in self.connectors]
        await asyncio.gather(*tasks)
