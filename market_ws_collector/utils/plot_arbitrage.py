import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from itertools import cycle
from collections import defaultdict

# 🎨 自动分配交易所颜色
_color_palette = cycle([
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
])
_exchange_color_map = {}

def get_color_for_exchange(exchange: str):
    exchange = exchange.upper()
    if exchange not in _exchange_color_map:
        _exchange_color_map[exchange] = next(_color_palette)
    return _exchange_color_map[exchange]

def plot_arbitrage_snapshot(symbol: str, symbol_data: dict, output_dir: str = "image", window_minutes: int = 1):
    if not symbol_data:
        print(f"⚠️ 无数据可绘制: {symbol}")
        return

    now = datetime.now()
    cutoff = now - timedelta(minutes=window_minutes)
    os.makedirs(output_dir, exist_ok=True)
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    spread_percent_list = []
    spread_time_list = []
    spread_meta = []

    # 📈 子图1：Bid/Ask 曲线（按秒过滤）
    second_groups = defaultdict(lambda: defaultdict(lambda: {'bid': None, 'ask': None}))
    for exchange, data in symbol_data.items():
        times = data['times']
        bids = data['bid']
        asks = data['ask']
        filtered = [(t, b, a) for t, b, a in zip(times, bids, asks) if t >= cutoff]
        if not filtered:
            continue
        filtered_times, filtered_bids, filtered_asks = zip(*filtered)

        color = get_color_for_exchange(exchange)
        axs[0].plot(filtered_times, filtered_asks, label=f"{exchange} Ask", color=color, alpha=0.7, linestyle='-')
        axs[0].plot(filtered_times, filtered_bids, label=f"{exchange} Bid", color=color, alpha=1.0, linestyle='--')

        # 填充秒级聚合容器
        for t, b, a in filtered:
            t_sec = t.replace(microsecond=0)
            second_groups[t_sec][exchange] = {'bid': b, 'ask': a}

    axs[0].legend()
    axs[0].set_ylabel("Price")
    axs[0].set_title(f"{symbol} Exchange Depth (Last {window_minutes} min)")

    # 📊 子图2：按秒级时间聚合套利分析
    for t_sec in sorted(second_groups.keys()):
        bid_list, ask_list, bid_ex, ask_ex = [], [], [], []

        for exchange, values in second_groups[t_sec].items():
            bid = values['bid']
            ask = values['ask']
            bid_list.append(bid)
            ask_list.append(ask)
            bid_ex.append(exchange)
            ask_ex.append(exchange)

        if not bid_list or not ask_list:
            continue
        max_bid = max(bid_list)
        min_ask = min(ask_list)
        if min_ask == 0:
            continue
        spread = (max_bid - min_ask) / min_ask * 100
        sell_ex = bid_ex[bid_list.index(max_bid)]
        buy_ex = ask_ex[ask_list.index(min_ask)]

        spread_percent_list.append(spread)
        spread_time_list.append(t_sec)
        spread_meta.append((sell_ex, buy_ex))

    axs[1].plot(spread_time_list, spread_percent_list, color="black", label="Arbitrage %")
    axs[1].set_ylabel("Spread (%)")
    axs[1].set_title("Taker-Taker Arbitrage Opportunity (Per Second)")
    axs[1].legend()

    if spread_percent_list:
        max_idx = spread_percent_list.index(max(spread_percent_list))
        axs[1].scatter(spread_time_list[max_idx], spread_percent_list[max_idx], color="red", zorder=5)
        sell, buy = spread_meta[max_idx]
        txt = f"{spread_percent_list[max_idx]:.2f}% Buy {buy} → Sell {sell}"
        axs[1].annotate(txt,
                        (spread_time_list[max_idx], spread_percent_list[max_idx]),
                        xytext=(10, -15), textcoords='offset points',
                        arrowprops=dict(arrowstyle="->", color="red"), fontsize=10)

    plt.suptitle(f"{symbol} Arbitrage Analysis ({window_minutes} min window)", fontsize=14)
    plt.tight_layout()

    # 💾 命名加绘图周期和时分秒
    timestamp_str = now.strftime("%H-%M-%S")
    chart_name = f"{symbol}_arbitrage_{window_minutes}min_{timestamp_str}.png"
    chart_path = os.path.join(output_dir, chart_name)
    plt.savefig(chart_path)
    plt.close()
    print(f"✅ 图像已保存到: {chart_path}")
