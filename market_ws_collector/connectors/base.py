from abc import ABC, abstractmethod

class BaseAsyncConnector(ABC):
    def __init__(self, exchange: str):
        self.exchange_name = exchange

    @abstractmethod
    async def connect(self): pass

    @abstractmethod
    async def subscribe(self, request): pass

    @abstractmethod
    async def run(self): pass

    @abstractmethod
    def format_symbol(self, generic_symbol: str): pass
