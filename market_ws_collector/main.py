import asyncio
import datetime
import os
import shutil
from collections import defaultdict
from dispatcher.manager import ExchangeManager
from utils.csv_utils import CSVManager, WriteTask, writer_worker
from utils.plot_arbitrage import plot_arbitrage_snapshot

# 🧹 启动前清空输出目录
output_dir = "snapshots"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

# 全局缓存
active_symbols = set()
symbol_exchange_data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'bid': [], 'ask': []}))

async def consume_snapshots(snapshot_queue: asyncio.Queue, write_queue: asyncio.Queue):
    while True:
        snapshot = await snapshot_queue.get()
        symbol = snapshot.raw_symbol
        exchange = snapshot.exchange
        bid1 = snapshot.bid1
        ask1 = snapshot.ask1
        timestamp = datetime.datetime.now()

        # ✅ 跟踪活跃 symbol
        active_symbols.add(symbol)

        # ✅ 更新数据缓存
        data = symbol_exchange_data[symbol][exchange]
        if isinstance(data, dict):
            data['times'].append(timestamp)
            data['bid'].append(bid1)
            data['ask'].append(ask1)
        else:
            print(f"❌ 数据错误: {type(data)}")
            snapshot_queue.task_done()
            continue

        # ⬇️ 写入 CSV 队列
        await write_queue.put(WriteTask("exchange", exchange, [
            timestamp.isoformat(), symbol, bid1, ask1, snapshot.bid_vol1, snapshot.ask_vol1
        ]))
        await write_queue.put(WriteTask("symbol", symbol, [
            timestamp.isoformat(), exchange, bid1, ask1, snapshot.bid_vol1, snapshot.ask_vol1
        ]))

        snapshot_queue.task_done()

async def periodic_plot_task(interval_sec: int):
    while True:
        await asyncio.sleep(interval_sec)
        current_symbols = list(active_symbols)
        for symbol in current_symbols:
            symbol_data = symbol_exchange_data.get(symbol)
            if symbol_data:
                plot_arbitrage_snapshot(symbol, symbol_data, f'{output_dir}/image')

async def main():
    snapshot_queue = asyncio.Queue()
    write_queue = asyncio.Queue()
    csv_manager = CSVManager(output_dir)
    manager = ExchangeManager(queue=snapshot_queue)

    try:
        await asyncio.gather(
            manager.run_all(),
            consume_snapshots(snapshot_queue, write_queue),
            writer_worker(write_queue, csv_manager, flush_interval=5),
            periodic_plot_task(60),  # ⏱ 自动获取 symbol，每 60 秒绘图
        )
    finally:
        csv_manager.close_all()

if __name__ == "__main__":
    asyncio.run(main())
