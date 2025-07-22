import asyncio
import datetime
import os
import shutil
from collections import defaultdict
import matplotlib.pyplot as plt

# from dispatcher.manager_pro import ExchangeManager
from dispatcher.manager import ExchangeManager

# Configurations
DATA_RETENTION_MINUTES = 10
PLOT_INTERVAL_SECONDS = 60 * 1

# Runtime storage
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

def compute_best_percent_spread_sequence(symbol, cutoff):
    exchanges = symbol_exchange_data.get(symbol, {})
    sequence = []

    if not exchanges:
        return []

    sample_count = len(next(iter(exchanges.values()))['times'])

    for i in range(sample_count):
        best_bid = -float("inf")
        best_ask = float("inf")
        time_ref, buy_ex, sell_ex = None, "", ""

        for ex_name, data in exchanges.items():
            if i >= len(data['times']) or data['times'][i] < cutoff:
                continue
            bid = data['bid'][i]
            ask = data['ask'][i]
            time = data['times'][i]
            if bid > 0 and ask > 0:
                if bid > best_bid:
                    best_bid = bid
                    sell_ex = ex_name
                if ask < best_ask:
                    best_ask = ask
                    buy_ex = ex_name
                time_ref = time

        if best_bid > best_ask and time_ref:
            percent = (best_bid - best_ask) / best_ask * 100
            sequence.append({
                "time": time_ref,
                "percent": percent,
                "buy_ex": buy_ex,
                "sell_ex": sell_ex
            })

    return sequence

def plot_symbol(symbol, cutoff):
    exchanges = symbol_exchange_data.get(symbol, {})
    colors = plt.colormaps['tab10']
    fig, (ax_price, ax_arbitrage) = plt.subplots(
        2, 1, figsize=(36, 8), sharex=True,
        gridspec_kw={'height_ratios': [2, 1]}
    )
    plotted = False

    # Price plot
    for idx, (exchange, data) in enumerate(exchanges.items()):
        times, bids, asks = zip(*[
            (t, b, a) for t, b, a in zip(data['times'], data['bid'], data['ask']) if t >= cutoff
        ])
        if not times or not is_price_valid(bids) or not is_price_valid(asks):
            continue
        color = colors(idx % 10)
        ax_price.plot(times, asks, label=f"{exchange} Ask", color=color, linestyle='-')
        ax_price.plot(times, bids, label=f"{exchange} Bid", color=color, linestyle='--')
        plotted = True

    if not plotted:
        print(f"⏭️ Skipping {symbol}: No valid price data.")
        plt.close()
        return

    ax_price.set_title(f"{symbol} Price Comparison Across Exchanges (last {PLOT_INTERVAL_SECONDS // 60} min)")
    ax_price.set_ylabel("Price")
    ax_price.grid(True)
    ax_price.legend()

    # Arbitrage percentage subplot
    sequence = compute_best_percent_spread_sequence(symbol, cutoff)
    if not sequence:
        print(f"⏭️ Skipping {symbol}: No valid arbitrage data.")
        plt.close()
        return

    segments = []
    prev_combo = None
    times, percents = [], []

    for point in sequence:
        combo = (point["buy_ex"], point["sell_ex"])
        if combo != prev_combo and times:
            segments.append((times, percents, prev_combo))
            times, percents = [], []
        times.append(point["time"])
        percents.append(point["percent"])
        prev_combo = combo

    if times:
        segments.append((times, percents, prev_combo))

    for idx, (t_list, p_list, (buy_ex, sell_ex)) in enumerate(segments):
        label = f"{buy_ex} → {sell_ex}"
        color = colors(idx % 10)
        ax_arbitrage.plot(t_list, p_list, label=label, color=color, linewidth=2)

    ax_arbitrage.set_title(f"{symbol} Optimal Arbitrage Route (Spread %)")
    ax_arbitrage.set_ylabel("Spread (%)")
    ax_arbitrage.set_xlabel("Time")
    ax_arbitrage.grid(True)
    ax_arbitrage.legend()

    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("imgs", f"{symbol}_spread_percent_{timestamp}.png")
    plt.savefig(filename)
    plt.close()
    print(f"🟢 Saved chart: {filename}")

async def periodic_plot_task():
    while True:
        await asyncio.sleep(PLOT_INTERVAL_SECONDS)
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=PLOT_INTERVAL_SECONDS)
        prune_old_data()
        for symbol in active_symbols:
            plot_symbol(symbol, cutoff)

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

        warn = f"👉👉👉👉👉👉👉👉👉👉👉👉👉⚠️⚠️⚠️⚠️⚠️⚠️ {exchange}" if bid1 == 0 and ask1 == 0 else ""

        print(
            f"{snapshot.timestamp_hms} | [{exchange}] | {snapshot.raw_symbol} | {symbol} | "
            f"Bid: {bid1:.2f} ({snapshot.bid_vol1:.2f}) | Ask: {ask1:.2f} ({snapshot.ask_vol1:.2f}) | {warn}"
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
