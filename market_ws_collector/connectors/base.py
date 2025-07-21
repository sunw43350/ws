from abc import ABC, abstractmethod
import zlib

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
            decompress = zlib.decompress()
            return decompress.decompress(payload) + decompress.flush()
        except Exception:
            return b""

