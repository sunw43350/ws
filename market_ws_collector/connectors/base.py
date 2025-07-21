from abc import ABC, abstractmethod

class BaseAsyncConnector(ABC):
    def __init__(self):
        self.exchange_name = self.__class__.__name__.replace("Connector", "")

    @abstractmethod
    async def connect(self): pass

    @abstractmethod
    async def subscribe(self, request): pass

    @abstractmethod
    async def run(self): pass

    @abstractmethod
    def format_symbol(self): pass
