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
    def __init__(self, exchange, symbol, best_bid, best_ask, timestamp,
                 bid_volume=None, ask_volume=None, total_volume=None):
        self.exchange = exchange              # 交易所名称
        self.symbol = symbol                  # 合约名称
        self.best_bid = best_bid              # 买一价格
        self.best_ask = best_ask              # 卖一价格
        self.timestamp = timestamp            # 推送时间戳

        self.bid_volume = bid_volume          # 买一量（可选）
        self.ask_volume = ask_volume          # 卖一量（可选）
        self.total_volume = total_volume      # 总成交量（可选）
