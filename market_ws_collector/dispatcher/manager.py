from connectors import ascendex, binance  # 添加你已实现的 Connector
from config import DEFAULT_SYMBOLS
import asyncio

class ExchangeManager:
    def __init__(self, queue):
        self.queue = queue
        self.connectors = [
            ascendex.Connector(symbols=DEFAULT_SYMBOLS["ascendex"], queue=queue),
            # 后续添加更多交易所
        ]

    async def run_all(self):
        tasks = [asyncio.create_task(conn.run()) for conn in self.connectors]
        await asyncio.gather(*tasks)
