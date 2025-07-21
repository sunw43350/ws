import os

project_root = "market_ws_collector"

folders = [
    "connectors",
    "dispatcher",
    "models",
    "pipelines",
    "utils"
]

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def write_file(path, content):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)

def create_async_project():
    mkdir(project_root)
    for folder in folders:
        mkdir(os.path.join(project_root, folder))
        write_file(os.path.join(project_root, folder, "__init__.py"), "")

    # models/base.py
    write_file(os.path.join(project_root, "models", "base.py"), """\
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

    # connectors/base.py
    write_file(os.path.join(project_root, "connectors", "base.py"), """\
from abc import ABC, abstractmethod

class BaseAsyncConnector(ABC):
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name

    @abstractmethod
    async def connect(self): pass
    @abstractmethod
    async def subscribe(self, request): pass
    @abstractmethod
    async def run(self): pass
""")

    # connectors/binance.py
    write_file(os.path.join(project_root, "connectors", "binance.py"), """\
import asyncio
import websockets
import json
from connectors.base import BaseAsyncConnector
from models.base import SubscriptionRequest, MarketSnapshot
import time

class Connector(BaseAsyncConnector):
    def __init__(self):
        super().__init__("binance")
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect("wss://stream.binance.com:9443/ws")

    async def subscribe(self, request: SubscriptionRequest):
        msg = {
            "method": "SUBSCRIBE",
            "params": [f"{request.symbol.lower()}@bookTicker"],
            "id": 1
        }
        await self.ws.send(json.dumps(msg))

    async def run(self):
        await self.connect()
        await self.subscribe(SubscriptionRequest("btcusdt"))

        while True:
            raw = await self.ws.recv()
            data = json.loads(raw)
            if "s" in data and "b" in data and "a" in data:
                snapshot = MarketSnapshot(
                    exchange=self.exchange_name,
                    symbol=data["s"],
                    best_bid=float(data["b"]),
                    best_ask=float(data["a"]),
                    timestamp=time.time()
                )
                print(f"📊 {snapshot.symbol} | 买一: {snapshot.best_bid} | 卖一: {snapshot.best_ask}")
""")

    # dispatcher/manager.py
    write_file(os.path.join(project_root, "dispatcher", "manager.py"), """\
import asyncio
from connectors import binance  # 可扩展为动态导入

class ExchangeManager:
    def __init__(self):
        self.connectors = [
            binance.Connector()
            # 添加其他 Connector 实例
        ]

    async def run_all(self):
        tasks = [asyncio.create_task(conn.run()) for conn in self.connectors]
        await asyncio.gather(*tasks)
""")

    # pipelines/collector.py
    write_file(os.path.join(project_root, "pipelines", "collector.py"), """\
class CollectorPipeline:
    @staticmethod
    async def run():
        while True:
            await asyncio.sleep(5)
            # 可连接到 DB、消息队列、策略等
""")

    # utils/logger.py
    write_file(os.path.join(project_root, "utils", "logger.py"), """\
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

    # main.py
    write_file(os.path.join(project_root, "main.py"), """\
import asyncio
from dispatcher.manager import ExchangeManager
from pipelines.collector import CollectorPipeline

async def main():
    manager = ExchangeManager()
    await asyncio.gather(
        manager.run_all(),
        CollectorPipeline.run()
    )

if __name__ == "__main__":
    asyncio.run(main())
""")

    print(f"✅ 已成功创建 asyncio 项目结构于：./{project_root}")

if __name__ == "__main__":
    create_async_project()
