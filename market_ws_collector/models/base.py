class SubscriptionRequest:
    def __init__(self, symbol, channel="ticker", depth_level=0):
        self.symbol = symbol
        self.channel = channel
        self.depth_level = depth_level

class MarketSnapshot:
    def __init__(self, exchange, symbol, best_bid, best_ask, timestamp):
        self.exchange = exchange
        self.symbol = symbol
        self.best_bid = best_bid
        self.best_ask = best_ask
        self.timestamp = timestamp
class MarketSnapshot:
    def __init__(
        self,
        exchange,
        symbol,
        bid1,
        ask1,
        timestamp,
        bid_vol1=None,
        ask_vol1=None,
        total_volume=None,
        raw_symbol=None    # 新增字段：原始未格式化符号
    ):
        self.exchange = exchange
        self.symbol = symbol              # 转换后的格式（如 PI_XBTUSD）
        self.raw_symbol = raw_symbol      # 原始符号（如 BTC-USDT）
        self.bid1 = bid1
        self.ask1 = ask1
        self.bid_vol1 = bid_vol1
        self.ask_vol1 = ask_vol1
        self.total_volume = total_volume
        self.timestamp = timestamp
