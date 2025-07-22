import asyncio
# from dispatcher.manager_pro import ExchangeManager  # 调度器管理多个交易所连接器
from dispatcher.manager import ExchangeManager  # 调度器管理多个交易所连接器


async def consume_snapshots(queue):
    while True:
        snapshot = await queue.get()
        print(
            f"📥 [{snapshot.exchange}] {snapshot.timestamp_hms} | {snapshot.raw_symbol} | {snapshot.symbol} | "
            f"买一: {snapshot.bid1:.2f} ({snapshot.bid_vol1:.2f}) | "
            f"卖一: {snapshot.ask1:.2f} ({snapshot.ask_vol1:.2f})"
        )

        queue.task_done()

async def main():
    snapshot_queue = asyncio.Queue()
    manager = ExchangeManager(queue=snapshot_queue)

    await asyncio.gather(
        manager.run_all(),              # 同时运行多个交易所的 Connector
        consume_snapshots(snapshot_queue)  # 输出推送结果
    )

if __name__ == "__main__":
    asyncio.run(main())
