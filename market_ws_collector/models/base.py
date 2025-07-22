# import datetime
from datetime import datetime
class SubscriptionRequest:
    def __init__(self, symbol, channel="ticker", depth_level=0):
        self.symbol = symbol
        self.channel = channel
        self.depth_level = depth_level


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
        raw_symbol=None
    ):
        self.exchange = exchange            # 交易所名称
        self.symbol = symbol                # 合约格式，例如 PI_XBTUSD
        self.raw_symbol = raw_symbol        # 原始币种格式，例如 BTC-USDT
        self.bid1 = bid1                    # 买一价
        self.ask1 = ask1                    # 卖一价
        self.bid_vol1 = bid_vol1            # 买一量
        self.ask_vol1 = ask_vol1            # 卖一量
        self.total_volume = total_volume    # 总成交量（可选）
        self.timestamp = timestamp          # 毫秒级时间戳
        self.timestamp_iso = self.to_iso(timestamp)  # ISO 格式时间
        self.timestamp_hms = self.to_hms(timestamp)


    def to_iso(self, ts_ms: int) -> str:
        try:
            return datetime.fromtimestamp(ts_ms / 1000).isoformat(timespec="milliseconds") + "Z"
        except:
            return ""
        
    def to_hms(self, ts_ms: int) -> str:
        try:
            return datetime.fromtimestamp(ts_ms / 1000).strftime("%H:%M:%S")
        except:
            return ""
