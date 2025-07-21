import asyncio
from connectors import binance  # 可扩展为动态导入

class ExchangeManager:
    def __init__(self):
        self.connectors = [
            binance.Connector()
            # 添加其他 Connector 实例
        ]

    async def run_all(self):
        tasks = [asyncio.create_task(conn.run()) for conn in self.connectors]
        await asyncio.gather(*tasks)
