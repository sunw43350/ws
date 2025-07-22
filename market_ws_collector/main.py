import asyncio
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import asyncio
# from dispatcher.manager_pro import ExchangeManager  # 调度器管理多个交易所连接器
from dispatcher.manager import ExchangeManager  # 调度器管理多个交易所连接器


# 配置参数
DATA_RETENTION_MINUTES = 1    # 保留10分钟数据
PLOT_INTERVAL_MINUTES = 1     # 每10分钟画一次图
PLOT_SYMBOLS = ['AAVE-USDT', '1INCH-USDT']  # 要画图的合约列表

# 数据结构：{symbol: {exchange: {'times': [], 'bid': [], 'ask': []}}}
symbol_exchange_data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'bid': [], 'ask': []}))

def prune_old_data():
    """清理超过保留时间的数据"""
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=DATA_RETENTION_MINUTES)
    for symbol, exchanges in symbol_exchange_data.items():
        for exchange, data in exchanges.items():
            # 找到第一个满足时间 >= cutoff 的索引
            times = data['times']
            idx = 0
            for i, t in enumerate(times):
                if t >= cutoff:
                    idx = i
                    break
            # 剪切所有数据，只保留最近的
            data['times'] = times[idx:]
            data['bid'] = data['bid'][idx:]
            data['ask'] = data['ask'][idx:]

def plot_symbol(symbol):
    plt.figure(figsize=(12, 6))
    exchanges = symbol_exchange_data.get(symbol, {})
    colors = plt.cm.get_cmap('tab10')

    for idx, (exchange, data) in enumerate(exchanges.items()):
        times = data['times']
        bids = data['bid']
        asks = data['ask']

        if len(times) == 0:
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

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{symbol}_prices_{timestamp_str}.png"
    plt.savefig(filename)
    plt.close()
    print(f"✅ 已保存图表: {filename}")

async def periodic_plot_task():
    """定时绘图任务，每 PLOT_INTERVAL_MINUTES 分钟执行一次"""
    while True:
        await asyncio.sleep(PLOT_INTERVAL_MINUTES * 60)
        prune_old_data()
        for symbol in PLOT_SYMBOLS:
            plot_symbol(symbol)

async def consume_snapshots(queue: asyncio.Queue):
    while True:
        snapshot = await queue.get()

        symbol = snapshot.symbol
        exchange = snapshot.exchange
        bid1 = snapshot.bid1
        ask1 = snapshot.ask1
        timestamp = datetime.datetime.now()

        # 记录数据
        data = symbol_exchange_data[symbol][exchange]
        data['times'].append(timestamp)
        data['bid'].append(bid1)
        data['ask'].append(ask1)

        # 输出日志
        print(
            f"📥 [{exchange}] {snapshot.timestamp_hms} | {snapshot.raw_symbol} | {symbol} | "
            f"买一: {bid1:.2f} ({snapshot.bid_vol1:.2f}) | "
            f"卖一: {ask1:.2f} ({snapshot.ask_vol1:.2f})"
        )

        queue.task_done()

async def main():
    snapshot_queue = asyncio.Queue()
    manager = ExchangeManager(queue=snapshot_queue)

    await asyncio.gather(
        manager.run_all(),                # 多交易所行情连接器
        consume_snapshots(snapshot_queue),  # 实时行情消费
        periodic_plot_task()              # 定时绘图任务
    )

if __name__ == "__main__":
    asyncio.run(main())
