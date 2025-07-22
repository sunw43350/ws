import asyncio
import datetime
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# from dispatcher.manager_pro import ExchangeManager
from dispatcher.manager import ExchangeManager

# 🔧 Parameters
DATA_RETENTION_MINUTES = 3
PLOT_INTERVAL_SECONDS = 60

# ⏳ Runtime collections
active_symbols = set()
symbol_exchange_data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'bid': [], 'ask': []}))

import shutil

def prepare_image_folder():
    img_folder = 'imgs'
    if os.path.exists(img_folder):
        shutil.rmtree(img_folder)  # 🧹 删除整个文件夹及其内容
    os.makedirs(img_folder)        # 🆕 重新创建空文件夹


def prune_old_data():
    """Remove data older than retention threshold"""
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=DATA_RETENTION_MINUTES)
    for symbol, exchanges in symbol_exchange_data.items():
        for exchange, data in exchanges.items():
            times = data['times']
            idx = next((i for i, t in enumerate(times) if t >= cutoff), len(times))
            data['times'] = times[idx:]
            data['bid'] = data['bid'][idx:]
            data['ask'] = data['ask'][idx:]

def is_price_valid(prices):
    """Check if price series contains non-zero values"""
    return all(p > 0 for p in prices)

def plot_symbol(symbol):
    """Generate and save price plot for a symbol"""
    plt.figure(figsize=(12, 6))
    exchanges = symbol_exchange_data.get(symbol, {})
    colors = plt.cm.get_cmap('tab10')
    plotted = False

    for idx, (exchange, data) in enumerate(exchanges.items()):
        times = data['times']
        bids = data['bid']
        asks = data['ask']

        if not times or not is_price_valid(bids) or not is_price_valid(asks):
            continue

        color = colors(idx % 10)
        plt.plot(times, asks, label=f"{exchange} Ask", color=color, linestyle='-')
        plt.plot(times, bids, label=f"{exchange} Bid", color=color, linestyle='--')
        plotted = True

    if not plotted:
        print(f"⏭️ Skipping {symbol}: No valid data")
        plt.close()
        return

    plt.title(f"{symbol} Price Comparison Across Exchanges ({DATA_RETENTION_MINUTES} min)")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("imgs", f"{symbol}_prices_{timestamp_str}.png")
    plt.savefig(filename)
    plt.close()
    print(f"✅ Saved plot: {filename}")

async def periodic_plot_task():
    """Plot prices every PLOT_INTERVAL_SECONDS"""
    while True:
        await asyncio.sleep(PLOT_INTERVAL_SECONDS)
        prune_old_data()
        for symbol in active_symbols:
            plot_symbol(symbol)

async def consume_snapshots(queue: asyncio.Queue):
    """Process incoming market snapshots"""
    while True:
        snapshot = await queue.get()
        symbol = snapshot.symbol
        exchange = snapshot.exchange
        bid1 = snapshot.bid1
        ask1 = snapshot.ask1
        timestamp = datetime.datetime.now()

        # 👁️ Track active symbols
        active_symbols.add(symbol)

        data = symbol_exchange_data[symbol][exchange]
        data['times'].append(timestamp)
        data['bid'].append(bid1)
        data['ask'].append(ask1)

        print(
            f"{snapshot.timestamp_hms} | [{exchange}] | {snapshot.raw_symbol} | {symbol} | "
            f"Bid: {bid1:.2f} ({snapshot.bid_vol1:.2f}) | Ask: {ask1:.2f} ({snapshot.ask_vol1:.2f})"
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
