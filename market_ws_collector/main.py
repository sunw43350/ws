import asyncio
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# from dispatcher.manager_pro import ExchangeManager  # 如果你使用高级连接器版本
from dispatcher.manager import ExchangeManager         # 默认连接器

# 🔧 配置参数
DATA_RETENTION_MINUTES = 1        # 数据保留时间（单位：分钟）
PLOT_INTERVAL_SECONDS = 10        # 每隔多少秒画一次图（可自行修改）

# 🧠 实时活跃合约symbol集合
active_symbols = set()

# 📊 数据结构：{symbol: {exchange: {'times': [], 'bid': [], 'ask': []}}}
symbol_exchange_data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'bid': [], 'ask': []}))


def prune_old_data():
    """⏳ 清理超过保留时间的数据"""
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=DATA_RETENTION_MINUTES)
    for symbol, exchanges in symbol_exchange_data.items():
        for exchange, data in exchanges.items():
            times = data['times']
            idx = next((i for i, t in enumerate(times) if t >= cutoff), len(times))
            data['times'] = times[idx:]
            data['bid'] = data['bid'][idx:]
            data['ask'] = data['ask'][idx:]


def plot_symbol(symbol):
    """📈 绘制某个symbol的价格图"""
    plt.figure(figsize=(12, 6))
    exchanges = symbol_exchange_data.get(symbol, {})
    colors = plt.cm.get_cmap('tab10')

    for idx, (exchange, data) in enumerate(exchanges.items()):
        times = data['times']
        bids = data['bid']
        asks = data['ask']

        if not times:
            continue

        color = colors(idx % 10)
        plt.plot(times, asks, label=f"{exchange} ask", color=color, linestyle='-')
        plt.plot(times, bids, label=f"{exchange} bid", color=color, linestyle='--')

    plt.title(f"{symbol} 不同交易所买卖价格走势（最近 {DATA_RETENTION_MINUTES} 分钟）")
    plt.xlabel("时间")
    plt.ylabel("价格")
    plt.legend()
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_prices_{timestamp_str}.png"
    plt.savefig(filename)
    plt.close()
    print(f"✅ 图表已保存: {filename}")


async def periodic_plot_task():
    """⏱️ 定时绘图任务，每 PLOT_INTERVAL_SECONDS 秒执行一次"""
    while True:
        await asyncio.sleep(PLOT_INTERVAL_SECONDS)
        prune_old_data()
        for symbol in active_symbols:
            plot_symbol(symbol)


async def consume_snapshots(queue: asyncio.Queue):
    """📥 处理实时快照数据"""
    while True:
        snapshot = await queue.get()

        symbol = snapshot.symbol
        exchange = snapshot.exchange
        bid1 = snapshot.bid1
        ask1 = snapshot.ask1
        timestamp = datetime.datetime.now()

        # ✨ 记录活跃symbol
        active_symbols.add(symbol)

        # ✍️ 记录行情数据
        data = symbol_exchange_data[symbol][exchange]
        data['times'].append(timestamp)
        data['bid'].append(bid1)
        data['ask'].append(ask1)

        print(
            f"📦 [{exchange}] {snapshot.timestamp_hms} | {snapshot.raw_symbol} | {symbol} | "
            f"买一: {bid1:.2f} ({snapshot.bid_vol1:.2f}) | 卖一: {ask1:.2f} ({snapshot.ask_vol1:.2f})"
        )

        queue.task_done()


async def main():
    snapshot_queue = asyncio.Queue()
    manager = ExchangeManager(queue=snapshot_queue)

    await asyncio.gather(
        manager.run_all(),                  # 连接并运行所有交易所
        consume_snapshots(snapshot_queue),  # 实时处理快照数据
        periodic_plot_task()                # 定期画图任务
    )


if __name__ == "__main__":
    asyncio.run(main())
