import websocket
import json

WS_URL = "wss://www.lbkex.net/ws/V2/"
SYMBOLS = ["btc_usdt", "eth_usdt", "sol_usdt", "ltc_usdt", "xrp_usdt"]

def on_open(ws):
    print("✅ 已连接 LBank WebSocket")

    for symbol in SYMBOLS:
        sub_msg = {
            "action": "subscribe",
            "subscribe": "tick",  # 订阅 ticker 数据
            "pair": symbol        # 交易对格式为 xxx_yyy
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅 tick:{symbol}")

def on_message(ws, message):
    data = json.loads(message)

    # 📊 示例字段说明（tick 数据结构）：
    # 'tick': {
    #     'latest'   : 最新成交价
    #     'high'     : 24h最高价
    #     'low'      : 24h最低价
    #     'vol'      : 24h成交量
    #     'turnover' : 24h成交额
    #     'dir'      : 最新成交方向（buy/sell）
    #     'change'   : 24h涨跌幅
    #     'to_usd'   : 最新价格折算为 USD
    #     'to_cny'   : 最新价格折算为 CNY
    #     'usd'      : 当前币种价格（USD）
    #     'cny'      : 当前币种价格（CNY）
    # }
    # ⚠️ 注意：tick 数据中不直接包含买一/卖一价格，需订阅 depth 或 bookTicker

    if data.get("type") == "tick" and "tick" in data:
        symbol = data.get("pair", "unknown")
        tick = data["tick"]
        print(f"📊 {symbol} | 最新价: {tick['latest']} | 涨跌: {tick['change']}% | 成交量: {tick['vol']}")

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
