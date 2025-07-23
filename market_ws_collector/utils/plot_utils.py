import os
import datetime
import matplotlib.pyplot as plt

def is_price_valid(prices):
    return all(p > 0 for p in prices)

def plot_symbol(symbol, exchanges, cutoff, output_folder="imgs"):
    colors = plt.colormaps['tab10']
    fig, (ax_price, ax_arbitrage) = plt.subplots(
        2, 1, figsize=(36, 8), sharex=True,
        gridspec_kw={'height_ratios': [2, 1]}
    )
    plotted = False

    # 绘制价格数据
    for idx, (exchange, data) in enumerate(exchanges.items()):
        filtered_data = [
            (t, b, a) for t, b, a in zip(data['times'], data['bid'], data['ask']) if t >= cutoff
        ]
        if not filtered_data:
            print(f"⏭️ Skipping {symbol} ({exchange}): No data within cutoff.")
            continue
        
        times, bids, asks = zip(*filtered_data)
        if not is_price_valid(bids) or not is_price_valid(asks):
            continue
        color = colors(idx % 10)
        ax_price.plot(times, asks, label=f"{exchange} Ask", color=color, linestyle='-')
        ax_price.plot(times, bids, label=f"{exchange} Bid", color=color, linestyle='--')
        plotted = True

    if not plotted:
        print(f"⏭️ Skipping {symbol}: No valid price data.")
        plt.close()
        return

    ax_price.set_title(f"{symbol} Price Comparison Across Exchanges")
    ax_price.set_ylabel("Price")
    ax_price.grid(True)
    ax_price.legend()

    # 绘制套利数据
    # 示例中未拆分，但可以调用与套利相关的函数或数据
    ax_arbitrage.set_title(f"{symbol} Optimal Arbitrage Route (Spread %)")
    ax_arbitrage.set_ylabel("Spread (%)")
    ax_arbitrage.set_xlabel("Time")
    ax_arbitrage.grid(True)
    ax_arbitrage.legend()

    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_folder, f"{symbol}_spread_percent_{timestamp}.png")
    plt.savefig(filename)
    plt.close()
    print(f"🟢 Saved chart: {filename}")
