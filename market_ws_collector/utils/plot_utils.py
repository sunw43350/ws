import os
import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def is_price_valid(prices):
    return all(p > 0 for p in prices)

def plot_symbol_interactive(symbol, exchanges, cutoff, output_folder="imgs"):
    os.makedirs(output_folder, exist_ok=True)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.08,
        subplot_titles=(f"{symbol} Price Comparison Across Exchanges", f"{symbol} Optimal Arbitrage Route (Spread %)"),
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

        fig.add_trace(go.Scatter(
            x=times, y=asks, mode='lines',
            name=f"{exchange} Ask", line=dict(dash='solid')
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=times, y=bids, mode='lines',
            name=f"{exchange} Bid", line=dict(dash='dash')
        ), row=1, col=1)

        plotted = True

    if not plotted:
        print(f"⏭️ Skipping {symbol}: No valid price data.")
        return

    # 套利数据（可扩展填充）
    # 暂时占位，实际可接入你的套利结果
    # 例：fig.add_trace(go.Scatter(...), row=2, col=1)

    fig.update_layout(
        height=600,
        title=f"{symbol} Price + Arbitrage Spread",
        xaxis2_title="Time",
        yaxis1_title="Price",
        yaxis2_title="Spread (%)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_folder, f"{symbol}_interactive_{timestamp}.html")
    fig.write_html(filename)
    print(f"🟢 Saved interactive chart: {filename}")
