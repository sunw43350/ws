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
        total_volume=None
    ):
        self.exchange = exchange        # 交易所名称
        self.symbol = symbol            # 合约或币种名称
        self.bid1 = bid1                # 买一价
        self.ask1 = ask1                # 卖一价
        self.timestamp = timestamp      # 时间戳

        self.bid_vol1 = bid_vol1        # 买一量
        self.ask_vol1 = ask_vol1        # 卖一量
        self.total_volume = total_volume  # 总成交量（可选）
