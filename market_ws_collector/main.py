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
