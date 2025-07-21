import asyncio
from connectors import ascendex

async def consume(queue):
    while True:
        snapshot = await queue.get()
        print(f"📥 推送 → {snapshot.exchange} | {snapshot.symbol} | 买一: {snapshot.best_bid} | 卖一: {snapshot.best_ask}")
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
