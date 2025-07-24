# market_ws_collector/config.py

# ✅ 标准化合约符号（注意：不同交易所格式可能不同）
DEFAULT_SYMBOLS = {
    "ascendex":      ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "krakenfutures": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bingx":         ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bitfinex":      ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bitget":        ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bitmart":       ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bitmex":        ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bitrue":        ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "blofin":        ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bybit":         ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LINK-USDT", "ADA-USDT"],
    "coinbase":      ["BTC-USD", "ETH-USD", "SOL-USD", "LTC-USD", "ADA-USD"],
    "cryptocom":     ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "digifinex":      ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "gateio":        ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "huobi":         ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LTC-USDT", "XRP-USDT"],
    "lbank":         ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LTC-USDT", "XRP-USDT"],
    "mexc":          ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "okx":           ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "oxfun":         ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "phemex":        ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
}


# ✅ 每个交易所 WebSocket 公共行情订阅地址
WS_ENDPOINTS = {
    "ascendex":      "wss://ascendex.com/1/api/pro/v2/stream",
    "krakenfutures": "wss://futures.kraken.com/ws/v1",
    "bingx":         "wss://open-api-ws.bingx.com/market", 
    
    "bitfinex":      "wss://api-pub.bitfinex.com/ws/2",
    "bitget":        "wss://ws.bitget.com/v2/ws/public",
    "bitmart":       "wss://openapi-ws-v2.bitmart.com/api?protocol=1.1",
    "bitmex":        "wss://ws.bitmex.com/realtime",
    "bitrue":        "wss://ws.bitrue.com/kline-api/ws",
    "blofin":        "wss://openapi.blofin.com/ws/public",
    "bybit":         "wss://stream.bybit.com/v5/public/linear",
    "coinbase":      "wss://advanced-trade-ws.coinbase.com",
    "cryptocom":     "wss://stream.crypto.com/exchange/v1/market",
    "digifinex":     "wss://openapi.digifinex.com/swap_ws/v2/",
    "gateio":        "wss://fx-ws.gateio.ws/v4/ws/usdt",
    "huobi":         "wss://api.huobi.pro/ws",
    # "lbank":         "wss://www.lbkex.net/ws/V2/",  
    "lbank":         "wss://ccws.rerrkvifj.com/ws/V3/",  # from page: lbank.com/trade/BTC_USDT
    
    "mexc":          "wss://contract.mexc.com/edge",
    "okx":           "wss://ws.okx.com:8443/ws/v5/public",
    "oxfun":         "wss://api.ox.fun/v2/websocket",
    "phemex":        "wss://ws.phemex.com",
}


DEFAULT_SYMBOLS.update({
    "binance": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT", "ADA-USDT"]
})

WS_ENDPOINTS.update({
    "binance": "wss://stream.binance.com:9443"
})
