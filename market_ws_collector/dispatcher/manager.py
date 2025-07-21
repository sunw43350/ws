from connectors import ascendex, kraken  # ✅ 添加 Kraken
from config import DEFAULT_SYMBOLS
import asyncio

class ExchangeManager:
    def __init__(self, queue):
        self.queue = queue
        self.connectors = [
            ascendex.Connector(symbols=DEFAULT_SYMBOLS["ascendex"], queue=queue),
            kraken.Connector(symbols=DEFAULT_SYMBOLS["kraken"], queue=queue),
            # 你可以继续添加 binance、bybit 等其他交易所
        ]

    async def run_all(self):
        tasks = [asyncio.create_task(conn.run()) for conn in self.connectors]
        await asyncio.gather(*tasks)
