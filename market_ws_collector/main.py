import asyncio
import datetime
import os
from collections import defaultdict
from data_utils import prune_old_data
from plot_utils import plot_symbol

import shutil

# from dispatcher.manager_pro import ExchangeManager
from dispatcher.manager import ExchangeManager

# 配置项
DATA_RETENTION_MINUTES = 10
PLOT_INTERVAL_SECONDS = 60 * 1

# 运行时存储
active_symbols = set()
symbol_exchange_data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'bid': [], 'ask': []}))

def prepare_image_folder():
    folder = 'imgs'
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

async def periodic_plot_task():
    while True:
        await asyncio.sleep(PLOT_INTERVAL_SECONDS)
        prune_old_data(symbol_exchange_data, DATA_RETENTION_MINUTES)
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=PLOT_INTERVAL_SECONDS)
        for symbol in active_symbols:
            exchanges = symbol_exchange_data[symbol]
            plot_symbol(symbol, exchanges, cutoff)

async def consume_snapshots(queue: asyncio.Queue):
    while True:
        snapshot = await queue.get()
        symbol = snapshot.raw_symbol
        exchange = snapshot.exchange
        bid1 = snapshot.bid1
        ask1 = snapshot.ask1
        timestamp = datetime.datetime.now()

        active_symbols.add(symbol)

        data = symbol_exchange_data[symbol][exchange]
        if isinstance(data, dict):
            data['times'].append(timestamp)
            data['bid'].append(bid1)
            data['ask'].append(ask1)
        else:
            print(f"❌ 数据错误: 预期为字典(dict)，但实际类型为 {type(data)}")
            continue

        note = f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! {exchange}" if bid1 == 0 and ask1 == 0 else ""

        print(
            f"{snapshot.timestamp_hms} | [{exchange}] | {snapshot.raw_symbol} | {symbol} | "
            f"Bid: {bid1:.5f} ({snapshot.bid_vol1:.2f}) | Ask: {ask1:.5f} ({snapshot.ask_vol1:.2f}) | {note}"
        )

        queue.task_done()

async def main():
    snapshot_queue = asyncio.Queue()
    manager = ExchangeManager(queue=snapshot_queue)
    await asyncio.gather(
        manager.run_all(),
        consume_snapshots(snapshot_queue),
        periodic_plot_task()
    )

if __name__ == "__main__":
    prepare_image_folder()
    asyncio.run(main())
