from connectors import (
    ascendex, krakenfutures, bingx, binance,
    bitget, bitmart, bitmex, bitrue,
    blofin, bybit, cryptocom, digifinex,
    gateio, huobi, lbank, 
    mexc, okx, oxfun, phemex,

# bitfinex,coinbase  # 这些交易所暂时不添加

)

from config import DEFAULT_SYMBOLS
import asyncio

import json
import time
import importlib



class ExchangeManager:
    def __init__(self, queue):
        self.queue = queue
        self.connectors = [
            # ascendex.Connector(exchange="ascendex", queue=queue),
            # binance.Connector(exchange="binance", queue=queue),  # ✅ 添加 Binance
            # bingx.Connector(exchange="bingx", queue=queue),  # ✅ 添加 BingX
            # bitget.Connector(exchange="bitget", queue=queue),  # ✅ 添加 Bitget
            # bitmart.Connector(exchange="bitmart", queue=queue),  # ✅ 添加 BitMart
            # bitmex.Connector(exchange="bitmex", queue=queue),  # ✅ 添加 BitMEX
            # bitrue.Connector(exchange="bitrue", queue=queue),  # ✅ 添加 Bitrue 1s  @
            # blofin.Connector(exchange="blofin", queue=queue),  # ✅ 添加 BloFin @
            # bybit.Connector(exchange="bybit", queue=queue),  # ✅ 添加 Bybit
            # cryptocom.Connector(exchange="cryptocom", queue=queue),  # ✅ 添加 Crypto. @
            # digifinex.Connector(exchange="digifinex", queue=queue),  # ✅ 添加 Digifinex
            # gateio.Connector(exchange="gateio", queue=queue),  # ✅ 添加 Gate.io
            # huobi.Connector(exchange="huobi", queue=queue),  # ✅ 添加 Huobi
            # krakenfutures.Connector(exchange="krakenfutures", queue=queue),
            # lbank.Connector(exchange="lbank", queue=queue),  # ✅ 添加 LBank @  LBank 异常: sent 1011 (internal error) keepalive ping timeout; no close frame received
            # mexc.Connector(exchange="mexc", queue=queue),  # ✅ 添加 MEXC slow update/1 second
            # okx.Connector(exchange="okx", queue=queue),  # ✅ 添加 OKX
            # oxfun.Connector(exchange="oxfun", queue=queue),  # ✅ 添加 OX.FUN
            # phemex.Connector(exchange="phemex", queue=queue),  # ✅ 添加 Phemex

            ##### debug
            # bitrue.Connector(exchange="bitrue",symbols=["ANIME-USDT"],  queue=queue),  # 
            # mexc.Connector(exchange="mexc", queue=queue),  # ✅ 添加 MEXC slow update/1 second
            # bitfinex.Connector(exchange="bitfinex", queue=queue),  #  invalid exchange





            ####### invalid exchanges
            # bitfinex.Connector(exchange="bitfinex", queue=queue),  #  添加 Bitfinex  fail slow
            # coinbase.Connector(exchange="coinbase", queue=queue),  # ✅ 添加 Coinbase spot only 

            # 你可以继续添加 binance、bybit 等其他交易所
        ]

        self.load_connectors() # 加载所有交易所连接器

    def load_connectors(self):
    
        with open("../selector/top100_exchange_symbols.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        print(data.keys())  # 显示所有的交易所名


        skip_exchanges = ["bitrue"]
        

        for exchange in data.keys():
            if exchange in skip_exchanges:
                continue
            if exchange not in globals():
                print(f"⚠️ exchange 模块未导入: {exchange}")
                continue

            try:
                connector = globals()[exchange].Connector(
                    exchange=exchange,
                    symbols=data[exchange],
                    queue=self.queue
                )
                self.connectors.append(connector)
                print(f"✅ 成功添加交易所: {exchange}（symbol 数量: {len(data[exchange])}）")
            except Exception as e:
                print(f"❌ 构建 {exchange}.Connector 时出错: {e}")
            

    async def run_all(self):
        tasks = [asyncio.create_task(conn.run()) for conn in self.connectors]
        await asyncio.gather(*tasks)
