当然 ✅！下面是为你整理的完整汇总文档，记录了当前已完成的 WebSocket Connector 模块详情。内容涵盖：

WebSocket 接入地址（WS_URL）

订阅频道结构（channel 或 method）

支持的 symbol 格式

推送字段结构（如 bid/ask）

快照构造说明

📘 Market WebSocket Connector 汇总

🗂 汇总列表（共 21 个交易所）

Exchange

WS 地址

订阅结构/频道

Symbol 特征

Ascendex

wss://ascendex.com/api/pro/v1/stream

depth

BTC/USDT

Binance

wss://stream.binance.com:9443/ws

ticker / depth

btcusdt

BingX

wss://ws.bingx.com/market

market.ticker

BTC-USDT

Bitfinex

wss://api-pub.bitfinex.com/ws/2

numeric channel

tBTCUSD

Bitget

wss://ws.bitget.com/mix/v1/market

books, ticker

BTCUSDT_UMCBL

Bitmart

wss://ws-manager-compress.bitmart.com/api?protocol=1.1

spot/ticker, spot/depth5

BTC_USDT

Bitmex

wss://www.bitmex.com/realtime

orderBookL2

XBTUSD

Bitrue

wss://ws.bitruemarket.com

depth, trade

btcusdt

Blofin

wss://api.blofin.com/ws/v1/public

futures.ticker

BTC_USDT

Bybit

wss://stream.bybit.com/v5/public

tickers, orderbook

BTCUSDT

Coinbase

wss://ws-feed.exchange.coinbase.com

ticker, level2

BTC-USD

Crypto.com

wss://stream.crypto.com/v2/market

subscribe

BTC_USDT

Digifinex

wss://openws.digifinex.com

ticker, order_book

btcusdt

Gate.io

wss://fx-ws.gate.io/v4/ws

futures.book_ticker

BTC_USDT

Huobi

wss://api.huobi.pro/ws

market.{symbol}.ticker

btcusdt

Kraken Futures

wss://futures.kraken.com/ws/v1

book, ticker

PI_XBTUSD

LBank

wss://www.lbkex.net/ws/V2/

depth

btc_usdt

MEXC

wss://contract.mexc.com/edge

sub.ticker

BTC_USDT

OKX

wss://ws.okx.com:8443/ws/v5/public

tickers

BTC-USDT

OX.FUN

wss://api.ox.fun/v2/websocket

depth:{symbol}

BTC-USD-SWAP-LIN

Phemex

wss://ws.phemex.com

orderbook.subscribe

BTCUSD

🔎 通用 Symbol 映射说明

标准格式输入

映射后格式用于订阅

使用平台示例

BTC-USDT

btcusdt

Binance, Huobi

BTC-USDT

BTC_USDT

Gate.io, Bitmart

BTC-USDT

BTC-USD-SWAP-LIN

OX.FUN

BTC-USDT

BTCUSD

Phemex, Bybit

BTC-USDT

BTCUSDT_UMCBL

Bitget

建议统一使用 SymbolFormatter 工具类进行格式化，确保订阅结构与推送字段匹配。

🧩 推送字段结构（示例）

🛒 常见深度字段（depth）

字段名

含义

bids

买单列表 [price, volume]

asks

卖单列表 [price, volume]

bid1

买一价格

ask1

卖一价格

bidSize

买一挂单量

askSize

卖一挂单量

timestamp

毫秒时间戳

📊 快照结构建议

标准化构造 MarketSnapshot 时推荐字段：

MarketSnapshot(
    exchange = "bitget",
    symbol = "BTCUSDT_UMCBL",
    raw_symbol = "BTC-USDT",
    bid1 = 11750.23,
    ask1 = 11751.12,
    bid_vol1 = 123.45,
    ask_vol1 = 120.08,
    total_volume = 555555.0,
    timestamp = 1753150000000
)

建议统一转为毫秒级时间戳，价格使用 float，数量字段使用 float 或 int 视实际数据而定。

