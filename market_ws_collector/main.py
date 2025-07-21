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


import asyncio
from connectors import ascendex

async def main():
    # 可传入 symbols 或使用默认 config.py 中配置
    connector = ascendex.Connector()
    await connector.run()

if __name__ == "__main__":
    asyncio.run(main())
