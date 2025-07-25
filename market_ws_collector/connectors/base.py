import asyncio
import datetime
import json
import gzip
import zlib
import logging

from abc import ABC, abstractmethod

# log_filename = f"log/log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_prefix = f"log/log"
log_dt = f"{datetime.datetime.now().strftime('%m%d_%H%M%S')}"


import os

log_dir = "./log"  # log 目录路径

def clean_log_dir(log_dir: str = "./log"):
    # 如果 log 目录不存在，创建它
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"✅ 创建 log 目录：{log_dir}")
        return

    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
            print(f"🗑️ 已删除文件：{filepath}")

clean_log_dir(log_dir)
clean_log_dir("snapshots")  # 清理 snapshots 目录


class BaseAsyncConnector(ABC):
    def __init__(
        self,
        exchange: str,
        compression: str = None,  # None / "gzip" / "zlib"
        ping_interval: int = 20,
        ping_payload=None,        # dict / str / bytes
        pong_keywords=None,
        log_filename=None,
        max_retries: int = 10
    ):
        self.exchange_name = exchange
        self.compression = compression
        self.ping_interval = ping_interval
        self.ping_payload = ping_payload
        self.pong_keywords = pong_keywords
        self.ws = None
        self._stop = False
        self._ws_alive = True
        self.retries = 0
        self.max_retries = max_retries

        # 设置日志系统
        self.logger = logging.getLogger(exchange)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        log_filename = f"{log_prefix}_{exchange}_{log_dt}.txt"

        if log_filename:
            fh = logging.FileHandler(log_filename, encoding='utf-8')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        else:
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            self.logger.addHandler(sh)

    @abstractmethod
    async def connect(self): pass

    @abstractmethod
    async def subscribe(self): pass

    @abstractmethod
    def format_symbol(self, generic_symbol: str): pass

    @abstractmethod
    async def handle_message(self, data): pass

    async def keep_alive(self):
        if not self.ping_payload:
            return

        while not self._stop:
            try:
                if self.ws:
                    payload = (
                        json.dumps(self.ping_payload)
                        if isinstance(self.ping_payload, dict)
                        else self.ping_payload
                    )
                    await self.ws.send(payload)
                    self.log(f"🔁 发送心跳: {payload}")
                await asyncio.sleep(self.ping_interval)
            except Exception as e:
                self._ws_alive = False
                self.log(f"⚠️ 心跳发送失败: {e}", level="WARNING")
                break

    async def receive_loop(self):
        try:
            async for raw in self.ws:
                try:
                    if isinstance(raw, bytes):
                        raw = self._decompress(raw)
                    data = json.loads(raw)
                    await self.handle_message(data)
                    
                except Exception as e:
                    self.log(f"消息解析失败: {e} | raw: {raw}", level="WARNING")
                    
        except Exception as e:
            self.log(f"接收循环异常: {e}", level="ERROR")
            raise

    def _decompress(self, raw: bytes) -> str:
        try:
            if self.compression == "gzip":
                return gzip.decompress(raw).decode("utf-8")
            elif self.compression == "zlib":
                return zlib.decompress(raw).decode("utf-8")
            return raw.decode("utf-8")
        except Exception:
            return ""

    def log(self, message: str, level="INFO"):
        print(f"[{self.exchange_name}] {message}")
        if level == "INFO":
            self.logger.info(f"[{self.exchange_name}] {message}")
        elif level == "WARNING":
            self.logger.warning(f"[{self.exchange_name}] {message}")
        elif level == "ERROR":
            self.logger.error(f"[{self.exchange_name}] {message}")
        else:
            self.logger.debug(f"[{self.exchange_name}] {message}")

    def stop(self):
        self._stop = True
        if self.ws:
            asyncio.create_task(self.ws.close())

    async def on_connected(self):
        self.log("WebSocket 已连接")

    async def on_disconnected(self):
        self.log("WebSocket 已断开")

    async def run_forever(self):
        while not self._stop:
            try:
                self.retries += 1
                if self.retries > self.max_retries:
                    self.log("超过最大重连次数, 终止", level="ERROR")
                    break

                await self._run_once()
            except Exception as e:
                self.log(f"异常: {e}", level="ERROR")
                await self.on_disconnected()
                await asyncio.sleep(1)

    async def _run_once(self):
        await self.connect()
        await self.on_connected()
        await self.subscribe()

        await asyncio.gather(
            self.receive_loop(),
            self.keep_alive()
        )

    async def run(self):
        await self.run_forever()