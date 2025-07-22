import asyncio
import datetime
import os
import shutil
from collections import defaultdict
import matplotlib.pyplot as plt

# from dispatcher.manager_pro import ExchangeManager
from dispatcher.manager import ExchangeManager

# Configuration
DATA_RETENTION_MINUTES = 10
PLOT_INTERVAL_SECONDS = 20

# Runtime containers
active_symbols = set()
symbol_exchange_data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'bid': [], 'ask': []}))

def prepare_image_folder():
    folder = 'imgs'
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

def prune_old_data():
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=DATA_RETENTION_MINUTES)
    for symbol, exchanges in symbol_exchange_data.items():
        for exchange, data in exchanges.items():
            times = data['times']
            idx = next((i for i, t in enumerate(times) if t >= cutoff), len(times))
            data['times'] = times[idx:]
            data['bid'] = data['bid'][idx:]
            data['ask'] = data['ask'][idx:]

def is_price_valid(prices):
    return all(p > 0 for p in prices)

def compute_arbitrage_spread(symbol):
    exchanges = symbol_exchange_data.get(symbol, {})
    timestamps = []
    spreads = []
    percents = []

    if not exchanges:
        return [], [], []

    sample_count = len(next(iter(exchanges.values()))['times'])

    for i in range(sample_count):
        best_bid = -float("inf")
        best_ask = float("inf")
        time_ref = None

        for data in exchanges.values():
            if i >= len(data['times']):
                continue
            bid = data['bid'][i]
            ask = data['ask'][i]
            time = data['times'][i]
            if bid > 0 and ask > 0:
                best_bid = max(best_bid, bid)
                best_ask = min(best_ask, ask)
                time_ref = time

        if best_bid > best_ask and time_ref:
            spread = best_bid - best_ask
            percent = (spread / best_ask) * 100
            timestamps.append(time_ref)
            spreads.append(spread)
            percents.append(percent)

    return timestamps, spreads, percents

def plot_symbol(symbol):
    exchanges = symbol_exchange_data.get(symbol, {})
    colors = plt.cm.get_cmap('tab10')
    fig, (ax_price, ax_arbitrage) = plt.subplots(
        2, 1, figsize=(16, 9), sharex=True,
        gridspec_kw={'height_ratios': [2, 1]}  # Price plot gets 2x vertical space
    )

    plotted = False

    # Plot bid/ask prices
    for idx, (exchange, data) in enumerate(exchanges.items()):
        times = data['times']
        bids = data['bid']
        asks = data['ask']
        if not times or not is_price_valid(bids) or not is_price_valid(asks):
            continue
        color = colors(idx % 10)
        axs[0].plot(times, asks, label=f"{exchange} Ask", color=color, linestyle='-')
        axs[0].plot(times, bids, label=f"{exchange} Bid", color=color, linestyle='--')
        plotted = True

    if not plotted:
        print(f"⏭️ Skipping {symbol}: No valid price data.")
        plt.close()
        return

    axs[0].set_title(f"{symbol} Price Comparison Across Exchanges ({DATA_RETENTION_MINUTES} min)")
    axs[0].set_ylabel("Price")
    axs[0].grid(True)
    axs[0].legend()

    # Plot arbitrage spread
    times, spreads, percents = compute_arbitrage_spread(symbol)
    axs[1].plot(times, spreads, label="Spread (USD)", color="purple")
    axs[1].plot(times, percents, label="Spread (%)", color="orange")
    axs[1].set_title(f"{symbol} Arbitrage Spread (Taker-Taker)")
    axs[1].set_ylabel("Spread / %")
    axs[1].set_xlabel("Time")
    axs[1].grid(True)
    axs[1].legend()

    plt.tight_layout()
    plt.gcf().autofmt_xdate()

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("imgs", f"{symbol}_arbitrage_{timestamp_str}.png")
    plt.savefig(filename)
    plt.close()
    print(f"🟢 Saved chart: {filename}")

async def periodic_plot_task():
    while True:
        await asyncio.sleep(PLOT_INTERVAL_SECONDS)
        prune_old_data()
        for symbol in active_symbols:
            plot_symbol(symbol)

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
