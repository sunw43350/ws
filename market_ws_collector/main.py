import asyncio
from dispatcher.manager import ExchangeManager

async def consume_snapshots(queue):
    while True:
        snapshot = await queue.get()
        print(f"📥 收到数据 → {snapshot.exchange} | {snapshot.symbol} | 买一: {snapshot.best_bid} | 卖一: {snapshot.best_ask}")
        queue.task_done()

async def main():
    snapshot_queue = asyncio.Queue()

    manager = ExchangeManager(queue=snapshot_queue)
    await asyncio.gather(
        manager.run_all(),               # 并发运行所有 Connector
        consume_snapshots(snapshot_queue)  # 消费数据
    )

if __name__ == "__main__":
    asyncio.run(main())
