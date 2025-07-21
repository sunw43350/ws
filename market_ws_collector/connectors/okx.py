# okx.py
from connectors.base import BaseConnector
from models.base import SubscriptionRequest, MarketSnapshot

class Connector(BaseConnector):
    def connect(self):
        pass

    def subscribe(self, request: SubscriptionRequest):
        pass

    def run_forever(self):
        pass
