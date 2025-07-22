import asyncio
import datetime
import os
import shutil
from collections import defaultdict
import matplotlib.pyplot as plt

# from dispatcher.manager_pro import ExchangeManager
from dispatcher.manager import ExchangeManager

# 🔧 配置参数
DATA_RETENTION_MINUTES = 3
PLOT_INTERVAL_SECONDS = 60

# 🌊 实时数据容器
active_symbols = set()
symbol_exchange_data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'bid': [], 'ask': []}))

def prepare_image_folder():
    """准备图像保存目录（清空后重新创建）"""
    folder = 'imgs'
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

def prune_old_data():
    """清理超过保留时间的数据"""
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=DATA_RETENTION_MINUTES)
    for symbol, exchanges in symbol_exchange_data.items():
        for exchange, data in exchanges.items():
            times = data['times']
            idx = next((i for i, t in enumerate(times) if t >= cutoff), len(times))
            data['times'] = times[idx:]
            data['bid'] = data['bid'][idx:]
            data['ask'] = data['ask'][idx:]

def is_price_valid(prices):
    """价格序列是否合法"""
    return all(p > 0 for p in prices)

def compute_arbitrage_spread(symbol):
    """计算套利价差（taker-taker模式）"""
    exchanges = symbol_exchange_data.get(symbol, {})
    timestamps, spreads, percents = [], [], []

    best_point = {
        "spread": 0,
        "percent": 0,
        "time": None,
        "buy_exchange": "",
        "sell_exchange": ""
    }

    if not exchanges:
        return [], [], [], None

    sample_count = len(next(iter(exchanges.values()))['times'])

    for i in range(sample_count):
        best_bid = -float("inf")
        best_ask = float("inf")
        time_ref, buy_ex, sell_ex = None, "", ""

        for ex_name, data in exchanges.items():
            if i >= len(data['times']):
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
            spread = best_bid - best_ask
            percent = (spread / best_ask) * 100
            timestamps.append(time_ref)
            spreads.append(spread)
            percents.append(percent)

            if spread > best_point["spread"]:
                best_point.update({
                    "spread": spread,
                    "percent": percent,
                    "time": time_ref,
                    "buy_exchange": buy_ex,
                    "sell_exchange": sell_ex
                })

    return timestamps, spreads, percents, best_point if best_point["time"] else None

def plot_symbol(symbol):
    """绘制价格和套利图表"""
    exchanges = symbol_exchange_data.get(symbol, {})
    colors = plt.colormaps['tab10']
    fig, (ax_price, ax_arbitrage) = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True,
        gridspec_kw={'height_ratios': [2, 1]}
    )
    plotted = False

    # 📈 主图：Bid / Ask 曲线
    for idx, (exchange, data) in enumerate(exchanges.items()):
        times, bids, asks = data['times'], data['bid'], data['ask']
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

    ax_price.set_title(f"{symbol} Price Comparison Across Exchanges ({DATA_RETENTION_MINUTES} min)")
    ax_price.set_ylabel("Price")
    ax_price.grid(True)
    ax_price.legend()

    # 💰 子图：套利价差 + 最大点标注
    times, spreads, percents, best_point = compute_arbitrage_spread(symbol)
    ax_arbitrage.plot(times, spreads, label="Spread (USD)", color="purple")
    ax_arbitrage.plot(times, percents, label="Spread (%)", color="orange")

    ax_arbitrage.set_title(f"{symbol} Arbitrage Spread (Taker-Taker)")
    ax_arbitrage.set_ylabel("Spread / %")
    ax_arbitrage.set_xlabel("Time")
    ax_arbitrage.grid(True)
    ax_arbitrage.legend()

    if best_point:
        ax_arbitrage.annotate(
            f"Max Spread: {best_point['spread']:.2f} USD ({best_point['percent']:.2f}%)\n"
            f"Buy: {best_point['buy_exchange']} | Sell: {best_point['sell_exchange']}",
            xy=(best_point["time"], best_point["spread"]),
            xytext=(best_point["time"], best_point["spread"] * 1.2),
            arrowprops=dict(arrowstyle="->", color="red"),
            fontsize=10,
            color="darkred",
            bbox=dict(boxstyle="round", fc="white", ec="red")
        )

    plt.tight_layout()
    plt.gcf().autofmt_xdate()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("imgs", f"{symbol}_arbitrage_{timestamp}.png")
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
        bid1, ask1 = snapshot.bid1, snapshot.ask1
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
