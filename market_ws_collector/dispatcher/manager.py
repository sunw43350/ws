# from connectors import ascendex, krakenfutures, bingx, bitfinex, bitget, bitmart, bitmex, bitrue, blofin, bybit, coinbase,cryptocom
from connectors import (
    ascendex, krakenfutures, bingx, bitfinex,
    bitget, bitmart, bitmex, bitrue,
    blofin, bybit, coinbase, cryptocom, digifinex,
    gateio, huobi, lbank, 
    mexc, okx, oxfun, phemex
)

from config import DEFAULT_SYMBOLS
import asyncio

class ExchangeManager:
    def __init__(self, queue):
        self.queue = queue
        self.connectors = [
            # ascendex.Connector(exchange="ascendex", queue=queue),
            # krakenfutures.Connector(exchange="krakenfutures", queue=queue),
            # bingx.Connector(exchange="bingx", queue=queue),  # ✅ 添加 BingX
            # bitget.Connector(exchange="bitget", queue=queue),  # ✅ 添加 Bitget
            # bitmart.Connector(exchange="bitmart", queue=queue),  # ✅ 添加 BitMart
            # bitmex.Connector(exchange="bitmex", queue=queue),  # ✅ 添加 BitMEX
            # bitrue.Connector(exchange="bitrue", queue=queue),  # ✅ 添加 Bitrue
            # blofin.Connector(exchange="blofin", queue=queue),  # ✅ 添加 BloFin
            # bybit.Connector(exchange="bybit", queue=queue),  # ✅ 添加 Bybit
            # coinbase.Connector(exchange="coinbase", queue=queue),  # ✅ 添加 Coinbase
            # cryptocom.Connector(exchange="cryptocom", queue=queue),  # ✅ 添加 Crypto.
            # digifinex.Connector(exchange="digifinex", queue=queue),  # ✅ 添加 Digifinex
            # gateio.Connector(exchange="gateio", queue=queue),  # ✅ 添加 Gate.io
            # huobi.Connector(exchange="huobi", queue=queue),  # ✅ 添加 Huobi
            # lbank.Connector(exchange="lbank", queue=queue),  # ✅ 添加 LBank  LBank 异常: sent 1011 (internal error) keepalive ping timeout; no close frame received
            # mexc.Connector(exchange="mexc", queue=queue),  # ✅ 添加 MEXC slow update/1 second
            # okx.Connector(exchange="okx", queue=queue),  # ✅ 添加 OKX
            # oxfun.Connector(exchange="oxfun", queue=queue),  # ✅ 添加 OX.FUN
            # phemex.Connector(exchange="phemex", queue=queue),  # ✅ 添加 Phemex

            bitfinex.Connector(exchange="bitfinex", queue=queue),  #  添加 Bitfinex  fail slow



            # 你可以继续添加 binance、bybit 等其他交易所
        ]

    async def run_all(self):
        tasks = [asyncio.create_task(conn.run()) for conn in self.connectors]
        await asyncio.gather(*tasks)
