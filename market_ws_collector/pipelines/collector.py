import asyncio

class CollectorPipeline:
    @staticmethod
    async def run():
        while True:
            await asyncio.sleep(5)
            # 可连接到 DB、消息队列、策略等
