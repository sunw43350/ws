import os

project_root = "market_ws_collector"

folders = [
    "models",
    "connectors",
    "utils"
]

exchange_modules = [
    "ascendex", "binance", "bingx", "bitfinex", "bitget", "bitmart", "bitmex",
    "bitrue", "blofin", "bybit", "coinbase", "cryptocom", "digifinex",
    "gateio", "huobi", "krakenfutures", "lbank", "mexc", "okx", "oxfun", "phemex"
]

def create_structure():
    # 根目录
    os.makedirs(project_root, exist_ok=True)

    # 子目录
    for folder in folders:
        os.makedirs(os.path.join(project_root, folder), exist_ok=True)

    # 模型文件
    model_file = os.path.join(project_root, "models", "base.py")
    if not os.path.exists(model_file):
        with open(model_file, "w") as f:
            f.write("""\
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
""")

    # 每个交易所模块
    for name in exchange_modules:
        path = os.path.join(project_root, "connectors", f"{name}.py")
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(f"""\
# {name}.py
from connectors.base import BaseConnector
from models.base import SubscriptionRequest, MarketSnapshot

class Connector(BaseConnector):
    def connect(self):
        pass

    def subscribe(self, request: SubscriptionRequest):
        pass

    def run_forever(self):
        pass
""")

    # 抽象父类
    base_connector = os.path.join(project_root, "connectors", "base.py")
    if not os.path.exists(base_connector):
        with open(base_connector, "w") as f:
            f.write("""\
from abc import ABC, abstractmethod

class BaseConnector(ABC):
    def __init__(self):
        self.exchange_name = self.__class__.__name__.replace("Connector", "")

    @abstractmethod
    def connect(self): pass
    @abstractmethod
    def subscribe(self, request): pass
    @abstractmethod
    def run_forever(self): pass
""")

    # 日志工具
    logger_file = os.path.join(project_root, "utils", "logger.py")
    if not os.path.exists(logger_file):
        with open(logger_file, "w") as f:
            f.write("""\
import logging

def get_logger(name="market_ws"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
""")

    # 主入口文件
    main_file = os.path.join(project_root, "main.py")
    if not os.path.exists(main_file):
        with open(main_file, "w") as f:
            f.write("""\
from models.base import SubscriptionRequest
from connectors import binance, bitmex, blofin

def main():
    connectors = [binance.Connector(), bitmex.Connector(), blofin.Connector()]
    for conn in connectors:
        conn.connect()
        req = SubscriptionRequest(symbol="BTC-USDT")
        conn.subscribe(req)
        conn.run_forever()

if __name__ == "__main__":
    main()
""")

    print(f"✅ 成功创建项目结构于: ./{project_root}/")

if __name__ == "__main__":
    create_structure()
