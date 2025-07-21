from abc import ABC, abstractmethod

class BaseAsyncConnector(ABC):
    def __init__(self):
        self.exchange_name = self.__class__.__name__.replace("Connector", "")

    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def subscribe(self, request): pass

    @abstractmethod
    def run_forever(self): pass
