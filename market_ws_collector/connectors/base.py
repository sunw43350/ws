from abc import ABC, abstractmethod
import zlib
import datetime

filename = "./log/" + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'


class BaseAsyncConnector(ABC):
    def __init__(self, exchange: str):
        self.exchange_name = exchange

    @abstractmethod
    async def connect(self): pass

    @abstractmethod
    async def subscribe(self): pass

    @abstractmethod
    async def run(self): pass

    @abstractmethod
    def format_symbol(self, generic_symbol: str): pass

    def inflate(self, payload: bytes) -> bytes:
        """默认 zlib 解压实现（适用于 Bitget）"""
        try:
            return zlib.decompress(payload)
        except Exception:
            return b""

    def extract_top_bid_ask(self, bids, asks):
        """
        提取买一 / 卖一价格和数量
        输入格式应为：[[price, qty], ...]
        """
        bid1, bid_vol1 = map(float, bids[0]) if bids else (0.0, 0.0)
        ask1, ask_vol1 = map(float, asks[0]) if asks else (0.0, 0.0)
        return bid1, bid_vol1, ask1, ask_vol1

    def format_snapshot(self, snapshot) -> str:
        """
        快照日志格式化输出（依赖 snapshot 的属性结构）
        """
        return (
            f"[{self.exchange_name}] {snapshot.timestamp_hms} | "
            f"{snapshot.raw_symbol} | {snapshot.symbol} | "
            f"买一: {snapshot.bid1:.2f} ({snapshot.bid_vol1:.2f}) | "
            f"卖一: {snapshot.ask1:.2f} ({snapshot.ask_vol1:.2f})"
        )

    def log(self, message: str, msg_more: str = ""):
        print(message)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"{now} | {self.exchange_name}: {message} | {msg_more}\n")
