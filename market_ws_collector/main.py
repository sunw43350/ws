import asyncio
from connectors import ascendex

async def consume(queue):
    while True:
        snapshot = await queue.get()
        print(
            f"📥 推送 → {snapshot.exchange} | {snapshot.symbol} | "
            f"买一价: {snapshot.bid1} ({snapshot.bid_vol1}) | "
            f"卖一价: {snapshot.ask1} ({snapshot.ask_vol1}) | "
            f"成交量: {snapshot.total_volume}"
        )

        queue.task_done()

async def main():
    snapshot_queue = asyncio.Queue()
    connector = ascendex.Connector(queue=snapshot_queue)
    
    await asyncio.gather(
        connector.run(),
        consume(snapshot_queue)
    )

if __name__ == "__main__":
    asyncio.run(main())
